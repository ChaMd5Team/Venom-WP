### 狂飙

出题人  w4n_y1ng

#### **考察点**

```Plain%20Text
编程能力

和数论思维
```

#### 题目代码

```python
import os
from secrets import flag
from Crypto.Util.number import *
from Crypto.Cipher import AES
m = 88007513702424243702066490849596817304827839547007641526433597788800212065249
key = os.urandom(24)
key = bytes_to_long(key)
n=m % key
flag += (16 - len(flag) % 16) * b'\x00'
iv = os.urandom(16)
aes = AES.new(key,AES.MODE_CBC,iv)
enc_flag = aes.encrypt(flag)

print(n)
print(enc_flag)
print(iv)


#103560843006078708944833658339172896192389513625588
#b'\xfc\x87\xcb\x8e\x9d\x1a\x17\x86\xd9~\x16)\xbfU\x98D\xfe\x8f\xde\x9c\xb0\xd1\x9e\xe7\xa7\xefiY\x95C\x14\x13C@j1\x9d\x08\xd9\xe7W>F2\x96cm\xeb'
#b'UN\x1d\xe2r<\x1db\x00\xdb\x9a\x84\x1e\x82\xf0\x86'
```

#### **题解**

我们已知

```
m % key =n
```

化简

```
m=k*key+n
k*key=m-n
```

通过sage `divisors` 得到除数列表 自动排列组合了

```
m-n分解出来之后  得到的是 k*keyRANHO
```

根据`key`的长度为`192bit`进行爆破

爆破长度后通过筛选`flag头`得到`flag`

#### **解题代码**

#sage

```
from Crypto.Cipher import AES
from Crypto.Util.number import *
n=103560843006078708944833658339172896192389513625588
m=88007513702424243702066490849596817304827839547007641526433597788800212065249
key=m-n
#88007513702424243702066490746035974298749130602173983187260701596410698439661
enc=b'\xfc\x87\xcb\x8e\x9d\x1a\x17\x86\xd9~\x16)\xbfU\x98D\xfe\x8f\xde\x9c\xb0\xd1\x9e\xe7\xa7\xefiY\x95C\x14\x13C@j1\x9d\x08\xd9\xe7W>F2\x96cm\xeb'
iv=b'UN\x1d\xe2r<\x1db\x00\xdb\x9a\x84\x1e\x82\xf0\x86'
for i in key.divisors():
    i=long_to_bytes(i,24)
    aes=AES.new(i,AES.MODE_CBC,iv)
    flag=aes.decrypt(enc)
    if b'flag{' in flag:
        print(flag)
```

得到

```Plain%20Text
b'flag{cf735a4d-f9d9-5110-8a73-5017fc39b1b0}\x00\x00\x00\x00\x00\x00'
```



