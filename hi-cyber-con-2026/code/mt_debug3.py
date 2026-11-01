#!/usr/bin/env python3
# Feed solve_block0 with EXACT untempered words from CPython getstate stepping.
import sys, random
sys.path.insert(0, '/tmp/ctfA/rocinate')
from rlib import solve_block0
from Crypto.Util.number import getPrime

random.seed(31337)
p, q = getPrime(1024), getPrime(1024)
N = p*q
while N.bit_length() != 2047:
    p, q = getPrime(1024), getPrime(1024)
    N = p*q
r = random.randint(1, N); e = random.randint(1, N)
st = random.getstate()
ST = list(st[1][:-1]); idx = st[1][-1]
W = idx
print("W:", W)

MAG = 0x9908b0df
def twist_blk(cur):
    out = [0]*624
    for i in range(624):
        y = (cur[i] & 0x80000000) | (cur[(i+1)%624] & 0x7fffffff)
        out[i] = cur[(i+397)%624] ^ (y >> 1) ^ (MAG if (y & 1) else 0)
    return out

# Build exact untempered stream starting at position W, length 6528
stream = []
cur = ST[:]           # current block, next emitted index = W
pos = W
blocks = [cur]
nxt = twist_blk(cur)
while len(stream) < 6528:
    blk_idx = len(stream) + W
    # absolute position blk_idx; block k covers [624k, 624(k+1))
    k = blk_idx // 624
    i = blk_idx % 624
    while len(blocks) <= k:
        blocks.append(twist_blk(blocks[-1]))
    stream.append(blocks[k][i])

K = [(w, 0xffffffff) for w in stream[:6528]]
res = solve_block0(K, W)
b0, b1 = res
bad = [i for i in range(624) if b0[i][0] != ST[i]]
print("exact-word b0 mismatches:", len(bad), bad[:8])

# Now with words_of masks from simulated getrandbits draws
from rlib import untemper, temper, words_of
K2 = []
j = 0
for d in range(102):
    words = stream[j:j+64]; j += 64
    val = 0
    for k in range(64):
        val |= temper(words[k]) << (32*k)
    val >>= 1  # getrandbits(2047) drop
    K2.extend(words_of(val))
res2 = solve_block0(K2, W)
b0b, b1b = res2
badb = [i for i in range(624) if (b0b[i][0] & b0b[i][1]) != (ST[i] & b0b[i][1])]
print("words_of-masked b0 mismatches:", len(badb), badb[:8])
