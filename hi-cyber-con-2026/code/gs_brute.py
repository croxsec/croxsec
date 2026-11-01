#!/usr/bin/env python3
import sys, re
sys.path.insert(0, '/tmp')
from gs_access import access, keystream16, KEY
from gs_client import GSP

g = GSP()
nonce_hex = [re.match(r'NONCE ([0-9a-f]+)', l).group(1) for l in g.greeting if l.startswith('NONCE')][0]
nonce8 = bytes.fromhex(nonce_hex)
ks = keystream16()
print("NONCE:", nonce_hex)

pads = {
    'n8+0': nonce8 + b'\x00'*8,
    '0+n8': b'\x00'*8 + nonce8,
    'n8+n8': nonce8*2,
    'ascii16': nonce_hex.encode(),
    'n8+ks8': nonce8 + ks[:8],
    'n8+KEY': nonce8 + KEY,
    'KEY+n8': KEY + nonce8,
    'ks8+n8': ks[:8] + nonce8,
}
keys = {
    'KEY': KEY,
    'ks8': ks[:8],
    'ks8b': ks[8:],
    'zeros': b'\x00'*8,
}
found = False
for pk, n16 in pads.items():
    for kk, k8 in keys.items():
        resp = access(n16, k8)
        r = g.cmd('AUTH ' + resp.hex())
        ok = any('access=engineer' in x for x in r)
        print(f"{pk:8s} x {kk:6s} -> {r[0] if r else '??'}")
        if ok:
            print("!!! WIN:", pk, kk)
            found = True
            for c in ['PROG LIST', 'BACKUP STATUS', 'WDOG STATUS', 'STATUS']:
                print(c, '->', g.cmd(c))
            break
    if found: break
if not found:
    print("ALL FAILED")
