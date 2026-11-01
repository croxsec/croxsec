// Chain: V = seed(32B BE); repeat cycles: V = SHA256(V); if(domod && v>=anchor) v%=anchor (bit-loop, u32 limbs)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef uint32_t u32; typedef uint8_t u8; typedef uint64_t u64;
#define ROR(x,n) ((x>>(n))|(x<<(32-(n))))
#define CH(x,y,z) ((x&y)^(~x&z))
#define MAJ(x,y,z) ((x&y)^(x&z)^(y&z))
#define EP0(x) (ROR(x,2)^ROR(x,13)^ROR(x,22))
#define EP1(x) (ROR(x,6)^ROR(x,11)^ROR(x,25))
#define SIG0(x) (ROR(x,7)^ROR(x,18)^(x>>3))
#define SIG1(x) (ROR(x,17)^ROR(x,19)^(x>>10))

static const u32 K[64]={0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};

// SHA256 of exactly 32 bytes given as 8 big-endian u32 limbs; output same convention
static void sha256_32(const u32 *vin, u32 *vout){
    u8 p[64];
    for(int i=0;i<8;i++){ p[4*i]=vin[i]>>24; p[4*i+1]=(vin[i]>>16)&0xff; p[4*i+2]=(vin[i]>>8)&0xff; p[4*i+3]=vin[i]&0xff; }
    p[32]=0x80;
    memset(p+33,0,23);
    p[56]=0; p[57]=0; p[58]=0; p[59]=0; p[60]=0; p[61]=0; p[62]=1; p[63]=0; // bitlen=256 BE
    u32 w[64];
    for(int i=0;i<16;i++) w[i]=(p[4*i]<<24)|(p[4*i+1]<<16)|(p[4*i+2]<<8)|p[4*i+3];
    for(int i=16;i<64;i++) w[i]=SIG1(w[i-2])+w[i-7]+SIG0(w[i-15])+w[i-16];
    u32 a=0x6a09e667,b=0xbb67ae85,c=0x3c6ef372,d=0xa54ff53a,e=0x510e527f,f=0x9b05688c,g=0x1f83d9ab,h=0x5be0cd19;
    for(int i=0;i<64;i++){
        u32 t1=h+EP1(e)+CH(e,f,g)+K[i]+w[i];
        u32 t2=EP0(a)+MAJ(a,b,c);
        h=g; g=f; f=e; e=d+t1; d=c; c=b; b=a; a=t1+t2;
    }
    u32 H[8]={a+0x6a09e667,b+0xbb67ae85,c+0x3c6ef372,d+0xa54ff53a,e+0x510e527f,f+0x9b05688c,g+0x1f83d9ab,h+0x5be0cd19};
    for(int i=0;i<8;i++) vout[i]=H[i];
}

static int cmpv(const u32*a,const u32*b){for(int i=0;i<8;i++){if(a[i]!=b[i])return a[i]>b[i]?1:-1;}return 0;}

static void subm(u32*rem,const u32*m){
    u64 br=0;
    for(int i=7;i>=0;i--){
        u64 sub=(u64)m[i]+br;
        u64 orig=rem[i];
        u64 d=orig-sub;
        rem[i]=(u32)d;
        br=(orig<sub)?1:0;
    }
}

static int bitlen(const u32*m){ int bl=256; for(int i=0;i<8;i++){ if(m[i]==0){bl-=32;continue;} bl-=__builtin_clz(m[i]); break;} return bl; }

static void shl(const u32*a,int k,u32*out){ // out = a << k, 0<=k<32
    if(k==0){ memcpy(out,a,32); return; }
    for(int i=0;i<8;i++){ u32 lo=a[i]; u32 hi=(i+1<8)?a[i+1]:0; out[i]=(lo<<k)|(hi>>(32-k)); }
}

// v %= m using precomputed shifted divisors vs[k]=m<<k, k=0..smax-1 (smax<=31 guaranteed by caller)
static void mod32p(u32*v,u32 vs[][8],int smax){
    if(cmpv(v,vs[0])<0) return;
    for(int k=smax-1;k>=0;k--){
        if(cmpv(v,vs[k])>=0) subm(v,vs[k]);
    }
}

int main(int argc,char**argv){
    if(argc>=2 && !strcmp(argv[1],"selftest")){
        u32 in[8], out[8];
        for(int i=0;i<8;i++) in[i]=0x03020100u + 0x04040404u*i; // bytes 0..31
        for(int i=0;i<8;i++){ u32 v=(u32)(4*i)<<24 | (u32)(4*i+1)<<16 | (u32)(4*i+2)<<8 | (u32)(4*i+3); in[i]=v; }
        sha256_32(in,out);
        for(int i=0;i<8;i++) printf("%08x",out[i]); printf("\n");
        return 0;
    }
    if(argc<4){fprintf(stderr,"usage: %s seedhex anchorhex|- cycles\n",argv[0]);return 1;}
    u32 seed[8]; for(int i=0;i<8;i++){unsigned v;sscanf(argv[1]+8*i,"%8x",&v);seed[i]=v;}
    int domod = strcmp(argv[2],"-")!=0;
    u32 anchor[8];
    u32 vs[32][8]; int smax=0;
    if(domod){
        for(int i=0;i<8;i++){unsigned v;sscanf(argv[2]+8*i,"%8x",&v);anchor[i]=v;}
        int bl=bitlen(anchor);
        smax=257-bl; if(smax>32) smax=32; if(smax<1) smax=1;
        for(int k=0;k<smax;k++) shl(anchor,k,vs[k]);
    }
    u64 cycles = strtoull(argv[3],0,10);
    u32 v[8]; memcpy(v,seed,32);
    u32 tmp[8];
    for(u64 i=0;i<cycles;i++){
        sha256_32(v,tmp);
        memcpy(v,tmp,32);
        if(domod && cmpv(v,anchor)>=0){ mod32p(v,vs,smax); }
    }
    for(int i=0;i<8;i++) printf("%08x",v[i]);
    printf("\n");
    return 0;
}
