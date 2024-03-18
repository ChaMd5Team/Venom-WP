def rc4_init(s,key,length):
	k = []
	for i in range(256):
		k.append('0')
	for i in range(256):
		s[i] = i
		k[i] = key[i%length]
	j = 0
	for i in range(256):
		j = (j+s[i]+ord(k[i]))%256
		tmp = s[i]
		s[i] = s[j]
		s[j] = tmp

def rc4_crypt(s,data,length):
	i = 0
	j = 0
	data1 = ''
	for k in range(length):
		i = (i+1)%256
		j = (j+s[i])%256
		tmp = s[i]
		s[i] = s[j]
		s[j] = tmp
		t = (s[i]+s[j])%256
		data1 += chr(((ord(data[k])^s[t])+i)&0xff)
	return data1

def rc4_crypt1(s,data,length):
	i = 0
	j = 0
	data1 = ''
	for k in range(length):
		i = (i+1)%256
		tmp_num = (ord(data[k])-i) & 0xff
		j = (j+s[i])%256
		tmp = s[i]
		s[i] = s[j]
		s[j] = tmp
		t = (s[i]+s[j])%256
		data1 += chr(tmp_num^s[t])
		print hex(tmp_num^s[t])
	return data1

def rc4_crypt2(s,data,length):
	i = 0
	j = 0
	data1 = ''
	for k in range(length):
		i = (i+1)%256
		j = (j+s[i])%256
		tmp = s[i]
		s[i] = s[j]
		s[j] = tmp
		t = (s[i]+s[j])%256
		data1 += chr(ord(data[k])^s[t])
	return data1

d = "711df52879efbcb8964b6056d926ea35"
key = "This_1s_f1lLllag"

s = []
for i in range(256):
	s.append(0)

rc4_init(s, key, len(key))
data1 = rc4_crypt(s, d, len(d))
print data1.encode('hex')

rc4_init(s, key, len(key))
data = rc4_crypt1(s, data1, len(d))
print data