# Tasmota Vault (56 pts · Hardware)

**Flag:** `hiCTF{b3rry_r0t4t10n_c94934d76344ab1151e03afd}`

## Descripción del reto
A farm gateway was retired during a vault-key rotation. Its flash still holds a sealed record, and the recovery lab preserved a short broker session. Recover the record the gateway could authenticate.

The gateway uses official ESP32 Tasmota firmware with a custom Berry agent. The attachment is a reproducible laboratory fixture; `recovery.txt` inside the archive describes its acquisition assumptions and the matching tooling. Analyze both the flash image and the MQTT traffic.

This challenge is entirely **offline**. No physical board, running broker, emulator, brute force, or connection to the captured IP addresses is required.

**Files:** [tasmota_vault.zip](https://hicon26-files-b19d71.nbg1.your-objectstorage.com/tasmota-vault/f1203f4ddd7020a9/tasmota_vault.zip)

SHA-256: `74e01ec638452b8674b70301a8270fe8607950737ca1c7a7dc3f5f62c03906ad`

**Flag Format:** `hiCTF{}`

## Solución
Write-up en elaboración por el enjambre. Notas crudas: `/tmp/ctf_notes_*.md` en el VPS del equipo.
