#!/usr/bin/env python3
import json
from eth_utils import keccak
from eth_keys import keys

parsed = json.load(open('/tmp/parsed_txs.json'))
by_n = {p['n']: p for p in parsed}
SELP = {'authorize':'3dff6cbc','redeem':'b38133be','stamp':'7256486f'}

def word(b,i): return b[i*32:(i+1)*32]
def recover(dg, v, r, s):
    try:
        sig = keys.Signature(vrs=(v-27 if v>=27 else v, r, s))
        return keys.PublicKey.recover_from_msg_hash(dg, sig).to_checksum_address()
    except Exception:
        return None

# gather all authorize & redeem args
recs = []
for p in parsed:
    d = p['data']
    if p['created'] or len(d)<10: continue
    pre = d[2:10]
    cd = bytes.fromhex(d[2:])
    contract = bytes.fromhex(p['to'][2:])
    if pre==SELP['authorize']:
        req=word(cd[4:],0); amount=int.from_bytes(word(cd[4:],1),'big'); recip=word(cd[4:],2)
        v=int.from_bytes(word(cd[4:],3),'big'); r=int.from_bytes(word(cd[4:],4),'big'); s=int.from_bytes(word(cd[4:],5),'big')
        recs.append({'ctx':'auth','contract':contract,'w':[req,amount.to_bytes(32,'big'),recip],'v':v,'r':r,'s':s,'n':p['n']})
    elif pre==SELP['redeem']:
        vid=int.from_bytes(word(cd[4:],0),'big'); amount=int.from_bytes(word(cd[4:],1),'big')
        v=int.from_bytes(word(cd[4:],2),'big'); r=int.from_bytes(word(cd[4:],3),'big'); s=int.from_bytes(word(cd[4:],4),'big')
        holder=bytes.fromhex(p['sender'][2:])
        recs.append({'ctx':'redeem','contract':contract,'w':[vid.to_bytes(32,'big'),amount.to_bytes(32,'big'),holder],'v':v,'r':r,'s':s,'n':p['n']})

pad32 = lambda a: b'\x00'*12 + a if len(a)==20 else a

def candidates(rec):
    c = rec['contract']; w0,w1,w2 = rec['w']
    base_variants = {
      'std': pad32(c) + w0 + w1 + w2,
      'no_contract': w0 + w1 + w2,
      '20B_contract': c + w0 + w1 + w2,
      '20B_both': c + w0 + w1 + (w2[12:] if len(w2)==32 else w2),
    }
    out = {}
    for k,v in base_variants.items():
        out['k_'+k] = keccak(v)
        out['sha3_'+k] = __import__('hashlib').sha3_256(v).digest()  # wrong but test
        out['191_'+k] = keccak(b'\x19Ethereum Signed Message:\n32' + keccak(v))
        out['191raw_'+k] = keccak(b'\x19Ethereum Signed Message:\n32' + v)
    # tuple-style: keccak of abi_encode(tuple) is same as concat for static
    return out

# test each candidate formula on ALL recs; score = distinct recovered signers
from collections import Counter
results = {}
for name in candidates(recs[0]).keys():
    signers = set()
    ok = 0
    for rec in recs:
        dg = candidates(rec)[name]
        a = recover(dg, rec['v'], rec['r'], rec['s'])
        if a: signers.add(a); ok+=1
    results[name] = (len(signers), ok, sorted(signers)[:3])

for name,(ns,ok,samp) in sorted(results.items(), key=lambda x:x[1][0]):
    print(f"{name:24s} distinct_signers={ns:3d} recovered={ok}/{len(recs)}  e.g. {samp[:2]}")
