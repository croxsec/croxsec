# CTF Night E2 — Titan Relay (pwn) + fallback Ground Station
Equipo: CROX Sec — modo aprendizaje post-CTF (submit cerrado, NO submitear)
Inicio: 2026-11-02 00:43 GMT+8

## Titan Relay (id e3ee5fb0-e4ec-4135-8751-128213da17cd, pwn, 65pts, 194 solves)
- Binario: Rust PE32+ x64 stripped (src/main.rs), 378 funcs. Menú: "route consensus vm".
- Opción 1 "load capsule": pide "Capsule length > " y "Capsule hex > ". Luego accepted/rejected.
- Strings clave: "[!] order rejected", "[!] route fault contained", "[+] capsule accepted", "[!] capsule rejected".
- Instancia: titan-relay-fc0470dad92a.chall.hiddeninvestigations.net:1337 (TLS, SNI=host). Deploy: PUT /api/v2/integrations/challs/{id}/instance con '{}' + Content-Type: application/json. ~20 min TTL, renovar PATCH cada 10 min.
- Flag real en /flag.txt del container (dummy local).
- night-E NO dejó solve de Titan (solo Ground Station + Cold Circuit). Análisis desde cero.

## Estado
- 00:46 instancia RUNNING. Menu visto. Análisis estático en curso.
