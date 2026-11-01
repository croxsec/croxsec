import ctypes, random
lib = ctypes.CDLL('/tmp/cairn/libgfpoly.so')
lib.e_poly_mulmod.argtypes=[ctypes.c_char_p]*4+[ctypes.c_int]
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
def i2b(v): return (v % P).to_bytes(32,'little')
def b2i(b): return int.from_bytes(b,'little')
def mkpoly(coeffs):
    b = bytearray(33*32)
    for i,c in enumerate(coeffs[:33]): b[i*32:(i+1)*32]=i2b(c)
    return bytes(b)
def pref_mulmod(A,B,M):
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
random.seed(42)
dm=3
M=[random.randrange(P) for _ in range(dm)]+[1]
A=[random.randrange(P) for _ in range(dm)]
B=[random.randrange(P) for _ in range(dm)]
out=ctypes.create_string_buffer(33*32)
lib.e_poly_mulmod(out, mkpoly(A), mkpoly(B), mkpoly(M), dm)
got=[b2i(out.raw[i*32:(i+1)*32]) for i in range(dm)]
exp=pref_mulmod(A,B,M)
print("match",got==exp)
if got!=exp:
    for i,(g,e) in enumerate(zip(got,exp)):
        if g!=e: print("idx",i,"got",g,"exp",e)
dm=2
M=[1,2,1]
A=[3,4]
B=[5,6]
out=ctypes.create_string_buffer(33*32)
lib.e_poly_mulmod(out, mkpoly(A), mkpoly(B), mkpoly(M), dm)
got=[b2i(out.raw[i*32:(i+1)*32]) for i in range(dm)]
exp=pref_mulmod(A,B,M)
print("small", got==exp, "got",got,"exp",exp)
