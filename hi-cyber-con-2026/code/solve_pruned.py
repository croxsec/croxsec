#!/usr/bin/env python3
from eth_utils import keccak

LEDGER = bytes.fromhex('68fb8760b1353f7349c431442d6e97ab61685ee7')
CALLER = bytes.fromhex('123332679fb9643cb4302de5dc8f7efba76d060f')
OPERATOR = bytes.fromhex('f22107168ea80e90c1a999cb742631cb29e074ec')

ARCHIVE_DOMAIN = b"hictf.pruned-ledger.archive"
SEAL_DOMAIN = keccak(text="hictf.pruned-ledger.seal")
NOTE_DOMAIN = keccak(text="hictf.pruned-ledger.note")

maskedNote = bytes.fromhex('a147d1efc85c723feead12eb8a48e766e083186ab46823065042d324299e5469')
maskedEntry = bytes.fromhex('ee03bc4124b54991dd9611dd6ce6a40a903331af04c894853c88a73f63dd646a')
record = bytes.fromhex('63616c6c64617461' + '00'*24)  # "calldata" padded
unlockHash = bytes.fromhex('e961e38a534b301c99c15d1de4d8140b6baea08ed62b4c2ae4911a3a2d7877c1')

def trim(w):
    return w.split(b'\x00')[0]

print("== NOTE for unlock caller 0x1233... ==")
mask = keccak(NOTE_DOMAIN + LEDGER + CALLER)
note_word = bytes(a ^ b for a, b in zip(maskedNote, mask))
print(" note_word:", note_word.hex())
print(" note     :", trim(note_word))

print("\n== NOTE for operator 0xf221... ==")
mask2 = keccak(NOTE_DOMAIN + LEDGER + OPERATOR)
nw2 = bytes(a ^ b for a, b in zip(maskedNote, mask2))
print(" note:", trim(nw2))

print("\n== unlockHash verification ==")
for guess in [b'calldata', b'settled', b'letmein', record]:
    h = keccak(guess)
    print(f"  keccak({guess[:20]}) = {h.hex()}  match={h==unlockHash}")

print("\n== ARCHIVE ENTRY ==")
entry_mask = keccak(SEAL_DOMAIN + LEDGER + record)
entry = bytes(a ^ b for a, b in zip(maskedEntry, entry_mask))
print(" entry:", entry.hex())
print(" entry trimmed:", trim(entry))
slot = (int.from_bytes(keccak(ARCHIVE_DOMAIN + record), 'big') - 1) % (2**256)
print(" archive slot:", hex(slot))

print("\n== try other candidate records for entry ==")
for rname, r in [('settled', bytes.fromhex('736574746c6564'+'00'*25)),
                 ('calldata', record)]:
    em = keccak(SEAL_DOMAIN + LEDGER + r)
    e = bytes(a ^ b for a, b in zip(maskedEntry, em))
    print(f"  record={rname}: entry={e.hex()} ascii={trim(e)}")
