# CTF D3 - crypto (ChronoGrind, JGMTFM, Rocinate)
## Rocinate (id=3fb2ceda-d5d3-4369-b887-2b18ff34a203, 64pts)
- chall.py: p,q=getPrime(1024); N=pq; r=rand(1,N); Rs=LCG(a,b,x,N) seed r, n=100 iters; e=rand(1,N); a,b=rand; Cs=rand(1,N)x100
- Zs[i]=ri*s^ci mod N; Ts[i]=ri^e mod N. PRINT: a,b,N,Zs,Cs,Ts -> **e NO se publica**, Rs tampoco.
- Idea clave: Zs[i]^e = Ts[i]*s^(e*ci) -> Ts[i]*h^ci = Zs[i]^e con h=s^e. Sistema con e,h desconocidos.
- Prox: parsear chall.txt, medir bits, ver estructura.
## ChronoGrind (id=61784143-ff04-444c-868d-faa4c53939e5, 59pts)
- state.dat 1358B magic CGD1; flag.enc 68B magic CGFX. Patrones "LLL"/"OMLL" repetidos (posible XOR o estructura).
- Hints: "patience", "bring a charger", "cores won't save you" -> computo secuencial (hash chain / time-lock).
## JGMTFM (id=0c29db29-bbf3-4dd1-b07a-6e5f05db558f, 61pts)
- 48 tokens: 19 con letra(u,v,w,x,z)+digito, 29 con digito+digito. Posible checkerboard 5x10.
