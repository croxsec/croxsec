
## 14:45 Night Batch — COBOL ELF
- ELF GnuCOBOL, no lee archivos, imprime "account rejected" al fallar
- Strings del programa NO están en claro en el binario (construidos en runtime, heap 0x47xxxx)
- main=0x400940; frames: #9=0x400bce #8=0x40c4b3
- 0x400bce: memset(0x460140, ' ', 40) → campo de 40 chars
- LOOP: cmpw $0x12(18),0x460130; cada iteración call 404bc0; si ret 0 → je 400b77 (repite)
- 404bc0 = función de validación clave
