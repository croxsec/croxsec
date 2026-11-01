import ctypes, random
lib = ctypes.CDLL('/tmp/cairn/libgfpoly.so')
for f in ['e_gfp_mul_raw','e_red512']:
    getattr(lib,f).argtypes=[ctypes.c_char_p]*3 if f=='e_gfp_mul_raw' else [ctypes.c_char_p]*2
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
def i2b(v): return (v % P).to_bytes(32,'little')
def b2i(b): return int.from_bytes(b,'little')
random.seed(7)
bad=0
for trial in range(20000):
    a=random.randrange(P); b=random.randrange(P)
    raw=ctypes.create_string_buffer(64)
    lib.e_gfp_mul_raw(raw, i2b(a), i2b(b))
    traw=int.from_bytes(raw.raw,'little')
    if traw != a*b:
        print("MUL4 FAIL", trial); bad+=1; break
print("mul4 ok" if not bad else "mul4 BAD")
# red512 via random 512-bit values
bad=0
for trial in range(50000):
    t=random.getrandbits(512)
    tb=t.to_bytes(64,'little')
    r=ctypes.create_string_buffer(32)
    lib.e_red512(r, tb)
    if b2i(r.raw) != t % P:
        print("RED512 FAIL", trial, hex(t))
        print("got", hex(b2i(r.raw)))
        print("exp", hex(t%P))
        bad+=1
        if bad>3: break
print("red512 ok" if not bad else f"red512 BAD {bad}")
