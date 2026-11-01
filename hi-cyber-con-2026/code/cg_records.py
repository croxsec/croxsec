#!/usr/bin/env python3
# Dump ChronoGrind records in hex for structural analysis
data = open('/tmp/ctf_D3c/chronogrind/chronogrind/state.dat','rb').read()
dec = bytes([b ^ 0x6c for b in data[4:]])

def dump(start, end, label):
    print(f"===== {label} [{start:#x}:{end:#x}] len={end-start} =====")
    for off in range(start, end, 16):
        chunk = dec[off:off+16]
        hx = ' '.join(f'{b:02x}' for b in chunk)
        asc = ''.join(chr(b) if 32<=b<127 else '.' for b in chunk)
        print(f'{off:04x}: {hx:<48} {asc}')

# segments between markers at 0x14, 0x11c, 0x265
dump(0x18, 0x11c, "RECORD 1 (data+trailer)")
dump(0x120, 0x265, "RECORD 2 (data+trailer)")
dump(0x269, 0x36e, "RECORD 3 (data+trailer)")
dump(0x372, 0x535, "RECORD 4 DEVICE NOTES (data+trailer?)")

# trailer candidates for each record (4 bytes before next marker / before notes)
import struct
print()
for name, off in [("R1 trailer", 0x118), ("R2 trailer", 0x261), ("R3 trailer", 0x36a), ("R4 trailer", 0x531)]:
    v = struct.unpack('<I', dec[off:off+4])[0]
    vb = struct.unpack('>I', dec[off:off+4])[0]
    print(f"{name} @{off:#x}: raw={dec[off:off+4].hex()} u32LE={v} ({v/1e9:.4f}e9) u32BE={vb}")
