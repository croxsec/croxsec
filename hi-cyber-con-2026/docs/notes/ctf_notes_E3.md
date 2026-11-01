# CTF E3 — notas (steg + osint) — HI Cyber Con 2026
## Unremarable (a420f2c0, 121pts)
- [x] PNG limpio: IHDR + 303 IDAT + IEND, sin tEXt/zTXt/iTXt, sin datos tras IEND, CRCs OK
- [x] ZIP limpio: solo chall.png, UT extra fields, sin comentarios (overhead 3158B explicado)
- [x] LSB-R MSB-first row-major: FAKE flag @offset0 "hiCTF{fake flag-> nahh_m4n_this_n0t_that_easy}\x00" (376 bits)
- [x] Streams bit0/1/2 x R/G/B + RGB-interleave, BGR: solo coincidencias gzip al azar (fallan al descomprimir)
- [x] Entropía ventanas: ~0.5 uniforme, sin regiones anómalas
- [x] Filtros PNG: distribución natural (0:59,1:86,2:65,3:1861,4:1079) — sin mensaje
- [x] Sweep zlib/gzip en TODOS los streams LSB (row/col): sin descompresiones válidas
- [x] XOR streams canales: sin "hiCTF"
- [x] OCR tesseract sobre original + 9 bit-planes: nada
- [x] Heatmap LSB: sesgo solo explicable por contenido foto (cielo abajo-izq)
- [ ] high-pass ±1 texto sutil: PENDIENTE resultado tesseract
- Modelo de visión (image tool) aborta constantemente — sin inspección visual
- Sospecha: la flag real puede requerir VISIÓN de bit-planes o esquema no trivial (PRNG/subset)

## Low Tide Ledger (06ba5cf9, 69pts) — OSINT
- Development = Eko Atlantic (ciudad recuperada del Atlántico, Lagos)
- Torres Eko Pearl: Black, Aqua, Champagne, White, Indigo Pearl
- Falta: AGENCY (oficina inmobiliaria pequeña DENTRO del complejo) + ROOM (piso+letra)
- room.jpg = PNG 1246x832 RGBA, sofá cojín cebra+magenta, vistas oceánicas
- Flag: hiCTF{Development_City_Country_Agency_Room}

## Paper Trail (7001419c, 60pts) — pendiente revisitar

## Paper Trail (60 pts) — 19:55 GMT+8, sin solve aún
- chall.pdf = paper real JDFSL 12(1) Tobin et al. 2017. Texto visible IDÉNTICO al original (Glos eprints). Sin incremental updates.
- ANOMALÍA: 4 streams invisibles añadidos (obj 179-182, `3 Tr`, Tm 8 8, F1=CMUSerif size1) en 4 páginas. TJ arrays de strings VACÍOS + números de kerning: total 165 números.
- Kern values 1-250 no mapean a anchuras de ninguna fuente embebida (CMU min 277, Times min 250). Numerosas transform probadas (mod26, bytes, xor, diffs, cumsum, morse) → sin texto.
- Masthead 3594x871 LSB limpio; OCR limpio; pdftotext limpio; metadata Appligent estándar; XMP obj 2 sin revisar del todo.
- PENDIENTE: signs(+-) como bits por stream alineados; XMP obj 2; render p7-13 no inspeccionado visualmente (image tool caído); compare vs ERAU version original (no Glos).
- PIVOT → Unremarable (121 pts).

## Low Tide Ledger (69 pts) — sigo sin Agency+Room
- Development = Eko-Atlantic (reclaimed city). City=Lagos Country=Nigeria.
- Foto room.jpg (1246x832 PNG RGBA) sin metadatos ni placa visible → listing por mobiliario (sofá marrón, cojines magenta/cebra, sillas cuero caramelo, columna teal).
- Bloqueos: NPC/Hutbay/propertypro 403 CF; Common Crawl index 504; archive.org timeout; DDG lite rate-limit; Bing imágenes basura.
- ACCESIBLES: estateagentsng.com espejos por agencia (curl OK: emmavisio sí, micon 404) → revelan URLs CDN images.nigeriapropertycentre.com/properties/images/{id}/{hash}-{slug}.jpg (¡CDN 200 con URL real!).
- Agencias con listings Eko Pearl vistas: Tedhol Properties, Prince Ademola Osinuga, Micon Homes, Emma-visio, JOOSA, "Eko Pearl Towers Luxury Apartments".
