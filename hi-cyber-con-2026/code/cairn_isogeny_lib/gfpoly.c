// GF(p) polynomial toolkit, p = secp256k1 prime = 2^256 - 2^32 - 977
// Coeffs: 256-bit as 4 little-endian uint64 limbs. Polys: 33 coeffs (1056B).
#include <stdint.h>
#include <string.h>

typedef struct { uint64_t c[33][4]; } Poly;

static const uint64_t P[4] = {0xFFFFFFFEFFFFFC2FULL, 0xFFFFFFFFFFFFFFFFULL,
                              0xFFFFFFFFFFFFFFFFULL, 0xFFFFFFFFFFFFFFFFULL};

static inline void mul4(uint64_t t[8], const uint64_t a[4], const uint64_t b[4]) {
    for (int i = 0; i < 8; i++) t[i] = 0;
    for (int i = 0; i < 4; i++) {
        uint64_t carry = 0, ai = a[i];
        for (int j = 0; j < 4; j++) {
            __uint128_t prod = (__uint128_t)ai * b[j] + t[i+j] + carry;
            t[i+j] = (uint64_t)prod;
            carry = (uint64_t)(prod >> 64);
        }
        t[i+4] += carry;
    }
}

// t mod p, t < 2^512. 2^256 ≡ 2^32 + 977 (mod p).
static inline void red512(uint64_t r[4], const uint64_t t[8]) {
    __uint128_t A[5];
    for (int i = 0; i < 5; i++) A[i] = 0;
    for (int i = 0; i < 4; i++) A[i] += t[i];
    // H*977
    uint64_t carry = 0;
    for (int i = 0; i < 4; i++) {
        __uint128_t prod = (__uint128_t)t[4+i] * 977ULL + carry;
        A[i] += (uint64_t)prod;
        carry = (uint64_t)(prod >> 64);
    }
    A[4] += carry;
    // H<<32 : limb i += (H[i]<<32) truncated, limb i+1 += H[i]>>32
    for (int i = 0; i < 4; i++) {
        A[i] += (uint64_t)(t[4+i] << 32);
        A[i+1] += (t[4+i] >> 32);
    }
    for (int i = 0; i < 4; i++) { A[i+1] += A[i] >> 64; A[i] &= 0xFFFFFFFFFFFFFFFFULL; }
    uint64_t hi = (uint64_t)A[4];
    uint64_t hi2 = (uint64_t)(A[4] >> 64);
    uint64_t a0=(uint64_t)A[0], a1=(uint64_t)A[1], a2=(uint64_t)A[2], a3=(uint64_t)A[3];
    // fold hi2*(2^320) = hi2*(2^96 + 977*2^64)
    if (hi2) {
        __uint128_t v;
        v = (__uint128_t)a0 + hi2 * 977ULL; a0 = (uint64_t)v; uint64_t cy = (uint64_t)(v >> 64);
        v = (__uint128_t)a1 + cy; a1 = (uint64_t)v; cy = (uint64_t)(v >> 64);
        if (cy) { v = (__uint128_t)a2 + cy; a2 = (uint64_t)v; cy = (uint64_t)(v >> 64); if (cy) a3 += cy; }
        v = (__uint128_t)a1 + (uint64_t)(hi2 << 32); a1 = (uint64_t)v; cy = (uint64_t)(v >> 64);
        v = (__uint128_t)a2 + (hi2 >> 32) + cy; a2 = (uint64_t)v; cy = (uint64_t)(v >> 64);
        if (cy) { a3 += cy; }
    }
    // fold hi*(2^32+977)
    {
        __uint128_t v;
        v = (__uint128_t)a0 + hi * 977ULL; a0 = (uint64_t)v; uint64_t cy = (uint64_t)(v >> 64);
        v = (__uint128_t)a1 + cy; a1 = (uint64_t)v; cy = (uint64_t)(v >> 64);
        if (cy) { v = (__uint128_t)a2 + cy; a2 = (uint64_t)v; cy = (uint64_t)(v >> 64); if (cy) a3 += cy; }
        v = (__uint128_t)a0 + (uint64_t)(hi << 32); a0 = (uint64_t)v; cy = (uint64_t)(v >> 64);
        v = (__uint128_t)a1 + (hi >> 32) + cy; a1 = (uint64_t)v; cy = (uint64_t)(v >> 64);
        if (cy) { v = (__uint128_t)a2 + cy; a2 = (uint64_t)v; cy = (uint64_t)(v >> 64); if (cy) a3 += cy; }
    }
    uint64_t val[4] = {a0, a1, a2, a3};
    for (int rep = 0; rep < 2; rep++) {
        int ge = 0;
        for (int i = 3; i >= 0; i--) {
            if (val[i] > P[i]) { ge = 1; break; }
            if (val[i] < P[i]) { ge = -1; break; }
        }
        if (ge == 0) ge = 1;
        if (ge > 0) {
            uint64_t borrow = 0;
            for (int i = 0; i < 4; i++) {
                uint64_t pb = P[i] + borrow;
                uint64_t nb = (pb < P[i]) || (val[i] < pb);
                val[i] = val[i] - pb; borrow = nb;
            }
        }
    }
    memcpy(r, val, 32);
}

static inline void gfp_mul(uint64_t r[4], const uint64_t a[4], const uint64_t b[4]) {
    uint64_t t[8]; mul4(t, a, b); red512(r, t);
}
static inline void gfp_sqr(uint64_t r[4], const uint64_t a[4]) {
    uint64_t t[8]; mul4(t, a, a); red512(r, t);
}
static inline int gfp_iszero(const uint64_t a[4]) { return (a[0]|a[1]|a[2]|a[3]) == 0; }
static inline void gfp_copy(uint64_t r[4], const uint64_t a[4]) { memcpy(r, a, 32); }
static inline void gfp_set_u64(uint64_t r[4], uint64_t v) { r[0]=v; r[1]=0; r[2]=0; r[3]=0; }

// a+b mod p (inputs < p)
static inline void gfp_add(uint64_t r[4], const uint64_t a[4], const uint64_t b[4]) {
    __uint128_t v;
    v = (__uint128_t)a[0] + b[0]; r[0] = (uint64_t)v; uint64_t cy = (uint64_t)(v >> 64);
    for (int i = 1; i < 4; i++) { v = (__uint128_t)a[i] + b[i] + cy; r[i] = (uint64_t)v; cy = (uint64_t)(v >> 64); }
    if (cy) { // a+b >= 2^256 : add (2^32+977)
        uint64_t C[4] = {977ULL, 1ULL, 0, 0};
        v = (__uint128_t)r[0] + C[0]; r[0] = (uint64_t)v; cy = (uint64_t)(v >> 64);
        for (int i = 1; i < 4; i++) { v = (__uint128_t)r[i] + C[i] + cy; r[i] = (uint64_t)v; cy = (uint64_t)(v >> 64); }
    }
    // conditional subtract p
    int ge = 0;
    for (int i = 3; i >= 0; i--) { if (r[i] > P[i]) { ge = 1; break; } if (r[i] < P[i]) { ge = -1; break; } }
    if (ge == 0) ge = 1;
    if (ge > 0) {
        uint64_t borrow = 0;
        for (int i = 0; i < 4; i++) { uint64_t pb = P[i] + borrow; uint64_t nb = (pb < P[i]) || (r[i] < pb); r[i] = r[i] - pb; borrow = nb; }
    }
}
static inline void gfp_sub(uint64_t r[4], const uint64_t a[4], const uint64_t b[4]) {
    uint64_t borrow = 0;
    for (int i = 0; i < 4; i++) {
        uint64_t bb = b[i] + borrow;
        uint64_t nb = (bb < b[i]) || (a[i] < bb);
        r[i] = a[i] - bb; borrow = nb;
    }
    if (borrow) {
        __uint128_t v;
        v = (__uint128_t)r[0] + P[0]; r[0] = (uint64_t)v; uint64_t cy = (uint64_t)(v >> 64);
        for (int i = 1; i < 4; i++) { v = (__uint128_t)r[i] + P[i] + cy; r[i] = (uint64_t)v; cy = (uint64_t)(v >> 64); }
    }
}

static void gfp_pow(uint64_t r[4], const uint64_t a[4], const uint8_t e[32]) {
    uint64_t base[4]; gfp_copy(base, a);
    gfp_set_u64(r, 1);
    int started = 0;
    for (int i = 31; i >= 0; i--) {
        uint8_t byte = e[i];
        for (int j = 7; j >= 0; j--) {
            int bit = (byte >> j) & 1;
            if (!started) { if (bit) { started = 1; gfp_copy(r, base); } continue; }
            gfp_sqr(r, r);
            if (bit) gfp_mul(r, r, base);
        }
    }
}

// p-2 = 0xFFFF...FFFFEFFFFFC2D, LE bytes
static const uint8_t PM2[32] = {0x2D,0xFC,0xFF,0xFF,0xFE,0xFF,0xFF,0xFF,
                                0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,
                                0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,
                                0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF};
static inline void gfp_inv(uint64_t r[4], const uint64_t a[4]) { gfp_pow(r, a, PM2); }

int poly_degree(const Poly* a) {
    for (int i = 32; i >= 0; i--) if (!gfp_iszero(a->c[i])) return i;
    return -1;
}
void poly_zero(Poly* a) { memset(a, 0, sizeof(Poly)); }
void poly_set_scalar(Poly* a, const uint64_t s[4]) { poly_zero(a); gfp_copy(a->c[0], s); }
void poly_set_x(Poly* a) { poly_zero(a); gfp_set_u64(a->c[1], 1); }

int poly_deriv(Poly* out, const Poly* a, int da) {
    poly_zero(out);
    if (da <= 0) return -1;
    for (int i = 1; i <= da; i++) {
        uint64_t f[4]; gfp_set_u64(f, (uint64_t)i);
        gfp_mul(out->c[i-1], a->c[i], f);
    }
    return da - 1;
}

int poly_divmod(Poly* q, Poly* r, const Poly* a, int da, const Poly* b, int db) {
    static Poly rem, quo;
    poly_zero(&quo); poly_zero(&rem);
    for (int i = 0; i <= da; i++) gfp_copy(rem.c[i], a->c[i]);
    uint64_t lcinv[4]; gfp_inv(lcinv, b->c[db]);
    int dr = da;
    while (dr >= db) {
        if (gfp_iszero(rem.c[dr])) { dr--; continue; }
        uint64_t coeff[4]; gfp_mul(coeff, rem.c[dr], lcinv);
        int shift = dr - db;
        gfp_copy(quo.c[shift], coeff);
        uint64_t tmp[4];
        for (int i = 0; i <= db; i++) {
            gfp_mul(tmp, coeff, b->c[i]);
            gfp_sub(rem.c[i+shift], rem.c[i+shift], tmp);
        }
        while (dr >= 0 && gfp_iszero(rem.c[dr])) dr--;
    }
    for (int i = 0; i < 33; i++) gfp_copy(r->c[i], rem.c[i]);
    for (int i = 0; i < 33; i++) gfp_copy(q->c[i], quo.c[i]);
    return dr;
}

int poly_gcd(Poly* out, const Poly* a, int da, const Poly* b, int db) {
    static Poly x, y, q, r;
    for (int i = 0; i < 33; i++) { gfp_copy(x.c[i], a->c[i]); gfp_copy(y.c[i], b->c[i]); }
    int dx = da, dy = db;
    while (dy >= 0) {
        int dr = poly_divmod(&q, &r, &x, dx, &y, dy);
        for (int i = 0; i < 33; i++) { gfp_copy(x.c[i], y.c[i]); gfp_copy(y.c[i], r.c[i]); }
        dx = dy; dy = dr;
    }
    if (dx < 0) { poly_zero(out); return -1; }
    uint64_t lcinv[4]; gfp_inv(lcinv, x.c[dx]);
    uint64_t tmp[4];
    poly_zero(out);
    for (int i = 0; i <= dx; i++) { gfp_mul(tmp, x.c[i], lcinv); gfp_copy(out->c[i], tmp); }
    return dx;
}

void poly_mulmod(Poly* out, const Poly* a, const Poly* b, const Poly* m, int dm) {
    static __thread uint64_t prod[65][4];
    memset(prod, 0, (size_t)(2*dm) * 32);
    uint64_t tmp[4];
    for (int i = 0; i < dm; i++) {
        if (gfp_iszero(a->c[i])) continue;
        for (int j = 0; j < dm; j++) {
            if (gfp_iszero(b->c[j])) continue;
            gfp_mul(tmp, a->c[i], b->c[j]);
            gfp_add(prod[i+j], prod[i+j], tmp);
        }
    }
    for (int k = 2*dm - 1; k >= dm; k--) {
        if (gfp_iszero(prod[k])) continue;
        uint64_t co[4]; gfp_copy(co, prod[k]);
        memset(prod[k], 0, 32);
        for (int j = 0; j < dm; j++) {
            if (gfp_iszero(m->c[j])) continue;
            gfp_mul(tmp, co, m->c[j]);
            gfp_sub(prod[j + k - dm], prod[j + k - dm], tmp);
        }
    }
    memset(out, 0, (size_t)dm * 32);
    for (int i = 0; i < dm; i++) gfp_copy(out->c[i], prod[i]);
}

void poly_sqrmod(Poly* out, const Poly* a, const Poly* m, int dm) {
    poly_mulmod(out, a, a, m, dm);
}

void poly_powmod(Poly* out, const Poly* base, const Poly* m, const uint8_t exp[32], int dm) {
    static __thread Poly table[16];
    uint64_t one[4]; gfp_set_u64(one, 1);
    poly_set_scalar(&table[0], one);
    for (int k = 1; k < 16; k++) poly_mulmod(&table[k], &table[k-1], base, m, dm);
    int started = 0;
    static __thread Poly acc;
    poly_set_scalar(&acc, one);
    for (int i = 31; i >= 0; i--) {
        for (int half = 0; half < 2; half++) {
            int nib = half ? (exp[i] & 0xF) : ((exp[i] >> 4) & 0xF);
            if (!started) {
                if (nib) { started = 1;
                    for (int j = 0; j < 33; j++) gfp_copy(acc.c[j], table[nib].c[j]);
                }
            } else {
                for (int s = 0; s < 4; s++) poly_sqrmod(&acc, &acc, m, dm);
                if (nib) poly_mulmod(&acc, &acc, &table[nib], m, dm);
            }
        }
    }
    for (int j = 0; j < 33; j++) gfp_copy(out->c[j], acc.c[j]);
}

void poly_compmod(Poly* out, const Poly* f, const Poly* g, const Poly* m, int dm) {
    static __thread Poly acc, t;
    int df = poly_degree(f);
    if (df < 0) { poly_zero(out); return; }
    poly_set_scalar(&acc, f->c[df]);
    for (int k = df - 1; k >= 0; k--) {
        poly_mulmod(&t, &acc, g, m, dm);
        for (int j = 0; j < 33; j++) gfp_copy(acc.c[j], t.c[j]);
        gfp_add(acc.c[0], acc.c[0], f->c[k]);
    }
    for (int j = 0; j < 33; j++) gfp_copy(out->c[j], acc.c[j]);
}

// ---- exports for Python (buffers 1056B unless noted) ----
int e_poly_degree(const uint8_t* a) { return poly_degree((const Poly*)a); }
void e_poly_zero(uint8_t* a) { poly_zero((Poly*)a); }
void e_poly_set_x(uint8_t* a) { poly_set_x((Poly*)a); }
int e_poly_deriv(uint8_t* out, const uint8_t* a, int da) { return poly_deriv((Poly*)out, (const Poly*)a, da); }
int e_poly_divmod(uint8_t* q, uint8_t* r, const uint8_t* a, int da, const uint8_t* b, int db) {
    return poly_divmod((Poly*)q, (Poly*)r, (const Poly*)a, da, (const Poly*)b, db);
}
int e_poly_gcd(uint8_t* out, const uint8_t* a, int da, const uint8_t* b, int db) {
    return poly_gcd((Poly*)out, (const Poly*)a, da, (const Poly*)b, db);
}
void e_poly_mulmod(uint8_t* out, const uint8_t* a, const uint8_t* b, const uint8_t* m, int dm) {
    poly_mulmod((Poly*)out, (const Poly*)a, (const Poly*)b, (const Poly*)m, dm);
}
void e_poly_powmod(uint8_t* out, const uint8_t* base, const uint8_t* m, const uint8_t* exp, int dm) {
    poly_powmod((Poly*)out, (const Poly*)base, (const Poly*)m, exp, dm);
}
void e_poly_compmod(uint8_t* out, const uint8_t* f, const uint8_t* g, const uint8_t* m, int dm) {
    poly_compmod((Poly*)out, (const Poly*)f, (const Poly*)g, (const Poly*)m, dm);
}
void e_gfp_mul(uint8_t* r, const uint8_t* a, const uint8_t* b) { gfp_mul((uint64_t*)r, (const uint64_t*)a, (const uint64_t*)b); }
void e_gfp_pow(uint8_t* r, const uint8_t* a, const uint8_t* e) { gfp_pow((uint64_t*)r, (const uint64_t*)a, e); }
void e_gfp_inv(uint8_t* r, const uint8_t* a) { gfp_inv((uint64_t*)r, (const uint64_t*)a); }
// debug exports
void e_gfp_mul_raw(uint8_t* r, const uint8_t* a, const uint8_t* b) { mul4((uint64_t*)r, (const uint64_t*)a, (const uint64_t*)b); }
void e_red512(uint8_t* r, const uint8_t* t) { red512((uint64_t*)r, (const uint64_t*)t); }
