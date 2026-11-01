#!/usr/bin/env python3
# Rocinate solver v2 — proper W validation via twist recurrence on known region.
import sys, math, pickle, random
sys.path.insert(0, '/tmp/ctfA/rocinate')
from rlib import untemper, temper, words_of, solve_block0, draw_val, enum_vals
from Crypto.Util.number import long_to_bytes, bytes_to_long, getPrime

SYNTH = '--synth' in sys.argv

if SYNTH:
    # capture true W for diagnostics
    import random as _r
    st = _r.getstate()
    random.seed(31337)
    _p, _q = getPrime(1024), getPrime(1024)
    _N = _p*_q
    while _N.bit_length() != 2047:
        _p, _q = getPrime(1024), getPrime(1024)
        _N = _p*_q
    def _draw_len():
        cnt = 0
        while True:
            cnt += 1
            v = random.getrandbits(2047)
            if v < _N: return cnt*64
    Wr = _draw_len(); We = _draw_len()
    print(f"SYNTH true W = {Wr+We} (r={Wr}, e={We})")
    random.seed(31337)
    sz, n = 1024, 100
    p, q = getPrime(sz), getPrime(sz)
    N = p*q
    while N.bit_length() != 2047:
        p, q = getPrime(sz), getPrime(sz)
        N = p*q
    flag = b'hiCTF{synth_test_rocinate_12345}'
    s = bytes_to_long(flag)
    def lcg(a,b,x,N): return (a*x+b)%N
    r = random.randint(1,N)
    Rs=[r]
    e = random.randint(1,N)
    a,b = random.randint(1,N), random.randint(1,N)
    for _ in range(n-1): Rs.append(lcg(a,b,Rs[-1],N))
    Cs = [random.randint(1,N) for _ in range(n)]
    Zs = [ri*pow(s,ci,N) for ri,ci in zip(Rs,Cs)]
    Ts = [pow(ri,e,N) for ri in Rs]
    print("SYNTH setup done, true W should be multiple of 64 (r,e draws)")
else:
    d = pickle.load(open('/tmp/ctfA/rocinate/data.pkl','rb'))
    a,b,N,Zs,Cs,Ts = d['a'],d['b'],d['N'],d['Zs'],d['Cs'],d['Ts']
    n = len(Zs)

K = []
for v in [a-1, b-1] + [c-1 for c in Cs]:
    K.extend(words_of(v))
print("K len:", len(K))

def draw_val_t(words, start):
    """Reconstruct getrandbits(2047) output candidates.
    CPython assembles first-tempered-word as LSW; only the LAST word (MSW)
    gets >>1. Unknown state bits (from recovery masks) enumerated.
    Returns list of candidate integer values."""
    # find unknown bits in the 64 state words (state domain)
    unk = []  # (k, bitpos_in_word)
    for k in range(64):
        w, m = words[start+k]
        mm = (~m) & 0xffffffff
        while mm:
            b = (mm & (-mm)).bit_length()-1
            unk.append((k, b))
            mm &= mm-1
    if len(unk) > 12:
        return []
    cands = set()
    for combo in range(1 << len(unk)):
        v = 0
        for k in range(64):
            w, m = words[start+k]
            x = w & m
            for ci, (kk, b) in enumerate(unk):
                if kk == k and ((combo >> ci) & 1):
                    x |= 1 << b
            tw_ = temper(x)
            if k == 63:
                tw_ >>= 1  # getrandbits drops MSW bit0
            v |= tw_ << (32*k)
        cands.add(v)
    return sorted(cands)

def tw(x, y):
    yy = (x & 0x80000000) | (y & 0x7fffffff)
    return (yy >> 1) ^ (0x9908b0df if (yy & 1) else 0)

found = False
for Wmult in range(1, 9):
    W = 64*Wmult
    res = solve_block0(K, W)
    if res is None:
        print(f"W={W}: solve failed (K short)"); continue
    b0, b1 = res
    # REAL discriminator: twist(b1) must equal next observed block K[1248-W : 1872-W]
    bad = 0; tot = 0
    for i in range(624):
        x, xm = b1[i]; y, ym = b1[(i+1) % 624]; xa, ma = b1[(i+397) % 624]
        kb, km = K[1248 - W + i]
        u = (x & 0x80000000) | (y & 0x7fffffff)
        pred = xa ^ (u >> 1) ^ (0x9908b0df if (u & 1) else 0)
        m_all = xm & ym & ma & km
        tot += 1
        if (pred ^ kb) & m_all: bad += 1
    print(f"W={W}: next-block twist check bad={bad}/{tot}")
    if bad > 0:
        continue
    if W + 64 > 624:
        print(f"W={W}: skip (straddles block boundary)")
        continue
    cands = draw_val_t(b0, W)
    if (a-1) not in cands:
        print(f"W={W}: a-regen mismatch (unexpected!)")
        continue
    print(f"W={W}: a-regen OK (W validated)")
    # find r: draws at 0,64,...; first accepted = r
    pos = 0
    r_cands = []
    while pos + 64 <= W:
        cands = [c for c in draw_val_t(b0, pos) if c < N]
        if cands:
            r_cands.append((pos, cands))
        pos += 64
    print(f"r-candidate positions: {[(p, len(ac)) for p, ac in r_cands]}")
    if not r_cands:
        print("no r candidates"); continue
    rpos, acc = r_cands[0]
    print(f"using r at pos {rpos} with {len(acc)} candidate value(s)")
    Ai, Bi = 1 % N, 0
    for rv in acc:
        R0 = rv + 1
        Rs = []
        Ai, Bi = 1 % N, 0
        for i in range(n):
            Rs.append((Ai * R0 + Bi) % N)
            Bi = (a*Bi+b) % N; Ai = (a*Ai) % N
        Us = [(Zs[i] % N) * pow(Rs[i], -1, N) % N for i in range(n)]
        okp = all(pow(Us[0], Cs[j], N) == pow(Us[j], Cs[0], N) for j in range(1, 30))
        print(f"  R0={R0.bit_length()}b consistency={okp}")
        if not okp: continue
        # stage-2: bezout over coprime pairs, quick verify then full verify
        def eg(aa, bb):
            if bb == 0: return (1, 0)
            xx, yy = eg(bb, aa % bb)
            return (yy, xx - (aa // bb) * yy)
        gflag = None
        pairs = [(i, j) for i in range(n) for j in range(i+1, n) if math.gcd(Cs[i], Cs[j]) == 1]
        for (i, j) in pairs:
            x, y = eg(Cs[i], Cs[j])
            t = pow(Us[i], x, N) * pow(Us[j], y, N) % N
            if all(pow(t, Cs[k], N) == Us[k] for k in (0, 1, 2, 3, 50, 77)):
                if all(pow(t, Cs[k], N) == Us[k] for k in range(n)):
                    gflag = t; break
        if gflag:
            flag = long_to_bytes(gflag)
            print("="*40)
            print("FLAG:", flag)
            open('/tmp/rocinate_flag.txt','wb').write(flag)
            found = True
            break
    if found: break
if not found:
    print("FAILED")
