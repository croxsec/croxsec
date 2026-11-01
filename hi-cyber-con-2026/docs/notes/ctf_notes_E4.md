# CTF E4 — Notas (subagent ctf-E4-steg124)

## Estado 18:55 CST
- **Unremarable** (121 pts, 49 solves, id=a420f2c0-f41c-4761-96f0-9cbac0cfc41a): EN CURSO
- **Caesar's Burial**: NO EXISTE en este CTF. Verificado contra /tmp/ctfE/challs.json (68 retos). Intel de predecesor = stale/errónea. Reportado.

## Hechos confirmados (Unremarable)
- PNG 4725x3150 RGB8, chunks limpios (solo IHDR+300 IDAT+IEND), 0 bytes trailing
- Descripcion: "The file was recovered without any accompanying notes. Nothing about it was considered significant at the time."
- Decoy: R-LSB row-major offset 0 = `hiCTF{fake flag-> nahh_m4n_this_n0t_that_easy}` (344 px de fila 0)
- Variantes descartadas (2 gen. anteriores + esta sesión): datos tras IEND, zsteg, steghide, compresión embebida, XOR canales, bit-planes visuales, FFT/espectro, LSB interleaved RGB, col-major, reversed, BGR, par/impar, R/G/B bits 0-3
- stegpy: nada (bits 1,2,4)
- stegano 3.0: lsb (no length prefix valido), red (lectura cruda cielo = basura), lsbset manual con identity/triangular/log/fermat/mersenne (headers invalidos)
- Reverse image search: Bing = resultados genericos "rainforest/mountains", sin match exacto; Google Lens = CAPTCHA (IP datacenter bloqueada)
- Regiones oscuras (sombra) con sesgo LSB natural = falsos positivos, descartado

## En ejecución
- qr_sorted_rel.py: QR scan en 24 bit-planes (cv2) + tesseract OCR + sorted-steg + codificaciones relacionales (R>G, paridad R+G+B, etc.)

## Pendientes si nada de lo anterior
- RS/SPA proper (estimar tasa embedding por canal)
- Residuo gaussiano con umbral adaptativo por regiones
- Imagen original: host alternativo p/ Lens, o Yandex images
- Entropía R-LSB tras byte 44 vs G
- Ordenes de lectura exoticos: serpentina/boustrophedon, diagonales, espiral, Hilbert
- Region embebida localizada: solo cielo (zona suave) -> analizar LSB chi2 solo en pixeles de baja varianza local
