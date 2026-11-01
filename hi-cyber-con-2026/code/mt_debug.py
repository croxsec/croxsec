#!/usr/bin/env python3
# Minimal MT chain debug for Rocinate synth
import sys, random
sys.path.insert(0, '/tmp/ctfA/rocinate')
from rlib import untemper, temper, words_of, solve_block0
from Crypto.Util.number import getPrime

random.seed(31337)
p, q = getPrime(1024), getPrime(1024)
N = p*q
while N.bit_length() != 2047:
    p, q = getPrime(1024), getPrime(1024)
    N = p*q
r = random.randint(1, N)
e = random.randint(1, N)
st = random.getstate()
ST = st[1][:-1]  # 624 words
idx = st[1][-1]
print("index before 'a':", idx)
a = random.randint(1, N)

# expected: untempered stream X[idx + t] for the 'a' draw
K_words = words_of(a - 1)  # list of (untempered_word, mask)
ok = 0
for t in range(64):
    exp = ST[(idx + t) % 624] if (idx + t) < 624 else None
    if exp is None:
        print(f"t={t}: beyond current block (need twist)")
        continue
    got, m = K_words[t]
    if (got & m) == (exp & m):
        ok += 1
    else:
        print(f"t={t}: MISMATCH got={got:08x} exp={exp:08x} mask={m:08x}")
print(f"word match: {ok}/64")

# So absolute position of 'a' first word = idx (mod 624) -> true W = idx
W = idx
# Build true b1 = S1 = twist(S0) where S0 = ST (current block)
MAG = 0x9908b0df
def twist_blk(cur):
    out = [0]*624
    for i in range(624):
        y = (cur[i] & 0x80000000) | (cur[(i+1)%624] & 0x7fffffff)
        out[i] = cur[(i+397)%624] ^ (y >> 1) ^ (MAG if (y & 1) else 0)
    return out
S1 = twist_blk(ST)

# solve_block0 should recover ST given b1 and known tail
K = []
for v in [a-1] + [c-1 for c in [random.randint(1,N) for _ in range(3)]]:
    K.extend(words_of(v))
res = solve_block0(K, W)
if res is None:
    print("solve_block0 returned None")
else:
    b0, b1 = res
    bad = 0
    for i in range(624):
        w, m = b0[i]
        if (w & m) != (ST[i] & m):
            bad += 1
            if bad < 5:
                print(f"b0[{i}]: got={w:08x} mask={m:08x} exp={ST[i]:08x}")
    print(f"b0 mismatch vs true ST: {bad}/624")
    # check b1 used matches true S1
    bad1 = sum(1 for i in range(624) if (b1[i][0] & b1[i][1]) != (S1[i] & b1[i][1]))
    print(f"b1 mismatch vs true S1: {bad1}/624")

# direct: draw a from b0 via temper
v0 = 0; v1 = 0
for k in range(64):
    w, m = b0[W + k]
    base = w & m
    w0 = temper(base)
    w1 = temper(base | (~m & 0xffffffff))
    v0 |= w0 << (32*k); v1 |= w1 << (32*k)
v0 >>= 1; v1 >>= 1
print("a-1 in [v0,v1] range?", (a-1) == v0 or (a-1) == v1, " mask bits:", bin(v0^v1).count('1'))
print("v0 == a-1?", v0 == a-1)
