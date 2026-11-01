# CTF Notes - Agente C (web/pwn/blockchain)
Prioridad: web (Whisper 300, Orphaned Context 225) > pwn (Apex Engine 486) > blockchain

## Cold Beacon — SOLVED (flag verified, already on scoreboard by teammate)
- key: C0ldB34c0n::unl0ck::7a3f (24 bytes)
- flag: hiCTF{c0ld_b34c0n_cfg_uns34l3d_fr0m_th3_s4mpl3}
- Challenge id: 3aef51b5-1216-4919-b80d-d49c9f358977
- Reversing notes: Nim binary. Anti-debug reads /proc/self/status TracerPid (at 0x4042e6, bypassed by patching to xor eax,eax). 
  check1 (0x403cff): table of 23 constraints on key bytes (ops @0x406070, counts @0x406050, expected @0x405fa0, index-tbl @0x405fc0). ops: 0/3/5=XOR, 1/4=SUM mod256, 2=PROD mod256. Solved with z3 (2304 solutions).
  Key expansion (0x404119): X=SHA256(key24); tkey = SHA256(X||ctr0_be)||SHA256(X||ctr1_be)[0:15] (47 bytes). ctr appended as 4-byte BE at END.
  Final check (NOT expansion==blob1^blob2 as I first thought): decoded = blob2(0x405e40) XOR tkey; then SHA256(decoded_data) compared to blob1[0:32] (0x405e20). Match -> prints decoded = FLAG.
  Launcher trick to feed binary keys via argv: /tmp/ctf/C/launcher reads /tmp/key.bin (24B) and execv's target.
  Inner Engine (292 solves) appears to be the SAME binary/template — reuse this exact method!

## Obfuscated Flow (56pts, 434 solves) — IN PROGRESS, parked
- Binary: /tmp/ctfC/rev-obs-flow/challenge, stripped, ~18KB. Input: hiCTF{+40+} (47 chars).
- Success path @0x401a9a: decodes 98-byte flag from PRNG XOR table, hash djb2*31==0xb4f079c8, printf("%s").
- PRNG mixer @0x401f80 (8-round, 4 qword state). XOR table @0x4031a0 (98 bytes, HAVE IT).
- Static seed @0xe0(rsp) = MD5 consts (0x0123456789abcdef, 0xfedcba9876543210, 0x89abcdef01234567, 0x76543210fedcba98).
- PROBLEM: state machine XORs input-derived values into seed before decode → seed is path/input-dependent.
- Decode loop structure FULLY understood (can emulate in Python, see /tmp/ of_decode.py logic inline above).
- TO RESUME: either (a) reverse the 10-dword bignum math (0x4011be-0x4014f5) + state machine checks to solve input dwords, or (b) full emulation. Math uses __modti3 (128-bit mod 0x7fffffff / 0x3b9aca07 / 0xfffffffb).
- Key dispatch IDs: 0x3d087b16, 0x2f71a8d4(hardcoded!), 0x38a5f41c→decode, 0x19c45d80, 0x51e29f3a, 0x6b3e91f2, 0x43b7e025, 0x7e192d4b, 0x6eadbeef.
- Fail branches: 0x4015ab jne (eax!=0x43b7e025), 0x401759 je (ebp rounds out).

## Night Batch (56pts) — PARKED
- GnuCOBOL static binary. Validation @0x402f40: SHA256(key[0:18]) → 42 rounds SHA256+XOR CONST@0x44d0bf → SHA256 → compare 256-bit target.
- Success prints 42-byte flag buffer @0x90(rsp). Target: 2c146846b66a3fbd 181654efa527e488 6dbc8ff6323aeadb b0a680efaef6a08f (LE qwords).
- "account rejected" XOR-0x5a @file 0x4d0a0, printed by fail handler @0x402780.
- BUG?: esi=*(0x4600f0)=0 always at validation → always fails. Flag @0x4600f0 goes 0→1→0 during init.
- Key space 18 bytes, SHA256 chain one-way. Key NOT found in binary (searched XOR-0x5a, EBCDIC, all single-byte XOR).
- CONST XOR table: file 0x4d0bf, 42 bytes.
- Needs: either find key encoding trick, or patch length byte to force SHA256 chain, or discover alternative validation path.

## Whisper (web, 59pts) SOLVED
- NoSQLi en POST /api/token: {"client_id":"report-signer","client_secret":{"$ne":null}} -> token Bearer scope report:export
- Pero /internal/export exige firma HMAC, no bearer.
- Exfiltré el client_secret carácter a carácter con oráculo $regex: "^<known><ch>" (devuelve access_token si coincide). Secreto por-instancia (32 hex).
- string_to_sign REAL: "POST\n/internal/export\n\n<hex_sha256(body)>\n<X-Timestamp>\n<X-Nonce>" (newlines reales, sin espacios). HMAC-SHA256(key=secret_string).
- El error "signature mismatch" del server describe el formato; el de "replay protection" indica añadir X-Nonce como línea final.
- Flag: hiCTF{bl1nd_regex_3xfil_then_f0rge_the_cust0m_s1gner_ce494233d2}

## Dormant Signer — SOLVED (58pts)
- Flag: hiCTF{layout_undead_borrowed_betrays}
- Chain: 380 txs, 4 contracts (VoucherDesk, Notary, SEAL + CAC authorizers).
- CAC = production (destroyed tx352). trusted_signer CAC=0x4e4bca7f, SEAL=0x740a4daf.
- **BUG CLAVE**: los `to` de las txs NO llevan prefijo '0x' → mi digest keccak(authorizer||req||amt||recipient) cortaba el 1er byte. Con eso corregido:
  - Clave CAC = 0x45f8c18e... (nonce-reuse complementario tx137/tx234, r=5729d3f4). SEAL = 0xc0ecef7b... (direct tx92/tx203, r=f055ac5e). Verificadas.
  - Signer usa RFC6979 (21/23 CAC match); los 2/23 no-match son nonce-reuse (diferente r).
- Liveness = RFC6979(key, keccak256("custody-desk/authorizer/liveness/v1")) = (v=28, r=0x7923e0f0.., s=0x24372a37..). ecrecover verifica.
- mask = keccak256(ESCROW_DOMAIN || r || s || bytes1(v)), ESCROW_DOMAIN=keccak256("custody-desk/authorizer/escrow/v1")=0xe921d598...
- **escrow plaintext = masked_secret XOR mask** (masked_secret=slot14=0x10967cb7..; NO es blob^mask). Resultado: "layout_undead_borrowed_betrays"+00 00.
- Lección: verificar prefijos 0x en addresses; el runtime desplegado (2392B) difiere 1 byte del source y el layout de storage está desplazado (running_digest=slot15, masked_secret=slot14).
