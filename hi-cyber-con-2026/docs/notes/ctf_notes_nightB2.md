# CTF Night B2 — Cairn (crypto) + Hall of Mirrors (steg)
Inicio: 2026-11-02 00:27 CST (post-competición, modo aprendizaje)
Estado API: CERRADA (no submit). Solo documentar flags.

## Plan
- [ ] Cairn: leer challenge files + gfpoly.c + test_lib.py. Isogeny walk 2^20 pasos.
- [ ] Hall of Mirrors: localizar archivos (zip / imagen). Stego por simetría/espejo.

## Log

## 00:40 — Estado
### Cairn (crypto 74)
- Spec RULES.md leído. Caminata determinista 2^20 pasos en GF(p^2) (p=secp256k1, p=3 mod4).
- Por paso: SHA256(ser(j)||BE8(i)||salt) -> l=L[h0%4] -> f(Y)=Phi_l(j,Y) -> parte squarefree
  -> TODAS las raíces en GF(p^2) (garantizado: x^(p^2)-x == 0 mod f_sq) -> j = r[h1 % n].
- Final: key=SHA256(ser(j_T)||"IsogenyLabyrinth"), AES-256-GCM decrypt.
- Predecessor dejó libgfpoly.so (SOLO GF(p), no GF(p^2)) + test_lib.py pasado.
- Prototipo python /tmp/cairn2/proto.py corriendo (300 pasos) para medir deg f_sq dist + timing.
- Optimización clave identificada: x^(p^2) mod f = composición de Frobenius (x^p mod f via powmod 256-bit,
  luego compose con conjugado) ~50x más barato que powmod 512-bit genérico.
- TODO: implementar walk completo en C (2 cores). Estimación python ~ms/step -> C ~5-15ms/step -> 1.5-4h.

### Hall of Mirrors (steg 73->500 decay, 134 solves)
- datasheet = especificación COMPLETA (MirrorStego v1):
  low_byte(S[i]) de int16 stereo 48kHz (data chunk 299,520,000 B, 149,760,000 samples, 1560s).
  SplitMix64(K): por bit: p += 1+(draw1%4096); w=(draw2>>17)&0xFF; bit=popcount(low[p]^w)&1, MSB-first.
  Frame: "MIRRORS1"|len u32 LE|crc32|payload. Payload = imagen MVM1 (VM con ISA propio) o TLV ECC+sellado.
- K desconocida. K obvias (0,1,fnv,sha-derived,MIRRORS1) NO funcionan.
- Estructura audio: autocorr -> unidades 2s (lag20), 24.2s (lag242), 243.7s (lag2437). "Espejos" anidados.
- Envelope no es palíndromo; dist a mediana sin outlier único grosero.
- Cracker C lanzado en bg: rango [2^24,2^32), ~11min. low.bin=149MB uint8 mapeado.
- TODO: espectrograma completo (spec_full.png) para localizar anomalía ("solo una apunta fuera") = posición = K.
