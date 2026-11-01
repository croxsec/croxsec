# CTF D1c — Reverse (Obfuscated Flow, Night Batch) + Warden's Maze cleanup
# Inicio: 17:31 CST 2026-11-01 | Quedan ~4.5h (fin 22:00 CST)
# Team CROX Sec: 21 kills/1160 pts

## IDs retos
- Obfuscated Flow: bbb7442a-7577-430e-a10e-e17dffffe581 (55-56pts, ~460 solves)
- Night Batch: 99ee0bc40-5ee5-4db7-823e-360c6ed98db6 (56pts, ~437 solves)
- Warden's Maze: 1a18e0db-e534-4694-b19c-c2307a094a7e (57pts, ~367 solves, misc)

## Estado heredado
- OBFL: C dejó ~80% reverso. Input 47B stdin "hiCTF{"+40+"}". 2 rutas de flag:
  0x401a9a (SipHash decrypt 98B de 0x4031a0, checksum djb2*31==0xb4f079c8) y
  0x401822 (SSE decrypt). Ruta SSE necesita b NO printable (descartada).
  Restricciones z3 parciales en notas C3. asm: /tmp/ctf_c3/obsflow.asm
- NB: GnuCOBOL. Path A (404bc0 digits-check + SHA chain) inwinnable por diseño.
  Path B via 0x4025c8 requiere [0x460180]==0 (error path con 40c290 ret -20/-10).
  H1: 411de0 en Path B rellena 0x4600e0 key-dependent.
- MAZE: bug int8 trunc fog CONFIRMADO. Exploit listo: /root/.openclaw/workspace/ctf/hic2026/B3/maze_exploit.py host port tls. Stand (14,4) -> corrupt (9,12) vault wall -> walk in. Local flag: hiCTF{warden_vault_cleared_e0466cc4} (seed local). SOLO FALTA instancia remota.
