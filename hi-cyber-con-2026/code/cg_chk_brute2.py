#!/usr/bin/env python3
# CHK brute force v2 (compact): base-241 / dec modes, hex digest search too
import hashlib, struct

data = open('/tmp/ctf_D3c/chronogrind/chronogrind/state.dat','rb').read()
dec = bytes([b ^ 0x6c for b in data[4:]])

R1 = dec[0x18:0x118]
R2 = dec[0x120:0x220]
R3 = dec[0x269:0x36a]
tr = [struct.unpack('<I', dec[0x118:0x11c])[0],
      struct.unpack('<I', dec[0x261:0x265])[0],
      struct.unpack('<I', dec[0x36a:0x36e])[0],
      9000000000]

def b241(n):
    if n == 0: return '0'
    ds = []
    while n:
        ds.append('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'[n % 241])
        n //= 241
    return ''.join(reversed(ds))

bufs = {'R1': R1, 'R2': R2, 'R3': R3}
def gen(buf):
    for L in (256, 128, 64, 41, 32):
        if L > len(buf): continue
        for o in (0, 4, 8, 16):
            if o + L > len(buf): continue
            yield (o, L, 'big', int.from_bytes(buf[o:o+L], 'big'))
            yield (o, L, 'lit', int.from_bytes(buf[o:o+L], 'little'))

V = {k: list(gen(b)) for k, b in bufs.items()}
print({k: len(v) for k, v in V.items()})

hits = []
tested = 0
pairs = [('R1','R2'), ('R2','R1'), ('R1','R3'), ('R3','R1'), ('R2','R3'), ('R3','R2')]
for ka, ks in pairs:
    for (oa, la, ea, a) in V[ka]:
        for (os_, ls, es, s) in V[ks]:
            for c in tr:
                for ma, ms in [('dec','dec'), ('b241','b241'), ('b241','dec'), ('dec','b241')]:
                    sa = str(a) if ma=='dec' else b241(a)
                    ss = str(s) if ms=='dec' else b241(s)
                    st = f"{sa}:{ss}:{c}"
                    h = hashlib.sha256(st.encode()).digest()
                    tested += 1
                    p = dec.find(h)
                    if p >= 0:
                        print(f"HIT bytes {ka}[{oa}:{oa+la} {ea}] {ks}[{os_}:{os_+ls} {es}] c={c} {ma},{ms} @{p:#x}: {st[:120]}")
                        hits.append(st)
                    ph = dec.find(h.hex().encode())
                    if ph >= 0:
                        print(f"HIT hex {ka}[{oa}:{oa+la} {ea}] {ks}[{os_}:{os_+ls} {es}] c={c} {ma},{ms} @{ph:#x}")
                        hits.append(st)
print("tested:", tested, "hits:", len(hits))
