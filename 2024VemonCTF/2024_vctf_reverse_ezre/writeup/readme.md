### ezre

#### 题目flag

flag{Simple_rEvErse}

#### 题目考点

换表base64，变异RC4

#### 题目wp

如下exp

``` 
import base64
import string

def rc4_init(s,key,length):
	k = []
	for i in range(128):
		k.append('0')
	for i in range(128):
		s[i] = i
		k[i] = key[i%length]
	j = 0
	for i in range(128):
		j = (j+s[i]+ord(k[i]))%128
		#print j
		tmp = s[i]
		s[i] = s[j]
		s[j] = tmp


def rc4_crypt(s,data,length):
	i = 0
	j = 0
	data1 = ''
	for k in range(length):
		i = (i+1)%128
		j = (j+s[i])%128
		tmp = s[i]
		s[i] = s[j]
		s[j] = tmp
		t = (s[i]+s[j])%128
		data1 += chr(data[k]^s[t])
	return data1


str1 = "3pn1Ek92hmAEg38EXMn99J9YBf8="

string1 = "0123456789XYZabcdefghijklABCDEFGHIJKLMNOPQRSTUVWmnopqrstuvwxyz+/="
string2 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="

data = base64.b64decode(str1.translate(str.maketrans(string1,string2)))
print(data)
key = "Thi5_1S_key?"
s = []
for i in range(128):
	s.append(0)
rc4_init(s,key,len(key))
data1 = rc4_crypt(s,data,len(data))
print(data1)
```

