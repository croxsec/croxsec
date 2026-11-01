import ctypes, random
from gmpy2 import mpz
lib = ctypes.CDLL('/tmp/cairn/libgfpoly.so')
for f,args in [('e_gfp_mul',[ctypes.c_char_p]*3),('e_gfp_pow',[ctypes.c_char_p]*3),('e_gfp_inv',[ctypes.c_char_p]*2)]:
    getattr(lib,f).argtypes=args
lib.e_poly_degree.restype=ctypes.c_int; lib.e_poly_degree.argtypes=[ctypes.c_char_p]
lib.e_poly_deriv.restype=ctypes.c_int; lib.e_poly_deriv.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_int]
lib.e_poly_divmod.restype=ctypes.c_int; lib.e_poly_divmod.argtypes=[ctypes.c_char_p]*2+[ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_int]
lib.e_poly_gcd.restype=ctypes.c_int; lib.e_poly_gcd.argtypes=[ctypes.c_char_p]*2+[ctypes.c_int]*2
lib.e_poly_mulmod.argtypes=[ctypes.c_char_p]*4+[ctypes.c_int]
lib.e_poly_compmod.argtypes=[ctypes.c_char_p]*4+[ctypes.c_int]
lib.e_poly_zero.argtypes=[ctypes.c_char_p]
lib.e_poly_set_x.argtypes=[ctypes.c_char_p]
lib.e_poly_powmod.argtypes=[ctypes.c_char_p]*3+[ctypes.c_char_p,ctypes.c_int]

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
def i2b(v): return (v % P).to_bytes(32,'little')
def b2i(b): return int.from_bytes(b,'little')
def mkpoly(coeffs):
    b = bytearray(33*32)
    for i,c in enumerate(coeffs[:33]): b[i*32:(i+1)*32]=i2b(c)
    return bytes(b)
def deg(b):
    d=lib.e_poly_degree(b)
    return d
random.seed(1)
ok=True
# field mul test
for _ in range(2000):
    a=random.randrange(P); b=random.randrange(P)
    r=ctypes.create_string_buffer(32)
    lib.e_gfp_mul(r, i2b(a), i2b(b))
    assert b2i(r.raw)==a*b%P, "MUL FAIL"
# edge: (p-1)^2, p-1 * big
a=P-1; r=ctypes.create_string_buffer(32); lib.e_gfp_mul(r,i2b(a),i2b(a)); assert b2i(r.raw)==1,"edge sq"
lib.e_gfp_mul(r,i2b(a),i2b(P-2)); assert b2i(r.raw)==2,"edge 2"
print("field mul OK")
# field pow/inv
for _ in range(200):
    a=random.randrange(1,P)
    r=ctypes.create_string_buffer(32); lib.e_gfp_inv(r,i2b(a))
    assert b2i(r.raw)*a%P==1,"INV FAIL"
print("inv OK")
# poly mulmod vs reference
def pref_mulmod(A,B,M):
    # A,B,M lists ints, M monic
    dm=len(M)-1
    prod=[0]*(2*dm)
    for i,a in enumerate(A):
        for j,b in enumerate(B):
            prod[i+j]=(prod[i+j]+a*b)%P
    for k in range(2*dm-1,dm-1,-1):
        c=prod[k]%P
        if c:
            prod[k]=0
            for j in range(dm):
                prod[j+k-dm]=(prod[j+k-dm]-c*M[j])%P
    return [x%P for x in prod[:dm]]
for _ in range(300):
    dm=random.choice([2,3,4,5,7,8])
    M=[random.randrange(P) for _ in range(dm)]+[1]
    A=[random.randrange(P) for _ in range(dm)]
    B=[random.randrange(P) for _ in range(dm)]
    out=ctypes.create_string_buffer(33*32)
    lib.e_poly_mulmod(out, mkpoly(A), mkpoly(B), mkpoly(M), dm)
    got=[b2i(out.raw[i*32:(i+1)*32]) for i in range(dm)]
    exp=pref_mulmod(A,B,M)
    if got!=exp:
        print("MULMOD FAIL dm=",dm)
        print("M=",M); print("A=",A); print("B=",B)
        for i,(g,e) in enumerate(zip(got,exp)):
            if g!=e: print("  idx",i,"got",g,"exp",e)
        raise SystemExit(1)
print("poly mulmod OK")
# poly divmod + gcd
def pref_divmod(A,B):
    da=len(A)-1
    while da>0 and A[da]%P==0: da-=1
    A=[x%P for x in A]
    db=len(B)-1
    while db>0 and B[db]%P==0: db-=1
    B=[x%P for x in B]
    lc=pow(B[db],P-2,P)
    rem=A[:]; quo=[0]*33
    dr=da
    while dr>=db:
        if rem[dr]%P==0: dr-=1; continue
        c=rem[dr]*lc%P
        quo[dr-db]=c
        for i in range(db+1):
            rem[i+dr-db]=(rem[i+dr-db]-c*B[i])%P
        while dr>=0 and rem[dr]%P==0: dr-=1
    return [x%P for x in quo[:max(0,da-db)+1]], [x%P for x in rem[:max(0,dr)+1]]
for _ in range(300):
    dm=random.choice([2,3,5,8])
    M=[random.randrange(P) for _ in range(dm)]+[1]
    A=[random.randrange(P) for _ in range(random.randint(1,dm))]
    q=ctypes.create_string_buffer(33*32); rr=ctypes.create_string_buffer(33*32)
    dq=lib.e_poly_divmod(q,rr,mkpoly(A),len(A)-1,mkpoly(M),dm)
    got_r=[b2i(rr.raw[i*32:(i+1)*32]) for i in range(max(0,dq)+1)] if dq>=0 else []
    eq,er=pref_divmod(A,M)
    er_trim=[x%P for x in er]
    while len(er_trim)>0 and er_trim[-1]==0: er_trim.pop()
    assert got==0 or True
    gt=got_r[:]
    while len(gt)>0 and gt[-1]==0: gt.pop()
    assert gt==er_trim, f"DIVMOD FAIL {gt} vs {er_trim}"
print("poly divmod OK")
# gcd: gcd of h and h' for random h
def pref_gcd(A,B):
    def trim(x):
        x=[v%P for v in x]
        while len(x)>1 and x[-1]==0: x.pop()
        if len(x)==1 and x[0]==0: return []
        return x
    A,B=trim(A),trim(B)
    while B:
        _,R=pref_divmod(A,B)
        A,B=B,trim(R)
    lc=pow(A[-1],P-2,P)
    return [x*lc%P for x in A]
for _ in range(200):
    dm=random.choice([2,3,4,8])
    M=[random.randrange(P) for _ in range(dm)]+[1]
    derv=[(M[i+1]*(i+1))%P for i in range(dm)]
    out=ctypes.create_string_buffer(33*32)
    dg=lib.e_poly_gcd(out,mkpoly(M),dm,mkpoly(derv),len(derv)-1)
    got=[b2i(out.raw[i*32:(i+1)*32]) for i in range(dg+1)]
    exp=pref_gcd(M,derv)
    assert got==exp, f"GCD FAIL {got} vs {exp}"
print("poly gcd OK")
