#!/usr/bin/env python3
"""Optimized solver for Inner Engine VM."""

count = 0
solutions = []

for i9 in range(256):
    i10 = (0xa4 - i9) & 0xFF
    i11 = (0xbe - i10) & 0xFF
    for i12 in range(256):
        i13 = (0x9f - i12) & 0xFF
        i14 = (0x99 - i13) & 0xFF
        i15 = (0x94 - i14) & 0xFF
        for i16 in range(256):
            i17 = (0x94 - i16) & 0xFF
            i18 = (0x9a - i17) & 0xFF
            i19 = (0x9b - i18) & 0xFF
            i20 = (0x99 - i19) & 0xFF
            i21 = (0x9a - i20) & 0xFF
            i22 = (0x96 - i21) & 0xFF
            
            # Early prune: C19
            if i10 ^ i18 != 0x36: continue
            # Early prune: C16
            if (i11 * i19) & 0xFF != 0x53: continue
            
            # C18: i4 = 0x41 ^ i12 ^ i20
            i4 = 0x41 ^ i12 ^ i20
            
            # C14: solve i3
            for i3 in range(256):
                if (i3 * i15) & 0xFF != 0x43: continue
                
                # C23: i6 = 0x77 ^ i3 ^ i11 ^ i14 ^ i19 ^ i22
                i6 = 0x77 ^ i3 ^ i11 ^ i14 ^ i19 ^ i22
                
                # C1: i5 = 0x54 ^ i6
                i5 = 0x54 ^ i6
                
                # C21: i0 = 0x56 ^ i5 ^ i9 ^ i13 ^ i17 ^ i21
                i0 = 0x56 ^ i5 ^ i9 ^ i13 ^ i17 ^ i21
                
                # C13: i23 = (0xb1 - i0) & 0xFF
                i23 = (0xb1 - i0) & 0xFF
                
                # C17: i8 = 0x21 ^ i0 ^ i16
                i8 = 0x21 ^ i0 ^ i16
                
                # C20: check
                if (i0 + i4 + i8 + i12 + i16 + i20) & 0xFF != 0x9a: continue
                
                # C22: i7 = (0x01 - i10 - i15 - i18 - i23) & 0xFF
                i7 = (0x01 - i10 - i15 - i18 - i23) & 0xFF
                
                # C15: check
                if (i7 * i21) & 0xFF != 0xec: continue
                
                count += 1
                inp = [0]*24
                inp[0]=i0; inp[3]=i3; inp[4]=i4; inp[5]=i5; inp[6]=i6
                inp[7]=i7; inp[8]=i8; inp[9]=i9; inp[10]=i10; inp[11]=i11
                inp[12]=i12; inp[13]=i13; inp[14]=i14; inp[15]=i15
                inp[16]=i16; inp[17]=i17; inp[18]=i18; inp[19]=i19
                inp[20]=i20; inp[21]=i21; inp[22]=i22; inp[23]=i23
                
                printable = sum(1 for b in inp if 32 <= b < 127)
                key = bytes(inp)
                solutions.append(key)
                print(f"Sol #{count}: {key.hex()} printable={printable}/24")
                print(f"  ascii: {''.join(chr(b) if 32<=b<127 else '.' for b in inp)}")

print(f"\nTotal solutions: {count}")
# Show ones with most printable chars
if solutions:
    best = max(solutions, key=lambda k: sum(1 for b in k if 32 <= b < 127))
    bp = sum(1 for b in best if 32 <= b < 127)
    print(f"Best printable: {best.hex()} ({bp}/24 printable)")
    print(f"  ascii: {''.join(chr(b) if 32<=b<127 else '.' for b in best)}")
