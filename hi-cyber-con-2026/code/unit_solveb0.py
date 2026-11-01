#!/usr/bin/env python3
# Unit test rlib.solve_block0 with synthetic S0/S1
import sys, random
sys.path.insert(0, '/tmp/ctfA/rocinate')
import rlib
from rlib import solve_block0

random.seed(1)
MAG = 0x9908b0df
def twist_blk(cur):
    out = [0]*624
    for i in range(624):
        y = (cur[i] & 0x80000000) | (cur[(i+1)%624] & 0x7fffffff)
        out[i] = cur[(i+397)%624] ^ (y >> 1) ^ (MAG if (y & 1) else 0)
    return out

S0 = [random.getrandbits(32) for _ in range(624)]
S1 = twist_blk(S0)
S2 = twist_blk(S1)
W = 128
# K covers absolute [W, W+6528) = S0[128..623] + S1 + S2 + ...
stream = S0 + S1 + S2 + twist_blk(S2) + twist_blk(twist_blk(S2))
K = [(stream[W+j], 0xffffffff) for j in range(len(stream)-W)]

res = solve_block0(K, W)
if res is None:
    print("None!"); sys.exit()
b0, b1 = res
bad = [i for i in range(624) if (b0[i][0] & b0[i][1]) != (S0[i] & b0[i][1])]
print("mismatched indices:", bad[:10], "... count:", len(bad))
print("recovered region all bad?", all(i < W for i in bad))
# verify a couple of hand computations
i = 227; j = (i+397) % 624
u = (S0[i] & 0x80000000) | (S0[(i+1)%624] & 0x7fffffff)
expect = S1[i] ^ (u >> 1) ^ (MAG if (u & 1) else 0)
print("hand-check j:", j, "expect==S0[j]:", expect == S0[j])
print("b1[j] vs S1[j]:", (b1[j][0] & b1[j][1]) == S1[j])
