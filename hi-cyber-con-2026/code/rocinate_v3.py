#!/usr/bin/env python3
# Rocinate v3: correct MT19937 untwist recovery (mask-aware)
import pickle, sys, random, math
A = 0x9908b0df
UPPER, LOWER = 0x80000000, 0x7fffffff

def temper(x):
    x ^= (x >> 11) & 0xffffffff
    x ^= (x << 7) & 0x9d2c5680
    x ^= (x << 15) & 0xefc60000
    x ^= (x >> 18) & 0xffffffff
    return x & 0xffffffff

def untemper(y):
    y ^= (y >> 18) & 0xffffffff
    y ^= (y << 15) & 0xefc60000
    y ^= (y << 7) & 0x9d2c5680
    y &= 0xffffffff
    y ^= (y >> 11) & 0xffffffff
    return y & 0xffffffff

def words_of(val):
    """getrandbits(2047) value -> 64 (word,mask) state words, stream order (word k at bits 32k)."""
    out = []
    for k in range(63):
        out.append((untemper((val >> (32*k)) & 0xffffffff), 0xffffffff))
    w63 = ((val >> (32*63)) << 1) & 0xfffffffe
    out.append((untemper(w63), 0xfffffffe))
    return out

def untwist_rhs(rhs, R):
    """Given rhs=tw(x,y) with known-bit mask R, return (x31,xmask,ylow,ymask).
    y[j] known iff R[31] and (j==0 or R[j-1]); x31 known iff R[31] and R[30]."""
    if not (R >> 31) & 1:
        return 0, 0, 0, 0
    y0 = (rhs >> 31) & 1
    ylow = y0
    ymask = 1
    for j in range(1, 31):
        if (R >> (j-1)) & 1:
            b = (rhs >> (j-1)) & 1
            if y0 and ((A >> (j-1)) & 1):
                b ^= 1
            ylow |= b << j
            ymask |= 1 << j
    x31 = (rhs >> 30) & 1
    if y0 and ((A >> 30) & 1):
        x31 ^= 1
    xmask = 1 if ((R >> 30) & 1) else 0
    return x31, xmask, ylow, ymask

class WState:
    def __init__(self):
        self.bits = [0]*624
        self.mask = [0]*624
    def set(self, j, bits, mask):
        ov = self.mask[j] & mask
        if ov and ((self.bits[j] ^ bits) & ov):
            return False
        self.bits[j] |= bits & mask
        self.mask[j] |= mask
        return True
    def get(self, j):
        return self.bits[j], self.mask[j]
    def full(self, j):
        return self.mask[j] == 0xffffffff

def twist_blk(S):
    out = [0]*624
    for k in range(624):
        ref = S[k+397] if k < 227 else out[k-227]
        yy = (S[k] & UPPER) | (S[(k+1) % 624] & LOWER)
        t = ((yy >> 1) ^ (A if (yy & 1) else 0)) & 0xffffffff
        out[k] = ref ^ t
    return out

def recover(Sp, Spm, W, K):
    """Sp: S' words; Spm: S' masks. K: (w,m) observed stream starting at abs pos W."""
    st = WState()
    for j in range(W, 624):
        w, m = K[j-W]
        if not st.set(j, w, m):
            return None
    # pass A: k in [227,624): rhs = Sp[k]^Sp[k-227]
    for k in range(227, 624):
        R = Spm[k] & Spm[k-227]
        x31, xm, ylow, ym = untwist_rhs(Sp[k] ^ Sp[k-227], R)
        if xm and not st.set(k, x31 << 31, xm << 31): return None
        if ym and not st.set((k+1) % 624, ylow, ym): return None
    # pass B: k in [0,227): rhs = Sp[k]^S[k+397]
    for k in range(0, 227):
        ka = k + 397
        if st.mask[ka] == 0:
            continue
        R = Spm[k] & st.mask[ka]
        x31, xm, ylow, ym = untwist_rhs(Sp[k] ^ st.bits[ka], R)
        if xm and not st.set(k, x31 << 31, xm << 31): return None
        if ym and not st.set(k+1, ylow, ym): return None
    return st

def twist_check(st, Sp, Spm):
    bits, mask = st.bits, st.mask
    outb = [0]*624; outm = [0]*624
    bad = 0; tot = 0
    for k in range(624):
        yy = (bits[k] & UPPER) | (bits[(k+1) % 624] & LOWER)
        t = ((yy >> 1) ^ (A if (yy & 1) else 0)) & 0xffffffff
        if k < 227:
            ref, refm = bits[k+397], mask[k+397]
        else:
            ref, refm = outb[k-227], outm[k-227]
        tm = (mask[k] & UPPER) | (mask[(k+1) % 624] & LOWER)
        outb[k] = ref ^ t
        outm[k] = refm & tm
        needm = outm[k] & Spm[k]
        if needm:
            diff = (outb[k] ^ Sp[k]) & needm
            tot += bin(needm).count('1')
            bad += bin(diff).count('1')
    return bad, tot

def draw_vals(st, pos, max_unk=16):
    unk = []
    for k in range(64):
        w, m = st.get(pos+k)
        mm = (~m) & 0xffffffff
        while mm:
            b = (mm & (-mm)).bit_length()-1
            unk.append((k, b))
            mm &= mm-1
    if len(unk) > max_unk:
        return []
    cands = set()
    base = []
    for k in range(64):
        w, m = st.get(pos+k)
        base.append(w & m)
    for combo in range(1 << len(unk)):
        v = 0
        for k in range(64):
            x = base[k]
            for ci, (kk, b) in enumerate(unk):
                if kk == k and ((combo >> ci) & 1):
                    x |= 1 << b
            t = temper(x)
            if k == 63:
                t >>= 1
            v |= t << (32*k)
        cands.add(v)
    return sorted(cands)

def egcd(aa, bb):
    if bb == 0: return (aa, 1, 0)
    g, x1, y1 = egcd(bb, aa % bb)
    return (g, y1, x1 - (aa//bb)*y1)

def attempt(N, n, a, b, Cs, Zs, st, W, verbose=True):
    cands = draw_vals(st, W)
    if (a-1) not in cands:
        if verbose: print(f"W={W}: a-regen FAIL (unexpected)")
        return None
    if verbose: print(f"W={W}: VALIDATED.")
    pos = 0
    r_cands = []
    while pos + 64 <= W:
        for c in draw_vals(st, pos):
            if c < N:
                r_cands.append((pos, c))
        if r_cands:
            break
        pos += 64
    if not r_cands:
        if verbose: print(f"W={W}: no r candidates"); return None
    pos_r, r = r_cands[0]
    if verbose: print(f"W={W}: r at pos {pos_r} ({r.bit_length()} bits)")
    R0 = r + 1
    Ai, Bi = 1 % N, 0
    Rs = []
    for i in range(n):
        Rs.append((Ai * R0 + Bi) % N)
        Bi = (a*Bi + b) % N; Ai = (a*Ai) % N
    idx_ok = [i for i in range(n) if math.gcd(Rs[i], N) == 1]
    if len(idx_ok) < 2:
        if verbose: print("not enough invertible Rs"); return None
    Us = {i: (Zs[i] % N) * pow(Rs[i], -1, N) % N for i in idx_ok}
    i0 = idx_ok[0]
    okc = all(pow(Us[i0], Cs[j], N) == pow(Us[j], Cs[i0], N) for j in idx_ok[1:40])
    if verbose: print(f"LCG consistency: {okc}")
    if not okc:
        return None
    s_rec = None
    ii = idx_ok
    for ix in range(len(ii)):
        for jx in range(ix+1, min(len(ii), 60)):
            i, j = ii[ix], ii[jx]
            g, x, y = egcd(Cs[i], Cs[j])
            if g != 1: continue
            val = (pow(Us[i], x, N) * pow(Us[j], y, N)) % N
            if all(pow(val, Cs[k], N) == Us[k] for k in ii[:30]):
                s_rec = val
                break
        if s_rec is not None: break
    if s_rec is None:
        if verbose: print("bezout failed"); return None
    pt = s_rec.to_bytes((s_rec.bit_length()+7)//8, 'big')
    if verbose: print("RECOVERED s bytes:", pt[:100])
    return pt

def run(N, n, a, b, Cs, Zs, K, verbose=True):
    for Wmult in range(1, 8):
        W = 64*Wmult
        if 624 - W + 624 > len(K):
            if verbose: print(f"W={W}: K too short ({len(K)})"); break
        Sp = [K[624-W+i][0] for i in range(624)]
        Spm = [K[624-W+i][1] for i in range(624)]
        st = recover(Sp, Spm, W, K)
        if st is None:
            if verbose: print(f"W={W}: inconsistent")
            continue
        bad, tot = twist_check(st, Sp, Spm)
        if verbose: print(f"W={W}: twist-verify bad_bits={bad}/{tot}")
        if bad > 0:
            continue
        pt = attempt(N, n, a, b, Cs, Zs, st, W, verbose)
        if pt:
            return pt
    return None

def synth_stream(nblocks, seed=1):
    rnd = random.Random(seed)
    S = [rnd.getrandbits(32) for _ in range(624)]
    blocks = [S]
    for _ in range(nblocks-1):
        S = twist_blk(S)
        blocks.append(S)
    return [w for blk in blocks for w in blk]

def draw_val_fwd(stream, pos):
    v = 0
    for k in range(64):
        t = temper(stream[pos+k])
        if k == 63: t >>= 1
        v |= t << (32*k)
    return v

if __name__ == "__main__":
    if "--synth" in sys.argv:
        # build twist-consistent stream with full-mask words
        stream = synth_stream(11, seed=99)
        N = random.Random(5).getrandbits(2047) | (1 << 2046)
        n = 100
        Wtrue = 128   # observed stream starts at absolute 128
        pr = 0        # r at position 0 (no rejections)
        a_m1 = draw_val_fwd(stream, Wtrue)
        b_m1 = draw_val_fwd(stream, Wtrue+64)
        r = draw_val_fwd(stream, pr) + 1
        a = a_m1 + 1; b = b_m1 + 1
        rnd = random.Random(7)
        while True:
            p = rnd.getrandbits(1024) | 1<<1023; q = rnd.getrandbits(1024) | 1<<1023
            if p != q and all(p % t for t in range(3, 1000)) and all(q % t for t in range(3, 1000)):
                break
        s = rnd.getrandbits(2047)
        c = [rnd.randrange(1, 100000) for _ in range(n)]
        while math.gcd(c[0], c[1]) != 1:
            c[1] += 1
        Cs = c
        Zs = []
        R = r % N if r > N else r
        for i in range(n):
            Zs.append(R * pow(s, Cs[i], N))
            R = (a*R + b) % N
        K = [(stream[Wtrue+j], 0xffffffff) for j in range(624*10)]
        print(f"synth: stream built, Wtrue={Wtrue}, r bits={r.bit_length()}")
        pt = run(N, n, a, b, Cs, Zs, K)
        # recover s_rec again for compare: rerun internals quickly
        if pt is None:
            print("SYNTH FAILED (run returned None)")
        else:
            print("SYNTH: s_rec == s ?", int.from_bytes(pt, 'big') == s)
    else:
        with open('/tmp/ctfA/rocinate/data.pkl','rb') as f:
            d = pickle.load(f)
        N, a, b = d['N'], d['a'], d['b']
        Cs, Zs, Ts = d['Cs'], d['Zs'], d['Ts']
        n = len(Cs)
        K = []
        for val in [a, b] + list(Cs):
            K += words_of(val - 1)
        print("real data loaded; K words:", len(K))
        pt = run(N, n, a, b, Cs, Zs, K)
        print("RESULT:", pt)
