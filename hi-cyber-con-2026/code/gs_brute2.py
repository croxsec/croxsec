#!/usr/bin/env python3
import sys, re, itertools
sys.path.insert(0, '/tmp')
from gs_access import access, keystream16, KEY
from gs_client import GSP

g = GSP()
nonce_hex = [re.match(r'NONCE ([0-9a-f]+)', l).group(1) for l in g.greeting if l.startswith('NONCE')][0]
n8 = bytes.fromhex(nonce_hex)
n16 = n8 + n8
ks = keystream16()
Z = b'\x00'*8
CONST_4011a8 = bytes.fromhex('01000200') + b'\x00'*12  # data const

# (input16, key8) candidate pairs
cands = []
# classic paddings
for padname, pad in [('Z',Z),('n8',n8),('KEY',KEY),('ks0',ks[:8]),('ks1',ks[8:]),
                     ('4011a8',CONST_4011a8[:8]),('GSC7',b'GSC-7\x00\x01\x23')]:
    cands.append((f'in=n8+{padname}', n8+pad, KEY))
    cands.append((f'in={padname}+n8', pad+n8, KEY))
# nonce as KEY
for inname, inp in [('ks16',ks),('n16',n16),('Z16',Z*2),('KEY+KEY',KEY+KEY),
                    ('ks^n16', bytes(a^b for a,b in zip(ks,n16))),
                    ('ascii16', nonce_hex.encode())]:
    cands.append((f'key=nonce,in={inname}', inp, n8))
# xor pads
cands.append(('in=n8+(n8^ks0)', n8 + bytes(a^b for a,b in zip(n8,ks[:8])), KEY))
cands.append(('in=ks0+n8,key=n8', ks[:8]+n8, n8))

def hexvariants(resp):
    h = resp.hex()
    return {'lower': h, 'upper': h.upper(), 'rev': resp[::-1].hex()}

found = False
for name, inp, k in cands:
    resp = access(inp, k)
    for hv, hs in hexvariants(resp).items():
        r = g.cmd('AUTH ' + hs)
        line = r[-1] if r else '??'
        status = 'WIN!!!' if 'access=engineer' in line else line
        print(f"{name:22s} hex={hv:5s} -> {status}")
        if 'access=engineer' in line:
            found = True
            for c in ['PROG LIST', 'BACKUP STATUS', 'WDOG STATUS', 'STATUS']:
                print(c, '->', g.cmd(c))
            break
    if found: break
if not found:
    print("=== ALL FAILED ===")
