# CTF D1e — Reverse (Night Batch + Obfuscated Flow)
# Inicio: 18:19 CST 2026-11-01 | Quedan ~3.8h (fin 22:00 CST)
# Team CROX Sec: 22 kills/1216 pts (#118)

## IDs retos
- Night Batch: 99ee0bc40-5ee5-4db7-823e-360c6ed98db6 (56pts)
- Obfuscated Flow: bbb7442a-7577-430e-a10e-e17dffffe581 (55-56pts)

## Night Batch — DESCUBRIMIENTO CLAVE (18:22)
- **Path B SE ALCANZA automáticamente con input de 18 dígitos!**
- [0x460180] YA es 0 cuando 0x400a70 se llama desde main
- Flujo: 0x400a70(edi=0) → 40c290 ret 0 → [0x460180]==0 → je 4025c8 → PATH B
- PERO: check en 0x4025bb falla (eax≠0 de 413920) → jmp 400b77 (FAIL)
- Segunda llamada a 400a70 con edi=-20 (0xffffffec) al final (cleanup?)
- **LO QUE FALTA**: hacer que 413920(0x45e360, 0x5e) retorne 0
  - 411de0 se llama justo antes (0x4025a7) — debe rellenar 0x4600e0
  - 0x45e360 = {size=3, data=0x4600e0}
  - 0x5e = 94
- SIGUIENTE: gdb trace de 411de0 y 413920 en Path B, ver contenido de 0x4600e0

## D1e (18:19+) — Night Batch: Extracción completa de checks
- 23 checks totales en el post-success path (0x400bce → ...)
- Valores esperados: 8,3,1,7,7,7,9,2,7,6,2,3,2,2,5,5,1,9,4,4,4,0 (último ==94 es Path B alternativo)
- Operaciones: MUL (t[i]*t[j]), ADD (t[i]+t[j]+t[k]), weighted sums (K1*t[i]+K3*t[j]+K2*t[k]+...)
- Constantes K1=1, K2=2, K3=3 (bytes ASCII '1','2','3' en 0x44cc74, 0x44a7e2, 0x44a7ea)
- Aritmética es modular (mod 10) — t[4]+t[5]+t[9]=15 se almacena como 5
- Path A (SHA chain) sigue siendo invencible — la flag se imprime por otro lado
- Estrategia: hill climbing con fitness = número de checks superados
- Script: /tmp/ctf_c3/hillclimb2.py

## ✅ NIGHT BATCH SOLVED (56 pts)
- Flag: hiCTF{c0b0l_p4ck3d_d3c1mal_n1ghtly_b4tch!}
- Key: 481702596318740925 (18 dígitos, argv[1] — NOT stdin!)
- Método: z3 solver con 22 ecuaciones mod 10
  - MUL checks también son mod 10 (t2*t11≡8, t2*t10≡4)
  - ADD/weighted checks mod 10
  - 23 checks totales extraídos via gdb trace de 41df30/413920
- Lección: el programa lee argv[1], NO stdin (echo | ./binary = "account rejected")
- z3 encontró exactamente 1 solución
