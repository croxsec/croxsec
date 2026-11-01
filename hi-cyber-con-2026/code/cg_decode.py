#!/usr/bin/env python3
# Decode state.dat: XOR 0x6c after 4-byte magic, digit-encoded fields
data = open('/tmp/ctf_D3c/chronogrind/chronogrind/state.dat','rb').read()
print("total len:", len(data))
dec = bytes([b ^ 0x6c for b in data[4:]])

DIGIT = {0x10+i: ord('0')+i for i in range(10)}
DIGIT[0x1a] = ord(':')
DIGIT[0x1d] = ord('=')
DIGIT[0x07] = ord('(')
DIGIT[0x08] = ord(')')
DIGIT[0x00] = ord('|')

def show_notes_region(start, end):
    out = []
    for i in range(start, end):
        b = dec[i]
        if b in DIGIT:
            out.append(chr(DIGIT[b]))
        elif 32 <= b < 127:
            out.append(chr(b))
        else:
            out.append(f'<{b:02x}>')
    print(''.join(out))

print("=== NOTES REGION 0x36e-0x535 ===")
show_notes_region(0x36e, 0x535)
print()
print("=== HEX DUMP notes 0x36e-0x535 ===")
for off in range(0x36e, 0x535, 16):
    chunk = dec[off:off+16]
    hx = ' '.join(f'{b:02x}' for b in chunk)
    asc = ''.join(chr(b) if 32<=b<127 else '.' for b in chunk)
    print(f'{off:04x}: {hx:<48} {asc}')

# Records analysis: markers at 0x14, 0x11c, 0x265
print()
print("=== RECORD BOUNDARIES ===")
import struct
for off in [0x14, 0x11c, 0x265]:
    print(f"marker @{off:#x}: next4={dec[off+4:off+8].hex()} next16={dec[off+4:off+20].hex()}")
# trailer u32 values before markers
for off in [0x11c, 0x265, 0x535-4]:
    v = struct.unpack('<I', dec[off-4:off])[0]
    print(f"u32LE before {off:#x}: {v} (0x{v:08x}) ~{v/1e9:.3f}e9")
# last 8 bytes of file
print("file tail 16B:", dec[-16:].hex())
print("u32LE at 0x535?:", dec[0x535-8:0x535].hex())
