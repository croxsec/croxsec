# CTF Notes D4e — Echoes of a Forgotten Canvas + TESSERA
## Timestamp: 2026-11-01 ~18:50 CST

## Echoes of a Forgotten Canvas (59pts)

### Chain
- echoes.zip → chall.png (8.7MB, 4000×4000 RGBA) — NOT encrypted
- chall.png alpha channel → embedded.zip (= inner.zip, 3.36MB) — DONE by prior agent
- inner.zip → carrier.jpg (3364164 bytes) — ZipCrypto encrypted ← STUCK HERE
- carrier.jpg → ??? → flag

### inner.zip / ZipCrypto analysis
- Method: Deflate (8), flags 0x9 (encrypted + data descriptor)
- carrier.jpg: csize=3358907, usize=3364164, CRC=4230eebb
- Compression ratio: 99.84% (typical for JPEG — headers compress, scan data doesn't)
- Info-ZIP 3.0 encoding software
- Data starts at file offset 69 (30 hdr + 11 name + 28 extra)
- First 12 bytes: encryption header (random + check byte)
- Deflate data starts at offset 12 within encrypted stream

### bkcrack attempts (all FAILED)
- Lane A: 7 JPEG header variants @ offset 5 (stored-block assumption)
  - jfif_v101, jfif_72dpi, jfif_v100, jfif_cm, adobe, dqt, png — ALL FAILED
- Lane B: EXIF variants @ offset 11 — never ran (killed)
- REASON FOR FAILURE: zlib uses DYNAMIC HUFFMAN (BTYPE=2) for first block even on JPEGs.
  The first bytes of deflate stream are huffman-coded, NOT raw JPEG header.
  Known-plaintext guesses of JPEG headers are USELESS at any offset near the start.

### Current attempts
- fcrackzip dictionary (custom + john password.lst) — RUNNING
- fcrackzip brute force lowercase 1-8 — RUNNING
- bkcrack -o semantics: offset relative to ciphertext WITHOUT 12-byte encryption header

### TODO / ideas
- [ ] If fcrackzip fails: try bkcrack with plaintext from END of stream (stored blocks)
- [ ] Try bkcrack -x with scattered known plaintext (stored block headers)
- [ ] Analyze chall.png deeper (zsteg-style on alpha)
- [ ] Check if more data hidden in PNG beyond embedded.zip
- [ ] Try john jumbo zip format if available

## TESSERA (63pts)
- 1GB zip, stored (no compression), 13293 entries
- Windows disk forensics: evidence/ directory with full Windows FS
- $Recycle.Bin, ProgramData, inetpub, PerfLogs, Crypto keys, etc.
- Extraction to /tmp/ctf_D4/tessera_x/ — RUNNING
- TODO: search for flags, documents, browser data, user files

## TESSERA — SOLVED (62pts) ✅
- Flag: hiCTF{alpc_p0rt_c0lloquy_s35s10n_z3r0_syst3npr0f1l3_r3p4r53_buff3r_vort3x}
- Source: PowerShell ScriptBlock logging in Microsoft-Windows-PowerShell%4Operational.evtx
- 3 stages: ALPC ETW trace (XOR 0x5A), DPAPI vault in Session 0, NTFS reparse buffer injection
- Reconstructed from 3 PowerShell script blocks found via strings -e l on EVTX

## Echoes of a Forgotten Canvas — IN PROGRESS
