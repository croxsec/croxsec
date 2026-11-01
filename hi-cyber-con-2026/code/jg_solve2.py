#!/usr/bin/env python3
import itertools, re
tokens = "53 74 u3 17 35 x3 x2 76 24 33 93 u3 16 v4 36 v4 93 32 64 22 z3 x2 42 w4 54 05 v2 v5 63 v6 26 23 26 33 86 u3 33 x3 74 x2 06 54 62 x5 22 74 44 04 45 v5 93 x2".split()

ROWSETS = [
    ['u','v','w','x','z'] + [str(d) for d in range(10)],
    [str(d) for d in range(10)] + ['u','v','w','x','z'],
    [str(d) for d in range(10)] + ['u','v','w','x','z'][::-1],
]
COLSETS = [
    [str(d) for d in range(2,8)],
    [str(d) for d in range(7,1,-1)],
    [str(d) for d in range(6)],
    [str(d) for d in range(5)],
]
PUNCT = '{}_!?.,;:@#$%^&*()-+=[]<>/|\\ "\''
def base_alpha(mode):
    if mode=='azAZ09': return 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    if mode=='AZaz09': return 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    if mode=='az09': return 'abcdefghijklmnopqrstuvwxyz0123456789'
    if mode=='az': return 'abcdefghijklmnopqrstuvwxyz'
    return 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

def keyed(key, base):
    seen=set(); out=[]
    for ch in key:
        if ch not in seen: seen.add(ch); out.append(ch)
    for ch in base:
        if ch not in seen: seen.add(ch); out.append(ch)
    return out

KEYS = ['','saad','harun','noon','saadharun','harunsaad','saadnoon','noonharun','saadharunnoon',
        'noonsaadharun','watching','building','strangecode','justgivemetheflagman','flag','key']

def fill_grid(alpha, rows, cols, fill):
    g={}; idx=0; nr=len(rows); nc=len(cols)
    if fill=='row':
        for i in range(nr):
            for j in range(nc):
                if idx<len(alpha): g[(rows[i],cols[j])]=alpha[idx]
                idx+=1
    else:
        for j in range(nc):
            for i in range(nr):
                if idx<len(alpha): g[(rows[i],cols[j])]=alpha[idx]
                idx+=1
    return g

def score(txt):
    s=0
    if 'hiCTF' in txt: s+=1000
    if txt.startswith('hiCTF{'): s+=500
    for w in ('flag','the','this','is','and','you','ctf'): s+= 20*txt.count(w)
    for ch in 'etaoinshrdlu': s+=txt.count(ch)
    for ch in 'qzJXQZK': s-=txt.count(ch)
    if txt.count('{')!=txt.count('}'): s-=30
    return s

best=[]
for rows in ROWSETS:
    for cols in COLSETS:
        nc=len(cols)
        for mode in ('azAZ09','AZaz09','az09'):
            base=base_alpha(mode)
            for key in KEYS:
                alpha=keyed(key,base)+list(PUNCT)
                for fill in ('row','col'):
                    g=fill_grid(alpha,rows,cols,fill)
                    for swap in (False,True):
                        out=[]
                        for t in tokens:
                            r,c=(t[1],t[0]) if swap else (t[0],t[1])
                            out.append(g.get((r,c),'?'))
                        txt=''.join(out)
                        sc=score(txt)
                        if sc>200:
                            best.append((sc,rows[:3],cols[0],mode,key,fill,swap,txt))
                            print(f"sc={sc} rows={rows[:3]} cols0={cols[0]} mode={mode} key='{key}' fill={fill} swap={swap}")
                            print("   ", txt)
best.sort(reverse=True)
print("=== TOP ===")
for b in best[:5]:
    print(b[0], b[7])
