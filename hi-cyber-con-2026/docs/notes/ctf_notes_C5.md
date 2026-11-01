# C5 - Hardware front notes (HI Cyber Con 2026)

## GhostBus (59pts, id=b7d2e1fc-...)
- Files: capture.vcd/csv (UART MCU<->SE), flash_dump.bin (1MB SPI NOR), firmware.elf (131KB), diagram.png
- CSV parse (AA55 sync, [cmd][len][data][crc16]):
  - ch0 msg1: cmd=0x0C? NO -> len=0x0C,cmd=0x01,"GB2.2 SE OK!",crc=D5C9 (greeting/version)
  - ch0 msg2: 00 10 00 7C -> cmd=0x00(READ), len=0x10(16), addr=0x007C? 
  - ch1 reply: cmd=0x10, len=0x10, data= 9E3B7A44C1D05F82A6E1B4907CD3F5A2, crc=F3E2  <-- SE nonce, 16 bytes
- SE holds nonce (same each read) + sealed ciphertext. Need key derivation from firmware + flash.

## Tasmota Vault (56pts, id=ceda2443-...)
- ESP32 Tasmota + custom Berry agent. Flash image + MQTT traffic. Offline. 58MB zip.

## C3 Vault (59pts, id=37ad0ee5-...)
- ESP32-C3, SPI flash 4MB + efuse_read.bin. Flag ONLY on live instance -> need to auth to live service after extracting creds.

## GhostBus SOLVED (59 pts)
- salt24 (rodata 0x8000ca0) = 04325a9c117f3da0c0ffee5aa55a00ff1234567890abcdef
- nonce16 (SE resp UART) = 9e3b7a44c1d05f82a6e1b4907cd3f5a2
- key = SHA256(salt||nonce)[:16]  (AES-128)
- IV = nonce ; AES-128-CBC decrypt
- ct = flash[0x6A000:+48] with each 4-byte group reversed (firmware unswaps after hidden read)
- flag = hiCTF{gh0st_bu5_uart_n0nc3_r3v3al_9c3f12}
- "hidden read" = SE cmd seq (03 06 a0 ...), firmware sends 0xFF x48 to clock out sealed ct, stores RX bytes

## Tasmota Vault — SOLVED ✅ (+56pts)
- Flag: hiCTF{b3rry_r0t4t10n_c94934d76344ab1151e03afd}
- Method: Berry bytecode vault.bec runs subscribe handler on MQTT VaultRotate.
- KDF: HMAC_SHA256(keyring[epoch], "tasmota-vault/unwrap/v2\x00" || device_raw16 || epoch_i32le || nonce_raw32)
- Sealed: IV(12) || CT(46) || TAG(16) = 74B → AES-256-GCM decrypt
- Keyring: 3x{u32 id, key32}, ids 6,7,8. Epoch 8 + nonce from pcap epoch 8.
- Solving offline in Python was 100x faster than debugging the Berry VM port.
- Full derivation verified via berry_port Python VM with native stubs (crypto/mqtt/read_blob).
