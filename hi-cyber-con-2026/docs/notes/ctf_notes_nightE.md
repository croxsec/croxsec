# CTF Night E — HI Cyber Con 2026 (modo aprendizaje post-CTF)
Equipo: CROX Sec (25 kills/1393 pts antes de esta tanda)
Fecha: 2026-11-01 23:58 GMT+8

## Estado general
- Submit API: cerrado ("The CTF has ended") pero instancer sigue vivo → modo aprendizaje, flags verificados localmente/vivo.
- Límite instancer: 2 instancias concurrentes por equipo.

## Cold Circuit (Reverse, 63-65pts) — ✅ RESUELTO (local)
- Binario `check`: 20 rondas ARX-like: por ronda: `x[j]+=T[r*16+j]`; `x=SBOX[x]`; `y[PERM[j]]=x[j]`.
- Tablas en .rodata: SBOX@0x2020, PERM@0x2120, T@0x2140 (320B), EXPECTED@0x2280.
- Anti-debug: ptrace → muta T[0]^=1 (resultado erróneo). Decoy: argc+c0 par/impar (primer char hex DEBE ser a-f/A-F si argc=1, si no exit 0x62).
- Inversión: de EXPECTED, rondas 19→0: unpermute (x[j]=y[PERM[j]]) → SBOX_INV → restar T.
- FLAG: hiCTF{6e305f6a7461675f6e65656465642121} ("n0_jtag_needed!!") — verificado: "Access granted." exit=0.
- API submit rechaza (CTF ended) — logueado igual.

## Ground Station (Hardware, 67-68pts) — 🔧 EN CURSO
- Firmware gsc-fw.bin (x86-64 stripped, 11KB) reversado completo.
- Algoritmo AUTH: ARX 12 rondas. Clave=KEY "GSC-7\x00\x01\x23" para image-sig; keystream LCG seed 0x1f2e3d4c.
- image-sig local = de8c1297 ✓ (match byte-exacto).
- 🔑 CLAVE DEL AUTH VIVO: response = access(keystream16(), nonce8) — el NONCE se usa como KEY y el vector fijo (keystream) como input. Confirmado: "OK access=engineer".
- Programa alterado: INTERLOCK_OK = (TANK_TEMP <= 145) — debe ser <= 45 (safety interlock).
- Watchdog: enabled=1, trigger=runtest, action=restore_backup, trusted_checksum = checksum del programa ALTERADO.
- Plan: PROG SET INTERLOCK_OK "(TANK_TEMP <= 45) AND (TANK_PSI <= 100)" → BACKUP SAVE (sincroniza trusted) → RUNTEST.
- Instancia expiró; reiniciando (gs_solve2.py). UA de urllib bloqueado por CF → usar UA curl.
