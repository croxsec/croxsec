# CTF E2 — Misc/OSINT — 2026-11-01

## Estado general
- Comp: HI Cyber Con 2026, termina 22:00 CST hoy. CROX Sec ~19 solves/1042 pts.
- Mis retos: Unremarable(124pt), Paper Trail(61pt), Low Tide Ledger(70pt). Caesar's Burial NO EXISTE en /challs (descartado).

## Low Tide Ledger (OSINT) — hipótesis Eko Pearl Towers, Eko Atlantic, Lagos, Nigeria
- Pistas: Atenas 2004 (reclamo ~2003-2008), dragado pre-Beijing 2008, UTC+1 sin DST, Bar Beach bajo los pies,
  "Great Wall of Lagos" de bloques ~5t. Torres "cinco gemas que nunca tocaron ostra" = Eko PEARL Towers
  (Black/White/Champagne/Indigo/Aqua Pearl). El complejo ES la "pearl" (oyster joke).
- Flag: hiCTF{Development_City_Country_Agency_Room}
  → Development=Eko Pearl Towers (?), City=Lagos, Country=Nigeria, Agency=?, Room=?
- room.jpg = foto de listing (sofá con cojín cebra + magenta, vistas oceánicas, sobreexpuesta).
  "Placa junto a la puerta" = número de habitación (piso+letra). Agencia = oficina PEQUEÑA dentro del complejo.
- TODO: encontrar listing exacto (mobiliario) → agencia + número de habitación.
  Buscar en nigeriapropertycentre.com, propertypro.ng, privateproperty.ng, estateagentsng.com, apartments.ng.

## Paper Trail (steg/pdf)
- chall.pdf = paper REAL "Forensic Analysis of Virtual Hard Drives" (JDFSL 12(1) 2017, DOI 10.15394/jdfsl.2017.1438)
  procesado por Prince 12.5 + Appligent AppendPDF Pro 6.3 (2019-12-03). 13 páginas (cover + 12).
- 4 streams de texto INVISIBLES (3 Tr) objs 179-182 pegados a páginas internas 52/61/72/86,
  arrays TJ con strings vacíos + números de kerning. brute_numbers.py → NADA con sentido (basura).
- Metadatos XMP limpios, ActualText=U+00A0, sin EmbeddedFiles/JS/OCG/AcroForm, un solo %%EOF.
- PLAN B (en curso): diff contra paper original. Wayback: web.archive.org/web/20231202062136/
  https://commons.erau.edu/cgi/viewcontent.cgi?article=1438&context=jdfsl (curl timeout anterior, reintentar).
- original.pdf 5.6KB = página de bloqueo Cloudflare, NO el PDF real.

## Unremarable (steg) — pendiente empezar
- chall.png 4725x3150 RGB 19.6MB. Sin datos tras IEND. Sin zsteg/stegseek.
- PLAN: análisis LSB propio con numpy (bitplanes por canal), buscar magics (PNG/JZ/hiCTF) en bitstreams.
- Solves: 47/124pts (el más caro de mis 3).

## Log
- 14:56 inicio. Descargados 3 retos, hashes ok.
- 15:21 ojo: /tmp/ctf_solves_E.log ya tiene SOLVE|Pruned Ledger (no es mío, otro escuadrón comparte el log?).
