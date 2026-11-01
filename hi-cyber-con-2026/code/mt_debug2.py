#!/usr/bin/env python3
# Full-chain MT debug: does solve_block0 recover true S0?
import sys, random, math
sys.path.insert(0, '/tmp/ctfA/rocinate')
from rlib import untemper, temper, words_of, solve_block0
from Crypto.Util.number import getPrime, bytes_to_long

random.seed(31337)
p, q = getPrime(1024), getPrime(1024)
N = p*q
while N.bit_length() != 2047:
    p, q = getPrime(1024), getPrime(1024)
    N = p*q
n = 100
flag = b'hiCTF{synth_mt_chain_debug_ok}'
s = bytes_to_long(flag)
def lcg(a,b,x,N): return (a*x+b)%N
r = random.randint(1, N)
e = random.randint(1, N)
# capture state right before 'a' draw
st = random.getstate()
ST = list(st[1][:-1]); idx = st[1][-1]
print("index before 'a':", idx)
a,b = random.randint(1,N), random.randint(1,N)
Rs=[r]
for _ in range(n-1): Rs.append(lcg(a,b,Rs[-1],N))
Cs = [random.randint(1,N) for _ in range(n)]
Zs = [ri*pow(s,ci,N) for ri,ci in zip(Rs,Cs)]

K = []
for v in [a-1, b-1] + [c-1 for c in Cs]:
    K.extend(words_of(v))
print("K len:", len(K), "true W =", idx)

res = solve_block0(K, idx)
print("solve_block0:", "None" if res is None else "ok")
if res:
    b0, b1 = res
    bad = 0
    for i in range(624):
        w, m = b0[i]
        if (w & m) != (ST[i] & m):
            bad += 1
    print(f"b0 mismatches vs true S0: {bad}/624")
    # a-regen
    v0 = 0; v1 = 0
    for k in range(64):
        w, m = b0[idx + k]
        base = w & m
        v0 |= temper(base) << (32*k)
        v1 |= temper(base | (~m & 0xffffffff)) << (32*k)
    v0 >>= 1; v1 >>= 1
    print("a-regen:", "OK" if ((a-1) == v0 or (a-1) == v1) else f"FAIL v0={v0:x} a-1={a-1:x}")
    # r-regen at pos 0
    w0 = 0; w1 = 0
    for k in range(64):
        w, m = b0[0 + k]
        base = w & m
        w0 |= temper(base) << (32*k)
        w1 |= temper(base | (~m & 0xffffffff)) << (32*k)
    w0 >>= 1; w1 >>= 1
    print("r-regen:", "OK" if ((r-1) == w0 or (r-1) == w1) else f"FAIL w0={w0:x} r-1={r-1:x}")
