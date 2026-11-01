#!/usr/bin/env python3
tokens = "53 74 u3 17 35 x3 x2 76 24 33 93 u3 16 v4 36 v4 93 32 64 22 z3 x2 42 w4 54 05 v2 v5 63 v6 26 23 26 33 86 u3 33 x3 74 x2 06 54 62 x5 22 74 44 04 45 v5 93 x2".split()

ROWS_VAR = [
    ['u','v','w','x','z'] + [str(d) for d in range(10)],
    [str(d) for d in range(10)] + ['u','v','w','x','z'],
]
COLS_VAR = [
    ['2','3','4','5','6','7'],
    ['0','1','2','3','4','5'],
    ['1','2','3','4','5','6'],
]

def keyed_alpha(key, base):
    seen = set(); out = []
    for ch in key:
        if ch not in seen:
            seen.add(ch); out.append(ch)
    for ch in base:
        if ch not in seen:
            seen.add(ch); out.append(ch)
    return out

BASE = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}_!@#$%^&*()-+=[]{};:,.<>?/|\"\'\\ '
KEYS = ['', 'saad', 'harun', 'noon', 'saadharun', 'harunsaad', 'saadnoon', 'harunnoon', 'noonsaadharun']

def decode(alpha, rows, cols, fill):
    # fill grid
    grid = {}
    idx = 0
    if fill == 'row':
        for r in rows:
            for c in cols:
                if idx < len(alpha):
                    grid[(r,c)] = alpha[idx]
                idx += 1
    else:
        for c in cols:
            for r in rows:
                if idx < len(alpha):
                    grid[(r,c)] = alpha[idx]
                idx += 1
    out = []
    for t in tokens:
        r, c = t[0], t[1]
        out.append(grid.get((r,c), '?'))
    return ''.join(out)

found = False
for rows in ROWS_VAR:
    for cols in COLS_VAR:
        for key in KEYS:
            alpha = keyed_alpha(key, BASE)
            if len(alpha) < 90: continue
            for fill in ('row','col'):
                txt = decode(alpha, rows, cols, fill)
                score = sum(txt.count(w) for w in ('hiCTF','flag','CTF','the','and'))
                if score > 0 or 'hiCTF' in txt:
                    print(f"*** rows={rows[:5]}.. cols={cols} key='{key}' fill={fill}: {txt}")
                    found = True
                elif key in ('saadharun','') and fill == 'row':
                    print(f"    rows={rows[:2]} cols={cols[0]}.. key='{key}' fill={fill}: {txt[:70]}")
if not found:
    print("no hits with basic keys")
