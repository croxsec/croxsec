

## 🎯 PISTA DEL AGENTE ANTERIOR (D4) — LEER PRIMERO
**Echoes of a Forgotten Canvas = ZIP con ZipCrypto (cifrado tradicional).**
- bkcrack YA ESTÁ COMPILADO en /tmp (busca: find /tmp -name "bkcrack*" -type f)
- ZIP ya extraído por el anterior — localízalo en /tmp/ctfB o /tmp/ctf
- Ataque known-plaintext con header JPG: bytes \xff\xd8\xff\xe0\x00\x10JFIF (guarda 12 bytes en plano.bin)
- bkcrack -C reto.zip -c nombre_interno.jpg -p plano.bin → recupera claves (minutos)
- bkcrack -C reto.zip -c entrada -k claves -D salida.zip → descifra
- La flag está en la imagen (steg o texto visible). PRIORIDAD MÁXIMA: esto cierra en minutos.
