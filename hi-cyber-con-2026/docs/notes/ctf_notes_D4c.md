# Notas D4c — Echoes / Dead Air / TESSERA

## 17:34 — Echoes of a Forgotten Canvas (59pts)
- ZIP descargado por D4: /tmp/ctf_D4/echoes.zip (sha OK)
- chall.png 4000x4000 RGBA. Tras IEND: ZIP embebido (3.3MB).
- inner.zip → carrier.jpg, ZipCrypto (flags 0x9), data descriptor, csize=3358907 usize=3364164.
- PNG chall.png: posible steg también, pero primero el ZIP.
- plano: JPEG header FF D8 FF E0 00 10 JFIF 00 01
- bkcrack lanzado PID en bkcrack.log
- Flag esperada en la imagen descifrada (strings/steghide/etc)
