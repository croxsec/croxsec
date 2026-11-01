

## Operación Chimera — hallazgo parcial (night-D2, squads ya cerrados por orden de Pim)
- PCAP 26s/159k paquetes. Credenciales FTP: `backup_agent / Backup2026!` en `files01.corp.internal` — solo login, sin transferencia.
- El flag probable: tráfico DNS (exfil por subdominios) o a 10.142.18.55:8080. Pendiente de extraer.
- Réplica de ataque si se reabre: tshark -Y "ftp || dns || tcp.port==8080" + reconstruir objetos HTTP.
