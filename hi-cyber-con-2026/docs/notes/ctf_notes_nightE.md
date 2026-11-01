# NOTAS NIGHT E — pwn/reverse/hardware
Inicio: 2026-11-01 23:58 CST
## Plan
1. Ground Station (Hardware 68) — SDR/radio
2. Cold Chain (Hardware 67) — IoT/sensores
3. Titan Relay (pwn 65) — bin remoto
4. Cold Circuit (Reverse 65) — key check
Regla: >12min atascado = siguiente

## 00:05 — INSTANCIAS VIVAS (PUT /api/v2/integrations/challs/{id}/instance)
- GS RUNNING: control=ground-station-control-service-5532ed08b758.chall.hiddeninvestigations.net:1337 (TLS SNI) | telem=ground-station-telemetry-feed-5532ed08b758.chall.hiddeninvestigations.net:1337
- Limite 2 concurrentes. TR pendiente (necesita slot).
- Cold Circuit = local only, sin instancia.
