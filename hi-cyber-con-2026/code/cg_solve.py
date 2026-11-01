#!/usr/bin/env python3
# ChronoGrind solve driver: run candidate KDF params, try ChaCha20-Poly1305 layouts, verify tag.
import hashlib, subprocess, itertools, sys
from Crypto.Cipher import ChaCha20_Poly1305

data = open('/tmp/ctf_D3c/chronogrind/chronogrind/state.dat','rb').read()
enc = open('/tmp/ctf_D3c/chronogrind/chronogrind/flag.enc','rb').read()
R = {'R1': data[0x1c:0x120], 'R2': data[0x124:0x269], 'R3': data[0x26d:0x372]}

def blocks(rn, count=3):
    Rr = R[rn]
    out = []
    for i in range(count):
        b = Rr[i*32:(i+1)*32]
        if len(b) == 32:
            out.append((f"{rn}b{i}BE", b.hex(), int.from_bytes(b,'big')))
            out.append((f"{rn}b{i}LE", b[::-1].hex(), int.from_bytes(b,'little')))
    return out

CHAIN = '/tmp/ctf_D3c/chain'

def run_chain(seed_hex, anchor_hex, cycles, domod=True, order='hash_then_mod', kform='V'):
    """Returns candidate K bytes (32). order: hash_then_mod | mod_then_hash. kform: V | hashV"""
    v = bytes.fromhex(seed_hex)
    a = int.from_bytes(bytes.fromhex(anchor_hex),'big') if domod else None
    # implement loop in python only for small cycles; else call C
    if cycles <= 2_000_000:
        for _ in range(cycles):
            if order == 'mod_then_hash' and a is not None:
                vi = int.from_bytes(v,'big')
                if vi >= a: v = (vi % a).to_bytes(32,'big')
            v = hashlib.sha256(v).digest()
            if order == 'hash_then_mod' and a is not None:
                vi = int.from_bytes(v,'big')
                if vi >= a: v = (vi % a).to_bytes(32,'big')
    else:
        # C chain implements hash_then_mod. For other orders, skip (return None)
        if order != 'hash_then_mod': return None
        arg2 = anchor_hex if domod else '-'
        out = subprocess.run([CHAIN, seed_hex, arg2, str(cycles)], capture_output=True, text=True)
        v = bytes.fromhex(out.stdout.strip())
    if kform == 'hashV':
        v = hashlib.sha256(v).digest()
    return v

def layouts(enc):
    e = enc
    outs = []
    outs.append(('V1_nonce_tag_ct', e[5:17], e[17:33], e[33:]))
    outs.append(('V4_nonce_tag_ct', e[8:20], e[20:36], e[36:]))
    outs.append(('V1_nonce_ct_tag', e[5:17], e[52:68], e[17:52]))
    outs.append(('V4_nonce_ct_tag', e[8:20], e[52:68], e[20:52]))
    outs.append(('V0_nonce_tag_ct', e[4:16], e[16:32], e[32:]))
    return outs

def try_decrypt(key, name):
    for lname, nonce, tag, ct in layouts(enc):
        for n in (nonce, nonce[::-1]):
            for nn in (n, n + b'\x00'*4 if len(n)==8 else n):
                cipher = ChaCha20_Poly1305.new(key=key, nonce=nn)
                try:
                    pt = cipher.decrypt_and_verify(ct, tag)
                    print(f"*** SUCCESS {name} layout={lname} ***")
                    print("FLAG:", pt)
                    return pt
                except Exception:
                    pass
    return None

# digit scan
import re
digit_runs = [(hex(m.start()), m.group()) for m in re.finditer(rb'[0-9]{4,}', data)]
print("digit runs:", digit_runs[:20])

# candidate params
anchors = blocks('R1',2) + blocks('R2',2) + blocks('R3',2)
seeds   = blocks('R1',2) + blocks('R2',2) + blocks('R3',2)
trailer_vals = []
for rn, off in (('R1',252),('R2',252)):
    b = R[rn][off:off+4]
    trailer_vals.append(int.from_bytes(b,'little'))
    trailer_vals.append(int.from_bytes(b,'big'))
b64 = R['R1'][64:68]
trailer_vals += [int.from_bytes(b64,'little'), int.from_bytes(b64,'big')]
cycles_cands = sorted(set([1,2,3,10,100,1000,10000,100000,1000000] + [v for v in trailer_vals if 1 <= v <= 10**12]))
print("cycles cands:", cycles_cands)

def main():
    tried = 0
    for (an, ah, _), (sn, sh, _) in itertools.product(anchors, seeds):
        for cyc in cycles_cands:
            for domod in (True, False):
                for order in ('hash_then_mod','mod_then_hash'):
                    if cyc > 2_000_000 and order != 'hash_then_mod':
                        continue
                    for kform in ('V','hashV'):
                        if cyc > 2_000_000 and kform != 'V':
                            continue
                        tried += 1
                        key = run_chain(sh, ah, cyc, domod, order, kform)
                        if key is None: continue
                        tag_ok = try_decrypt(key, f"a={an} s={sn} c={cyc} mod={domod} {order} k={kform}")
                        if tag_ok:
                            print("TRIED:", tried)
                            return
                        if tried % 200 == 0:
                            print("tried", tried, "last:", an, sn, cyc, domod, order, kform, flush=True)
    print("TRIED:", tried, "no luck")

main()
