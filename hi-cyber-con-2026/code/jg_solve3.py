#!/usr/bin/env python3
import itertools, re
tokens = "53 74 u3 17 35 x3 x2 76 24 33 93 u3 16 v4 36 v4 93 32 64 22 z3 x2 42 w4 54 05 v2 v5 63 v6 26 23 26 33 86 u3 33 x3 74 x2 06 54 62 x5 22 74 44 04 45 v5 93 x2".split()
stream = ''.join(tokens)
assert len(stream)==104, len(stream)

FIRST = sorted(set(t[0] for t in tokens))
SECOND = sorted(set(t[1] for t in tokens))
print("FIRST set:", FIRST, "SECOND set:", SECOND)

def keyed(key, base):
    seen=set(); out=[]
    for ch in key:
        if ch not in seen: seen.add(ch); out.append(ch)
    for ch in base:
        if ch not in seen: seen.add(ch); out.append(ch)
    return out

PUNCT = list('{}_!?.,;:@#$%^&*()-+=[]<>/|\\ "\'')
def alpha_full(key, base='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    return keyed(key, base) + PUNCT

# English scoring via common words + letter freq
COMMON = ['the','and','this','that','with','flag','is','are','you','saad','harun','noon','meet','note','code','watch','building','hiCTF','CTF','give','man','just']
def score(txt):
    s=0
    if 'hiCTF' in txt: s+=2000
    if txt.startswith('hiCTF'): s+=1000
    for w in COMMON: s += 30*len(re.findall(w, txt))
    for ch in 'etaoinshrdlu ': s+=txt.count(ch)
    for ch in 'qzQZJX': s-=2*txt.count(ch)
    return s

def build_and_decode(cells_fn, alpha, rows, cols, fill):
    g={}; idx=0
    if fill=='row':
        for r in rows:
            for c in cols:
                if idx<len(alpha): g[(r,c)]=alpha[idx]
                idx+=1
    else:
        for c in cols:
            for r in rows:
                if idx<len(alpha): g[(r,c)]=alpha[idx]
                idx+=1
    return ''.join(g.get(cell,'?') for cell in cells_fn())

LROWS = ['u','v','w','x','z']
DROWS = [str(d) for d in range(10)]
COLS6 = [str(d) for d in range(2,8)]
COLS5 = [str(d) for d in range(2,7)]

def cells_direct(swap=False):
    return [( (t[1],t[0]) if swap else (t[0],t[1]) ) for t in tokens]

def cells_fraction_halves(order='rowthencol'):
    # split stream into 2 halves; pair i-th of each
    h = len(stream)//2
    A, B = stream[:h], stream[h:]
    if order=='rowthencol':
        return [(A[i],B[i]) for i in range(h)]
    else:
        return [(B[i],A[i]) for i in range(h)]

KEYS = ['','saad','harun','noon','saadharun','harunsaad','saadnoon','noonharun','saadharunnoon','noonsaadharun','justgivemetheflagman']

results=[]
# A) 15x6 single grid, various
for rows in (LROWS+DROWS, DROWS+LROWS):
    for cols in (COLS6, COLS6[::-1]):
        for key in KEYS:
            alpha=alpha_full(key)
            for fill in ('row','col'):
                for swap in (False,True):
                    cells=cells_direct(swap)
                    txt=build_and_decode(lambda:cells,alpha,rows,cols,fill)
                    sc=score(txt)
                    results.append((sc,f"15x6 rows={rows[:3]} key='{key}' fill={fill} swap={swap}",txt))
# B) fractionation halves
for order in ('rowthencol','colthenrow'):
    cells=cells_fraction_halves(order)
    for rows in (LROWS+DROWS, DROWS+LROWS):
        for cols in (COLS6,):
            for key in ('','saadharun','noon'):
                alpha=alpha_full(key)
                for fill in ('row','col'):
                    txt=build_and_decode(lambda:cells,alpha,rows,cols,fill)
                    sc=score(txt)
                    results.append((sc,f"FRAC-{order} key='{key}' fill={fill}",txt))

results.sort(reverse=True)
for sc,desc,txt in results[:12]:
    print(f"\nsc={sc} {desc}\n  {txt}")
