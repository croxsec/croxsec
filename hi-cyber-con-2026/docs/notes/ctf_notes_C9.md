# C9 — Dormant Signer ✅ SOLVED (58 pts)

## Flag: hiCTF{layout_undead_borrowed_betrays}

## Método (parseo offline transactions.jsonl, sin RPC)
1. 380 txs legacy RLP. 4 despliegues: VoucherDesk, Notary, Authorizer1 (0x5EBb...8516EB), Authorizer2 (0xCaC5...d6327c).
2. Digest authorize = keccak(pad32(contract) ++ request_id ++ amount ++ pad32(recipient)) — VERIFICADO 17/17 en AUTH1.
3. **Nonce reuse** (mismo r, calldata distinto):
   - #92/#203 (misma paridad v=28): k=(z1-z2)/(s1-s2) → key1=0xc0ecef7b... (signer AUTH1=0x740a4DAf)
   - #137/#234 (paridad opuesta v=27/28): k=(z1-z2)/(s1+**s2**) → key2=0x45f8c18e... (signer AUTH2=0x4E4bCA7F)
   - Pares misma paridad + mismo calldata = RFC6979 dup (señuelos).
4. running_digest = cadena keccak de digests de authorize EXITOSOS (simular: relayer registrado + quota + request no usado + firma válida). AUTH2: 20 exitosos, 3 reverts (dups #187/#268/#366).
5. Liveness sig = RFC6979(key, keccak("custody-desk/authorizer/liveness/v1")), low-s.
6. escrow = blob_destroy ^ running_digest ^ keccak(keccak("custody-desk/authorizer/escrow/v1") ++ r ++ s ++ v)
7. AUTH2 (destroyed production) → "layout_undead_borrowed_betrays" = FLAG.
   AUTH1 (sealed) → "packed_frozen_shared_exposes" (señuelo, badFlag).

## Scripts: /tmp/{parse,sel,diff,sigs,brute,oracle,solve,escrow1,escrow2,collide,check18}_ds.py
