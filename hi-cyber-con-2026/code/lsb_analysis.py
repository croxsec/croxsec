#!/usr/bin/env python3
"""LSB bitplane analysis for unremarkable/chall.png — no zsteg available."""
import numpy as np
from PIL import Image
import sys, os

p = '/tmp/ctf_e2/unremarkable/chall.png'
im = Image.open(p)
print('mode', im.mode, 'size', im.size)
a = np.array(im)
h, w, c = a.shape
print('shape', a.shape, 'dtype', a.dtype)

magics = [b'hiCTF', b'\x89PNG', b'PK\x03\x04', b'\xff\xd8\xff', b'GIF8', b'%PDF', b'RIFF', b'IHDR', b'IDAT', b'IEND', b'http', b'flag', b'FLAG']

def scan(bits, name):
    # bits: flat uint8 array of 0/1
    nbytes = len(bits) // 8
    b = bits[:nbytes*8].reshape(-1, 8)
    by = np.packbits(b, axis=1).reshape(-1)
    data = by.tobytes()
    for m in magics:
        i = data.find(m)
        if i >= 0:
            print(f'[{name}] FOUND {m} at byte {i}: {data[max(0,i-8):i+64]!r}')
    return data

# 1) Each channel LSB separately, MSB-first bit order
for ci, cn in enumerate('RGB'):
    plane = (a[:,:,ci] & 1).reshape(-1)
    scan(plane, f'{cn}-lsb-msb')

# 2) All channels interleaved RGB
inter = (a & 1).reshape(-1)
scan(inter, 'RGB-interleave-msb')

# 3) Bit order reversed (LSB-first)
for ci, cn in enumerate('RGB'):
    plane = (a[:,:,ci] & 1).reshape(-1)
    nbytes = len(plane)//8
    b = plane[:nbytes*8].reshape(-1, 8)[:, ::-1]
    by = np.packbits(b, axis=1).reshape(-1)
    data = by.tobytes()
    for m in magics:
        i = data.find(m)
        if i >= 0:
            print(f'[{cn}-lsb-lsbfirst] FOUND {m} at byte {i}: {data[max(0,i-8):i+64]!r}')

# 4) Higher bit planes (bits 1-3) in case of "amplified" stego
for bit in (1, 2):
    for ci, cn in enumerate('RGB'):
        plane = ((a[:,:,ci] >> bit) & 1).reshape(-1)
        scan(plane, f'{cn}-bit{bit}-msb')

print('--- bitplane visual stats ---')
# If a bitplane encodes data, its local variance differs from noise. Compute per-plane entropy quickly.
for bit in range(4):
    for ci, cn in enumerate('RGB'):
        plane = ((a[:,:,ci] >> bit) & 1).astype(np.uint8)
        # fraction of 1s
        f = plane.mean()
        # neighbor correlation
        p1 = plane[:-1,:]; p2 = plane[1:,:]
        corr = np.abs(p1.astype(int)-p2.astype(int)).mean()
        print(f'{cn} bit{bit}: frac1={f:.4f} rowdiff={corr:.4f}')

# 5) Save bitplane images for visual check (LSB planes)
out = np.zeros((h, w, 3), dtype=np.uint8)
for ci in range(3):
    out[:,:,ci] = (a[:,:,ci] & 1) * 255
Image.fromarray(out).save('/tmp/ctf_e2/lsb_planes.png')
print('saved /tmp/ctf_e2/lsb_planes.png')
print('DONE')
