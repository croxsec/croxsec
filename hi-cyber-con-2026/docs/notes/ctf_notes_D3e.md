# CTF Notes D3e — 2026-11-01 ~19:40 CST (quedan ~2.5h)

## Estado del equipo: 22 kills / 1216 pts (#118)

## ChronoGrind (58 pts, id 61784143-ff04-444c-868d-faa4c53939e5)

### Parseo confirmado de state.dat (1358B total, magic CGD1, resto XOR 0x6c)
- dec = data[4:] XOR 0x6c, len 1354
- Header dec[0:0x14]: " l!,   TEAM.TESTRUN1" (artifact del test run del autor)
- Marcador de registros: "#!  " (0x23 0x21 0x20 0x20)
- R1 = dec[0x18:0x118] (256B) + trailer u32LE = 42794175
- R2 = dec[0x120:0x261] (321B) + trailer u32LE = 1175340878
  - Cola de R2 contiene ASCII: "THE\x00ANCHOR\x00HOLDS\x0e\x00KEEP\x00GRINDING\x0eF"
  - y digitos en charset propio (0x1N='N'): "9000000000" (posibles CYCLES = 9e9!)
- R3 = dec[0x269:0x36a] (257B) + trailer u32LE = 2673290950
- dec[0x36e:0x372] gap 4B
- R4 notas = dec[0x372:0x531] (447B) + trailer "5   " + 21 bytes extra dec[0x535:0x54a]

### Notas decodificadas (charset: 0x1N=digito N, 0x00=|, 0x07='(', 0x08=')', 0x0c=',')
- ANCHOR = REC{11} BASE241 / SEED = REC{22} BASE241 / CYCLES = REC{33} DECIMAL
- CHK = REC{44} = SHA256("ANCHOR:SEED:CYCLES" decimal colon-sep) — **NO esta almacenado en ningun archivo** (16k tests, 0 hits)
- DERIVATION: V = SEED; REPEAT CYCLES TIMES: V = V*V MOD ANCHOR
- K = SHA256(V AS 256-BYTE BIG-ENDIAN)  <-- OJO: dice 256-BYTE no 256-bit
- MSG CONTAINER cgfx: MAGIC(4) VER(1) NONCE(12) TAG(16) CT(rest)
- AEAD = CHACHA20-POLY1305, FLAG = AEAD-DECRYPT(K,NONCE,CT), TAG MUST VERIFY

### Decodificaciones base-241 (digito = byte-0x10)
- sub10 (para en byte<0x10): R1→5 digitos (39b) big=312553056933 lit=143379026853; R2→6 digitos big=19503092000624 lit=126865977722384
- sub10_skip (salta bytes<0x10): R1→242 digitos (1914b), R2→299 digitos (2363b)
- raw (byte=digito): INVALIDO para base-241 (bytes >= 241)

### Factorizaciones
- A s10_big = 3·3·13·67·1093·36479, λ=16852836
- A s10_lit = 3·4289·11143159, λ=23890930752
- A skip_big (1914b) = 167 × N(1907b compuesto NO primo)

### TODO PROBADO Y FALLADO (~96 combos de cadena × 8 formas de K × 3 AAD × 2 layouts):
1. Cadena corta (A sub10 4 endian combos) × C ∈ {42794175, 1175340878, 2673290950} × K∈{sha256(V32BE),sha256(V256B),sha256(V8BE),sha256(Vhex),sha256(Vdec),raw32,raw256,rawV8pad} → 0 hits
2. λ-trick (A corto factorizado, C∈trailers±3 + 9e9, S∈4 variantes, swap A/S) × 5 K × 2 layouts × 4 AAD → 0 hits
3. Kitchen sink: 108 claves (passphrases TEAM.TESTRUN1, CGD1, THE ANCHOR HOLDS..., sha256(R1/R2/R3/notes/...), raw bytes) × {ChaCha-Poly std/ver-shift, XChaCha20, ChaCha20 raw, Salsa20} → 0 hits
4. Primality trick: ningun A (corto o largo) es primo
5. Trailers NO son CRC32/adler32 de los records

### EN CURSO (background):
- /tmp/cg_bigchain.py 42794175: cadena big-A (skip_big 1914b) × 4 S variants, C=42.7M (~85s c/u) → log /tmp/cg_bigchain_42M.log
- /tmp/cg_bigchain.py 2673290950: misma cadena con C=2.67e9 (~2h, puede no terminar) → /tmp/cg_bigchain_2673M.log
- Si HIT: flag en /tmp/cg_FLAG.txt → submit!

### Pendiente si falla todo:
- C=9000000000 (9e9 del arte) con big-A = 5h de cadena — NO cabe en tiempo
- Re-verificar si decodificacion base-241 correcta (endianness por digito? digitos de 2 bytes?)
- Re-verificar charset de las notas (el 0x0a entre "V|=|V<0a>V|MOD" podria ser '+' u otro operador, no '×')

## JGMTFM (60 pts, id 0c29db29-bbf3-4dd1-b07a-6e5f05db558f)
- 52 tokens, 35 simbolos distintos, 18 tokens letra (u,v,w,x,z) + 34 digito
- Crib FORZADO: 53=h (solo pos1), 74=i (solo pos2), u3=C (pos3,18,37), 17=T (solo pos4), 35=F (solo pos5), x3={ (pos6,38)
- x2 ×4 (pos 7,22,40,52) — candidato a '}' pero genera llaves desbalanceadas
- Tokens letra en pos: 3,6,7,12,14,16,21,22,24,27,28,30,36,38,40,44,50,52
- Clues: Saad, Harun, note, noon → palabras probables: SAAD/HARUN/NOON/BUILDING/WATCHING
- Annealing con tetragrams (built from /usr/share/common-licenses): 12 restarts, score ~438 = basura. NO converge → hipotesis monoalfabetica cuestionable
- PENDIENTE: probar que x3 (pos38) NO es '{' sino otra letra; probar sustitucion HOMOFONICA (letra→multiple simbolos); probar que tokens digito forman bigramas de letras (ej: 53='h' donde 5=fila,3=col en cuadrícula)
- Scripts: /tmp/jg_crack.py (annealing), /tmp/tetra_table.json

## Rocinate (60 pts, id 3fb2ceda-d5d3-4369-b887-2b18ff34a203)
- Datos: /tmp/ctfA/rocinate/data.pkl, rlib
- Predecesor (D3d): solve_block0 recupera cola sembrada bien, region [0,128) 100% mal
- Franklin-Reiter: para e ∈ {65537,3,5,7,17,257, e=1..64}: gcd_Z/NZ(x^e−Ts[i], (a·x+b)^e−Ts[i+1]) con gmpy2
- Scripts previos: /tmp/ctf_D3c/rocinate_v2.py (--synth valida W via twist), unit_solveb0.py
- PENDIENTE: arreglar region [0,128) del MT19937, recuperar estado, atacar RSA/LCG

## API
- POST https://ctf.hiddeninvestigations.net/api/v1/challs/{id}/submit {"flag":"hiCTF{...}"}
- Bearer LNQF0OoRX_MGy73HnleSyaU4IH0vWBbj7RtQuO01w5mCvwtkKiEZTD0uE7fGNkUQDs6kc7M7HCuTdhKTcHpoS5aKwkIZYK7U78y7EcUdhIRi4deWVcBQ-kLbpdu3
- 1-2s entre intentos
- Aciertos: echo "SOLVE|<nombre>|<puntos>|<flag>" >> /tmp/ctf_solves_A.log
