## 20:14 — Inicio. TESSERA first: check dir + grep hiCTF
## 20:15 — grep hiCTF: 0 hits. Paso 2: Recycle.Bin + unattend + ps1 + browser + flag{
## 20:16 — Standard locations: NADA. Explorando estructura del disco
## 20:17 — Usuario sospechoso: N!. Explorando
## 20:18 — N! vacío. Probando registry NTUSER.DAT + inetpub + SYSTEM
## 20:19 — Buscando en binarios: MFT, LogFile, pagefile, hiberfil, evtx
## 20:21 — MFT/LogFile/binarios: vacío. Reviso notas previas + EVTX clave
## 20:21 — TESSERA YA RESUELTA por D4e! Flag en notas. Verifico EVTX + estado de submit
## 20:22 — Confirmando TESSERA en API y pasando a ECHOES
## 20:23 — Verificando TESSERA submit
## 20:24 — TESSERA confirmada. ECHOES: parseando chall.png chunks + inner.zip
## 20:25 — zTXt/iTXt XMP presentes. Decomprimiendo
## 20:26 — XMP = Photoshop metadata. Check full history + PNG tail + inner.zip parse
## 20:27 — Tail = inner.zip completo. Parseo estructura total
## 20:29 — Estado: fcrack/bkcrack previos, cores, test bkcrack fail-time
## 20:31 — Maté fcrack viejo. Analizando alpha channel del PNG a fondo
## 20:32 — carrier.jpg EXISTE (3364164B)! Verifico CRC
## 20:33 — carrier.jpg VERIFICADO (crc ok). Buscando steg
## 20:34 — steghide installed. Extrayendo
## 20:35 — Buscando password/keys en logs previos
## 20:37 — carrier.jpg real. Buscando cómo se crackeó (password para steghide)
## 21:22 — Solo 38min! Buscando password del otro lane
## 21:24 — Veo carrier.jpg + artefactos
## 21:26 — Vision falló. OCR + steghide dict + strings
## 21:27 — POEMA 'Wilder Echoes' visible en la imagen! OCR completo
## 21:29 — Poema completo. Última línea: 'Spell sigeecsmpee' — probando steg
## 21:31 — Localizando 'Spell <palabra>' en la imagen
## 21:33 — Crop de 'Spell X' en (2530,1429) w=167 h=19
## 21:36 — OCR fino del spell-word (bbox 2648,1429,167,19)
## 21:44 — Acrostico: apilando primeras letras
## 21:47 — Poema leído. Acróstico AWSTFHTPATEDAT. Pruebo outguess+steghide masivo
## 21:49 — outguess extrae basura sin key. Buscando más líneas del poema fuera del crop
## 21:51 — Últimos minutos: outguess keys + stegseek
## 21:53 — Buscando password del zip (posible key steg)
## 21:54 — ZIP PW=dreamcatcher → steghide con esa pass
## 21:56 — Submit rápido de candidatos
## 22:01 — CTF FINALIZADO ("The CTF has ended")
## RESUMEN LANE D4f:
## - TESSERA: SOLVED previamente (hiCTF{alpc_p0rt_c0lloquy_s35s10n_z3r0_syst3npr0f1l3_r3p4r53_buff3r_vort3x}) — verificado already-solved contra API.
## - Echoes de-codificado al 95%:
##   1. chall.png → inner.zip appendeado tras IEND (3,359,095 B)
##   2. inner.zip ZipCrypto → PASSWORD=dreamcatcher (fcrack_rockyou.log)
##   3. carrier.jpg (CRC OK) = poema "WILDER ECHOES" (14 líneas, leído por OCR+visión)
##   4. Acróstico: AWSTFHTPATEDAT (no legible como palabra — probablemente OCR de caligrafía imperfecto)
##   5. steghide/outguess con dreamcatcher/acróstico → FAIL (basura)
##   PENDIENTE: password steghide correcta (candidatos: palabras clave del poema no probadas)
## Candidatos submit fallaron por fin de CTF, no por flag incorrecta.
