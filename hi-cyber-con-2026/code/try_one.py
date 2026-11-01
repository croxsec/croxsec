#!/usr/bin/env python3
# try_one.py seedhex anchorhex|- cycles kform
import sys, subprocess, hashlib
from Crypto.Cipher import ChaCha20_Poly1305
seed, anchor, cycles, kform = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
out = subprocess.run(['/tmp/ctf_D3c/chain', seed, anchor, cycles], capture_output=True, text=True)
V = bytes.fromhex(out.stdout.strip())
K = hashlib.sha256(V).digest() if kform == 'hashV' else V
enc = open('/tmp/ctf_D3c/chronogrind/chronogrind/flag.enc','rb').read()
e = enc
layouts = [
    ('V1_nt_ct', e[5:17], e[17:33], e[33:]),
    ('V4_nt_ct', e[8:20], e[20:36], e[36:]),
    ('V1_nc_t_t', e[5:17], e[52:68], e[17:52]),
    ('V4_nc_t_t', e[8:20], e[52:68], e[20:52]),
    ('V0_nt_ct', e[4:16], e[16:32], e[32:]),
]
tag_ok = False
for name, nonce, tag, ct in layouts:
    for nn in {nonce, nonce[::-1]}:
        try:
            c = ChaCha20_Poly1305.new(key=K, nonce=nn)
            pt = c.decrypt_and_verify(ct, tag)
            print(f"SUCCESS layout={name} kform={kform} seed={seed[:16]}.. anchor={anchor[:16] if anchor!='-' else '-'} cyc={cycles}")
            print("FLAG:", pt)
            tag_ok = True
        except Exception:
            pass
if not tag_ok:
    print(f"FAIL seed={seed[:16]} anchor={anchor[:16] if anchor!='-' else '-'} cyc={cycles} kform={kform} V={V.hex()[:32]}")
