# CTF D3c notes — HI Cyber Con 2026 (CROX Sec)
Fecha: 2026-11-01 ~17:30 CST. Quedan ~4.5h. Estado equipo: 21 kills/1160 pts.

## ChronoGrind (58pts, id 61784143-ff04-444c-868d-faa4c53939e5)
- state.dat 1358B magic CGD1. TODO el archivo (tras magic) es XOR 0x6c.
- Decodificado: header "TEAM TESTRUN1", marcadores "#!  " (OMLL), mensajes "THE ANCHOR HOLDS"/"KEEP GRINDING".
- NOTAS EMBEBIDAS (autodescriptivas): DEVICE NOTES
  ANCHOR = REC{11} BASE...; SEED = REC{22}...; CYCLES = REC{33}...; CHK = REC{44}
  CHK = SHA256(ANCHOR:SEED:CYCLES) decimal colon separated
  DERIVATION: K = SEED, REPEAT CYCLES TIMES: V = SHA256(V) MOD ANCHOR
  MSG CONTAINER cgfx MAGIC(cgfx) VER NONCE TAG CT REST
  AEAD = CHACHA20-POLY1305, KEY=K, NONCE=nonce FIELD
  FLAG = AEAD-DECRYPT(K,NONCE,CT), TAG MUST VERIFY
- Registros: R1=data[0x1c:0x120] (260B), R2=data[0x124:0x269] (325B; 256B binario + art ASCII 69B), R3=data[0x26d:0x372] (261B), R4 notas.
- Tráilers 4B: R1 end 0x11c=2d410964 (u32LE 1.68e9); R2 binario end 0x224=8c0cd47f (u32LE 2.15e9). Candidatos CYCLES ~10^9.
- Dígitos en notas: bytes 0x1N codifican dígito N (\x11='1'..); \x1a=':', \x1d='=', \x07='(', \x08=')', \x00=sep.
- NONCE(12B) TAG(16B) → ChaCha20-Poly1305 confirmado.
- flag.enc 68B: CGFX + 01 fb71b0a2 00955be7 728a5b4c f84a1f9f 80317d48 ce64361c 61b6a307 0d6b477e 3776f59c 3de606b0 c967d787 5e65c135 ab0369ce 46e70d28 70d27e61 7c
  Layout tentativo: VER(4B?)=01fb71b0 | NONCE(12B)=a200955b e7728a5b 4cf84a1f | TAG(16B)=9f80317d 48ce6436 1c61b6a3 | CT(36B)... O VER(1B)=01 NONCE=fb71b0a2 00955be7 728a5b52...
  Probar ambos órdenes (NONCE|TAG|CT y NONCE|CT|TAG).
- PLAN: (1) buscar ANCHOR/SEED/CYCLES por verificación CHK (sha256("a:s:c") dentro del archivo) — CORRIENDO bg; (2) implementar cadena en C para velocidad; (3) descifrar.

## Rocinate (60pts real, id 3fb2ceda-d5d3-4369-b887-2b18ff34a203)
- chall.py: N 2047b, a,b IMPRESOS. n=100. Zs = r_i*(s^c_i mod N) ENTERO (4083-4094 bits, NO reducido mod N).
- Cs aleatorios 2039-2047b, gcd(Cs)=1. Ts = r_i^e mod N. e=random.randint(1,N) (salvo instancia débil).
- Reducción: conocido r_0 + gcd(Cs)=1 → s = Π(Zs[i]·r_i^{-1})^{u_i} mod N (extended Euclid, no hace falta e).
- Ataque: Franklin-Reiter con e pequeño: gcd(x^e−Ts[i], (a·x+b)^e−Ts[i+1]) sobre Z/NZ → raíz r_i. Probar e=1..64.
- IMPLEMENTANDO test e pequeño.

## Just Give Me The Flag Man (60pts real, id 0c29db29-bbf3-4dd1-b07a-6e5f05db558f)
- chall.txt 48 tokens: 18 letra+dígito / 30 dígito+dígito. Letras {u,v,w,z,x}; segundos chars de letra ∈ {2,3,4,5,6}.
- Flavor: Saad, Harun, note, watching building since noon → claves candidatas SAADHARUN/HARUN/NOON.
- Pendiente: probar decodificaciones (checkerboard 5x10 / mapeo letra→dígito).
