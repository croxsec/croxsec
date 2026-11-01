# CTF HI Cyber Con 2026 — Frente C3 (Reverse fáciles) — NOTAS

## Estado global
- 3 objetivos: Epsilon Drift (55p,524), Obfuscated Flow (56p,434), Night Batch (56p,406)
- Binarios descargados en /tmp/ctf_c3/{epsilon-drift,rev-obs-flow,night-batch}/
- z3 OK 5.3.3 · gdb OK · sin ltrace · sin angr (no verificado)

================================================================
## NIGHT BATCH — GnuCOBOL 392KB, dinámico (libcob.so)
================================================================
Comportamiento: `./night-batch <key>` → "account rejected" (siempre, con cualquier key)
El string "account rejected\n" (17B) está XOR-0x5a en file 0x4d0a0 (vaddr 0x44d0a0).
Decode rutina: 0x402780 (loop XOR 0x5a, fwrite 17B a stdout).

### Flujo principal (crt0 GnuCOBOL)
- 0x4026c1 init: flag [0x4600f0] 0→1 (memcpy via 0x40df7c, caller 0x4026c6)
- 0x400b81: call 40f900(0x44ce30, 0x45e380) → validación libcob; RESET flag 1→0 (memcpy caller 0x400b86) — CON KEY INCORRECTA. ¿Con key correcta quizá NO resetea?
- 0x400bc2: call 402f40(edi=0x460140=key buf, esi=BYTE[0x4600f0])
  - esi==0 → call 402780 ("account rejected") → ret 0
  - esi!=0 → cadena SHA-256 (ver abajo)
- 0x400bce: cleanup rep stos 0x20×0x28 a 0x460140

### Cadena SHA-256 (función 4027e0 = SHA-256, IV estándar en 0x44d0f0/0x44d100: 6a09e667 bb67ae85 3c6ef372 a54ff53a / 510e527f 9b05688c 1f83d9ab 5be0cd19)
- D0 = SHA256(key18bytes @ 0x460140)  ; len hardcoded 0x12=18 en 0x402f52
- Loop r12d=0,1: Di = SHA256(D0‖bswap32(i), 36 bytes)  ; 0x24=36 en 0x402fad
  - digest_0 a rsp+0x90[0..31]: out[k]=T[0x44d0c0+k]^D0[k]  (tabla vaddr 0x44d0c0, file 0x4d0c0)
  - digest_1 a rsp+0x90[32..41]: out[32+k]=T[0x44d0e0+k... ]^D1[k]  (10 bytes, edi=32)
- final = SHA256(out42, 42) @ rsp+0x40
- cmp final[0:16] == {0x2c146846b66a3fbd, 0x181654efa527e488} (movabs 0x403057/0x403066)
- match → je 0x4030a1 (éxito, ret eax!=0) → caller 0x400bc9 call 40c470 (probable print flag)

### COBOL fields (.bss, descriptors en .data 0x45e2e0+)
- 0x45e320: {size=0x28(40), data=0x460140, attr=0x44ce90} — KEY BUFFER
- 0x45e380: {size=1, data=0x4600f0, attr=0x44cea0} — FLAG byte (gate del check)
- 0x45e360: {size=3, data=0x4600e0} · 0x45e2e0:{2,0x460120} · 0x45e300:{2,0x460130} · 0x45e340:{2,0x460170}
- NO hay key esperada en claro (.data sin texto, .bss=0). Key se verifica por SHA-chain o se computa.

### gdb realizados
- run AAAA×18: buffer 0x460140 = 18 A's + spaces (key copy OK), flag=[0] al check → fail inmediato
- watch 0x4600f0: 0→1 @init (caller 0x4026c6), 1→0 @0x400b86 (caller del 40f900 @0x400b81) — SIEMPRE llega 0 al check con key mala
- 40d7c0 (cob_cmp/cob_move) hits: {1,0x44cc74}vs{1,0x4600f0}(flag), stack temps vs {2,0x460120} y {0x28,0x460140}=KEY

### HIPÓTESIS aún por probar
1. 40f900 con key correcta NO resetea flag → check SHA-chain corre → success
2. La comparación real de la key está en el árbol 40f900→40d7c0 (cob_cmp sobre campo KEY)
3. SIGUIENTE PASO: gdb script traceando cob_cmp con campo KEY como operando, capturar el otro operando (key esperada) — o comparar flujo con key de 18B alfanumérica vs largas
4. Alternativa: el keylen real importa: ¿se aceptan keys != 18B? Probar `./night-batch` con key de 40 chars (buffer es 40B)

================================================================
## EPSILON DRIFT — ELF estático 1.2MB (pendiente, sin analizar aún)
================================================================
- Uso: ./epsilon-drift <hexvector> → "calibration residual out of band"
- Datos: .rodata 0x4e33a0+ (aleatorio), floats 0x4e3300
- strings "unlock" en ~0x124xxx (region libc estática)
- PENDIENTE TODO: buscar rutina de validación, formato del vector, algoritmo

================================================================
## OBFUSCATED FLOW — ELF 18KB estático (reversado ~80%)
================================================================
Archivo asm: /tmp/ctf_c3/obsflow.asm (1766 líneas, offsets 730-1766 PENDIENTE de leer)
- Input 47B: "hiCTF{" + 40 chars + "}"; strncmp("hiCTF{",6); '}' en offset 0x2e
- dwords d0..d9 en rsp+0x176..0x19a
- 0x4028f0 = __modti3 · 0x401f80 = SipHash (8 rounds sobre 4 qwords rsp+0xe0)
- M1=0x7fffffff m2=0xfffffffb P=0x3b9aca07
- Switch externo 0x401504: cmp eax,0x2f71a8d4 → siempre Falso (0x401b9d): 3^0x7ffffffe mod (2^31-1)=1 (Fermat)
  → selector := 0x6b3e91f2
- Tablas (6×32B, dword[0]=selector, [1..7]=decoys 0x0ddcba00..66):
  0x4030e0→6b3e91f2 · 0x403100→19c45d80 · 0x403120→43b7e025 · 0x403140→51e29f3a · 0x403160→3d087b16 · 0x403180→38a5f41c
- Primos 0x403080-0x4030d8: 2,3,5,7,11,13,17,19,23,29,31,37
- Datos cifrado flag: tabla 0x4031a0 (64B). MD5-ish 0x403210/0x403220/0x403230 (075bcd15, 0e42882f)
- Terminales: 0x7e192d4b (0x401e87 éxito sin print), 0x6eadbeef (0x401e14 deny)
- Contador 32 pasos (ebp=0x20)
- RUTA FLAG: selector 0x38a5f41c → 0x401a9a: descifra 98 bytes de 0x4031a0 con
  bits de estado SipHash evolutivo → buffer rsp+0x100; checksum (hash*31+byte)==0xb4f079c8
  → printf("%s", rsp+0x100) ← LA FLAG SALE AQUÍ
- Restricciones derivadas:
  s30==0 exige (d8+d9) mod M1 == 0x4770c967 AND (d8·d9) mod M1 == 0x2e97d196
  s48 = ((d0mod·d1mod) mod M1) ^ 0x37c0f52c == 0
  s38−s40 == 0x1e054920 (s40=((d1mod²)·0x7a69) mod M1)
  stage-1: s18=d3mod, s20=d9, s28=d8, s50=d0, s5c=d1, s68=d8, s78=d4 mod 0x7ffffffe, s7c=d5 mod 0x7ffffffe
- PENDIENTE: leer obsflow.asm offsets 730-1766 (rutas 0x40176a, 0x4017db, 0x401949,
  0x401a9a completa, helpers 0x402010 y 0x402220). Extraer restricciones por dword,
  resolver con z3 → construir input 47B → flag por printf.

================================================================
## PLAN
1. [AHORA] Epsilon Drift (más resuelto, probablemente algoritmo limpio)
2. [DESPUÉS] Obfuscated Flow: terminar de leer asm, z3, flag
3. [SI CABE] Night Batch: gdb trace cob_cmp para key esperada, o invertir SHA-chain

---
## NIGHT BATCH — deep dive dinámico (gdb) — 2026-11-01 ~06:30
- **Check 1 (404bc0)**: key de 18 bytes debe ser TODOS dígitos ASCII 0-9 (loop: cada byte -0x30 <=9).
- **Char loop** (0x400c97-0x400d01, counter w120=1..18): cob_move copia cada key[i]→tabla[0x4600ff+i] (tabla placeholder inicial 0x0f×18).
- **Post-loop 94-check** (0x400d84-0x400d9a): call 411de0 → call 413920 → test → jne 400b77 (fail).
  - Campo 0x45e360={size3, data:0x4600e0, attr:0x44ce60}. Data={00 00 0f}.
  - **KEY-INDEPENDIENTE**: mismo valor (0x000f0000) con keys 012345678901234567 y 999999999999999999.
  - Única escritura: 0x41136f (dentro de 4113c0, llamado justo antes del check) → 0x000f0000.
  - 413920 retorna 0xffffffff (≠0) → FAIL siempre. **Path A es inwinnable por diseño.**
- **Path B (0x4025c8)**: ÚNICA vía al éxito. je 0x400b3e→4025c8 requiere [0x460180]==0.
  - [0x460180]=1 (init 0x4026fd). Error path (0x400ae3) lo pone a 0.
  - Error path requiere que 40c290 (call al inicio de 0x400a80, args edi=0x460178,esi=rsp+0x120) retorne -20(0xffffffec) o -10(0xfffffff6).
  - Path B: 4×41df30(0x2b=43B) + 41e530(0x44cd30) + 4113c0 + 411de0(0x45e360,0) + 413920(0x45e360, 0x5e=94).
  - je 0x4025bd→400b86 (SALTA el reset del flag; flag≠0 → SHA chain corre → éxito).
  - jmp 0x4025c3→400b77 (fail).
  - **HIPÓTESIS**: 411de0 EN PATH B rellena 0x4600e0 desde la key de forma key-DEPENDIENTE (en Path A no lo hace).
  - PENDIENTE: tracear 0x400a80 callers + args; ver si 40c290 puede retornar -20/-10 con input especial (¿argv vacío? ¿arg count?); ver args exactos de 4113c0/411de0 en Path B.
- **Flujos confirmados (traza nb17, key 18 dígitos)**: ENTER(w170=1,flag=1) → 404bc0=1 → char loop i=1..18 → 0x400b77(flag pre-reset=1) → 40f900 reset flag→0 → esi=0 → 402f40 gate fail → FAILPRINT("account rejected") → exit.
- **El flag byte 0x4600f0 es reseteado por 0x400b77→40f900('0'→flag) SIEMPRE** que se entra por esa ruta. El salto 0x4025bd→0x400b86 lo EVITA.

---

## Obfuscated Flow (56pts, 434 solves) — ANÁLISIS PROFUNDO (sin flag)

### Binario
- `/tmp/ctf_c3/rev-obs-flow/challenge` (18440 bytes, stripped ELF x86-64)
- Disasm: `/tmp/ctf_c3/obsflow.asm`
- Input: stdin, formato `hiCTF{` + 40 chars body + `}` = 47 chars total
- Validación: length==0x2e, strncmp "hiCTF{" (6), byte[46]='}'

### Estructura del control flow
1. **Selector computation** (0x4011da-0x4014ed): carga dword0-dword9 del body, modmuls mod (2^31-1), computa valores salvados
2. **Primer dispatch** (0x401504-0x40152d): cmp eax con {0x3d087b16→0x40176a, ja 0x401590, 0x2f71a8d4→0x401b9d, 0x38a5f41c→0x401a9a(FLAG), 0x19c45d80→0x401822}
3. **Segundo dispatch** (0x401740): cmp eax con {0x7e192d4b→exit, 0x6eadbeef→exit, 0x3d087b16→0x40176a, sino→back}
4. **Loop**: ebp=32 iteraciones max, cada iteración modifica el estado (XOR + SipHash) y computa nuevo selector
5. **Estado**: 4 qwords en [rsp+0xe0], inicializado de constantes 0x403210/0x403220

### Tablas
- **Table1** @0x403100 (8 entradas, usada en 0x401738): [0]=0x19c45d80 [1]=0x11badc0d [2]=0x22badc0d ... [7]=0x00badc0d
- **Table2** @0x403180 (usada en 0x4017cf): [0]=0x38a5f41c ← FLAG SELECTOR
- **Mod-exp table** @0x4030e0: [0]=0x6b3e91f2 [1]=0x00badc0d

### Rutinas de flag
1. **0x401a9a** (SipHash decrypt): dead code natural — el selector 0x38a5f41c NO está en Table1. Solo alcanzable vía Table2[0] → 0x4017cf → 0x401740 → 0x401510 → 0x40151d. SipHash 8 rounds × 4 blocks, XOR ciphertext@0x4031a0 (98B), checksum h=h*31+b, cmp 0xb4f079c8, printf("%s")
2. **0x401822** (SSE decrypt): alcanzable vía Table1[0]=0x19c45d80 → 0x40152d. Usa xmm0=constantes@0x403230 (incluye 123456789=0x075bcd15), [rsp+0x10], [rsp+0x18], itera 1337 veces (0x539), shr r15,1. Checksum idéntico 0xb4f079c8 → printf.

### Condiciones para flag path (0x401822)
- Selector en 2º dispatch = Table1[0]=0x19c45d80 → necesita (r9 | [rsp+0x48]) == 0
- [rsp+0x48] = P ^ 0x37c0f52c donde P = (dword0_mod × dword1_mod) mod (2^31-1)
- Para [rsp+0x48]=0: P = 0x37c0f52c → dword1 = 0x37c0f52c × dword0^(-1) mod M
- r9 = (P-Q) ^ 0x1e054920 [si P≥Q] o (M-(Q-P)) ^ 0x1e054920 [si P<Q]
- Para r9=0 con P≥Q: Q = P - 0x1e054920 = 0x19bbac0c
- Q = ((dword1_mod² mod M) × 31337) mod M
- Resolviendo: b² × 31337 ≡ 0x19bbac0c (mod M) → b = 0x268ad444 o 0x59752bbb (ambos NO PRINTABLE)
- **CONCLUSIÓN**: No hay solución printable analítica para 0x401822

### Para flag path (0x401a9a vía 0x40176a)
- Necesita selector 0x3d087b16 en 2º dispatch → va a 0x40176a
- 0x40176a: modifica estado, SipHash, eax=Table2[0]=0x38a5f41c → 2º dispatch → 1º dispatch → flag
- Pero 0x3d087b16 tampoco está en Table1 — debe venir de otro state mod path
- **PENDIENTE**: mapear TODOS los paths state mod (0x40181d, 0x401d3a, 0x401d73) para ver cuál produce 0x3d087b16

### Datos clave
- Ciphertext 98B @0x4031a0: `9ac3f795bcc3096f309d6717f01d294b588269521feb7fbb979c9198b7f805a2880635e0c541b28ea7f9af8f64b626284be6c4f265293d97697b9bd966b7913ab69cc6c3adb277a6ab6c65e12eb9a09b76d6ff68d105421f62c31796655b60bfb448`
- Checksum target: 0xb4f079c8
- XOR state const: 0x1e054920
- Constants SSE: 0x075bcd15, 0x0e42882f, 0x4c3b031b01, 0xffffdde000000008
- M = 2^31-1 = 2147483647 (primo)
