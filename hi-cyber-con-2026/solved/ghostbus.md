# GhostBus (58 pts · Hardware)

**Flag:** `hiCTF{gh0st_bu5_uart_n0nc3_r3v3al_9c3f12}`

## Descripción del reto
A smart-lock sensor hub was pulled from a decommissioned site. The vendor insists the
secure element is locked and the sealed region cannot be read. A field engineer probed
the hub's internal UART bus between the MCU and the secure element, and separately
dumped the hub's external SPI NOR flash. The external flash also holds a recovery
copy of the MCU firmware; `firmware.elf` is supplied separately for analysis.

The secure element holds a nonce for the currently provisioned sealed record.
It returns the same nonce on each read; reprovisioning replaces both that nonce
and the sealed ciphertext. This is not a fresh-random-number command.

Recover the hidden read, reverse the key derivation and open the sealed region.
No brute force needed: all crypto is standard, and every byte you need is in the
provided evidence.

**Files:** [ghost_bus.zip](https://hicon26-files-b19d71.nbg1.your-objectstorage.com/ghost-bus/3caa8119268aad4c/ghost_bus.zip)

SHA-256: `8ffeac83846c1261595323f18fa701d940c702cc724c185e312cebdd72ef2676`

**Flag Format:** `hiCTF{}`

## Solución
Write-up en elaboración por el enjambre. Notas crudas: `/tmp/ctf_notes_*.md` en el VPS del equipo.
