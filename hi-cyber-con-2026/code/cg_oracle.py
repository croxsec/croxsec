#!/usr/bin/env python3
# ChronoGrind AEAD oracle: small-anchor candidates via C chain, then ChaCha20-Poly1305
import subprocess, hashlib, itertools, sys
from Crypto.Cipher import ChaCha20_Poly1305

data = open('/tmp/ctf_D3c/chronogrind/chronogrind/state.dat','rb').read()
dec = bytes([b ^ 0x6c for b in data[4:]])
R1 = dec[0x18:0x118]; R2 = dec[0x120:0x220]; R3 = dec[0x269:0x36a]
enc = open('/tmp/ctf_D3c/chronogrind/chronogrind/flag.enc','rb').read()
print("flag.enc:", len(enc), enc.hex())

TR = [42794175, 1175340878, 2673290950, 9000000000]
anchors = [241, 2**41, 42794175, 1175340878, 2673290950]
seed_bufs = {'R1': R1, 'R2': R2, 'R3': R3}
seeds = {}
for k, b in seed_bufs.items():
    for L in (256, 128, 64, 41, 32):
        if L > len(b): continue
        for off in (0, 4, 8):
            if off + L > len(b): continue
            seeds[f"{k}[{off}:{off+L}]BE"] = int.from_bytes(b[off:off+L], 'big')
            seeds[f"{k}[{off}:{off+L}]LE"] = int.from_bytes(b[off:off+L], 'little')

# Build chain jobs: (M, S mod M, CYCLES)
jobs = []
meta = []
for M in anchors:
    for sname, s in seeds.items():
        for c in TR:
            jobs.append((M, s % M, c))
            meta.append((M, sname, c))
print("jobs:", len(jobs))

proc = subprocess.Popen(['/tmp/ctf_D3c/cg_chain64'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
inp = "".join(f"{M} {S} {C}\n" for M, S, C in jobs)
out, _ = proc.communicate(inp)
Vf = [int(x) for x in out.strip().split('\n')]
print("chain results:", len(Vf))

def key_candidates(v):
    ks = set()
    b32 = v.to_bytes(32, 'big', signed=False) if v < 2**256 else None
    if b32: ks.add(('V32BE', b32))
    b8 = v.to_bytes(8, 'big')
    ks.add(('V8BE+pad', b'\x00'*24 + b8))
    ks.add(('Vhex', hashlib.sha256(format(v, 'x').encode()).digest()))
    ks.add(('Vdec', hashlib.sha256(str(v).encode()).digest()))
    if b32: ks.add(('rawV32', b32))
    return ks

# ChaCha layouts: (nonce_slice, tag_slice, ct_slice)
LAYOUTS = [
    ('n5t17c33', slice(5,17), slice(17,33), slice(33,None)),
    ('n5c17tlast', slice(5,17), slice(len(enc)-16,None), slice(17,len(enc)-16)),
]
AADS = [('none', b''), ('hdr5', enc[0:5]), ('allbuttag', None)]

hits = 0
for (M, sname, c), v in zip(meta, Vf):
    for kname, key in key_candidates(v):
        for lname, nsl, tsl, csl in LAYOUTS:
            nonce = enc[nsl]; tag = enc[tsl]; ct = enc[csl]
            for aname, aad in AADS:
                if aad is None:
                    aad = enc[:tsl.start] + enc[tsl.stop:]
                try:
                    d = ChaCha20_Poly1305.new(key=key, nonce=nonce)
                    d.update(aad)
                    pt = d.decrypt_and_verify(ct, tag)
                    print(f"*** HIT M={M} seed={sname} cyc={c} key={kname} lay={lname} aad={aname}: {pt}")
                    hits += 1
                except Exception:
                    pass
                # also try without aad update
                try:
                    d = ChaCha20_Poly1305.new(key=key, nonce=nonce)
                    pt = d.decrypt_and_verify(ct, tag)
                    print(f"*** HIT(noAADupd) M={M} seed={sname} cyc={c} key={kname} lay={lname}: {pt}")
                    hits += 1
                except Exception:
                    pass
print("hits:", hits)
