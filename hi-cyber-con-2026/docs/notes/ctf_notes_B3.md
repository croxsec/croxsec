# CTF notes B3 (forensics/steg/misc ronda 3)
# Inicio: Sun Nov  1 09:35:22 AM CST 2026


## 2026-11-01 ~19:00 CST — Warden's Maze: EXPLOIT LOCAL COMPLETO
- BUG CONFIRMADO (reversing estatico): funcion fog 0x9680-0x98f4.
  Write de explored-mark: base=[rsp+0x58]=player_idx; offset = dx + W*dy (W=24),
  pero movsx rcx,cl @0x98a1 TRUNCA a int8. O=144 (dy=+6,dx=0) -> -112 ->
  escribe map[P_idx-112]. Valor: (tile_objetivo & 0x3f)|0x40.
- OBJETIVO T=(20,4)=' ' floor, LOS por col 4 despejada (rows 15-19 col 4 ok).
  P=(14,4): P_idx=340; 340-112=228=(9,12) MURO DEL VAULT '=' -> pasa a type 4 FLOOR.
- spawn REAL = (1,12) (no (1,13)). Row render indented 2 espacios (len 26; strip!).
- interior vault '-' y prize '*' son walkable (types 4/5; bloquean solo 1 y 3).
- LOCAL: hiCTF{warden_vault_cleared_e0466cc4} (FLAG_SEED=1234 local).
- exploit: /root/.openclaw/workspace/ctf/hic2026/B3/maze_exploit.py (host port tls)
- Pendiente: instancia REMOTA bloqueada (limite 2 instancias equipo, compañeros).
  Retry loop: /tmp/warden_instance_retry.sh -> /tmp/warden_instance.json
  Cuando llegue: python3 maze_exploit.py <host> <port> tls -> flag real -> submit.
