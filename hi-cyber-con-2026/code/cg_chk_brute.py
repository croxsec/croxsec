#!/usr/bin/env python3
# Brute-force the CHK = SHA256("anchor:seed:cycles") parse of state.dat
import hashlib, itertools, struct

data = open('/tmp/ctf_D3c/chronogrind/chronogrind/state.dat','rb').read()
dec = bytes([b ^ 0x6c for b in data[4:]])

R1 = dec[0x18:0x118]      # 256B
R2 = dec[0x120:0x220]     # 256B
R3 = dec[0x269:0x36a]     # 257B
tr1 = struct.unpack('<I', dec[0x118:0x11c])[0]
tr2 = struct.unpack('<I', dec[0x261:0x265])[0]
tr3 = struct.unpack('<I', dec[0x36a:0x36e])[0]
embedded_9e9 = 9000000000  # '9' + 9x'0' in R2

cycles_cands = {tr1, tr2, tr3, embedded_9e9}

# digest search target: anywhere in dec
haystack = dec

def find_digest(d):
    return haystack.find(d)

# value extraction variants: (offset, length, endianness)
def variants(buf, name):
    out = []
    lens = [16, 20, 24, 28, 32, 36, 40, 41, 44, 48, 56, 64, 128, 256]
    for L in lens:
        if L > len(buf): continue
        for o in range(0, len(buf)-L+1, 4):
            for endian in ('big','little'):
                out.append((name, o, L, endian, int.from_bytes(buf[o:o+L], endian)))
    return out

vA = variants(R1, 'R1')
vS = variants(R2, 'R2')
# also consider anchor/seed possibly from R3 or other combos
vA_extra = variants(R3, 'R3')

print(f"R1 variants={len(vA)} R2 variants={len(vS)} cycles={sorted(cycles_cands)}")
print("trailer values:", tr1, tr2, tr3)

best = None
count = 0
tested = set()
def test(a, s, c, tag):
    global count, best
    key = (a, s, c)
    if key in tested: return
    tested.add(key)
    count += 1
    h = hashlib.sha256(f"{a}:{s}:{c}".encode()).digest()
    pos = find_digest(h)
    if pos >= 0:
        print(f"*** MATCH *** {tag} anchor={a} seed={s} cycles={c} digest@{pos:#x}")
        print(f"    flag string: {a}:{s}:{c}")
        best = (a, s, c, pos)

# main sweep: R1 as anchor, R2 as seed, all cycle cands
for (na, oa, la, ea, a) in vA:
    for (ns, os, ls, es, s) in vS:
        for c in cycles_cands:
            test(a, s, c, f"{na}[{oa}:{oa+la} {ea}] {ns}[{os}:{os+ls} {es}] c={c}")

print("main sweep done, tested:", count, "best:", best)

# extra: R3-as-anchor/seed sweeps (smaller)
for (na, oa, la, ea, a) in vA_extra[:200]:
    for (ns, os, ls, es, s) in vS[:200]:
        for c in cycles_cands:
            test(a, s, c, f"X {na}[{oa}:{oa+la}] {ns}[{os}:{os+ls}] c={c}")
print("extra sweep done, total tested:", count, "best:", best)
