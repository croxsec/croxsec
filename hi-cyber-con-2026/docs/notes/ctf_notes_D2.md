# CTF D2 notes - Sun Nov  1 02:44:24 PM CST 2026

## SOLVED: The Inner Engine (58 pts)
- Flag: hiCTF{vm_byt3c0d3_1nn3r_3ng1n3_unw0und!}
- Key: L1c#N0d3_7mQ9f3a2b8c6d1e
- Method: Nim ELF with custom bytecode VM. Anti-debug via /proc/self/status TracerPid check (op242).
  Patched op242 handler (file offset 0x3ff6: xor eax,1 -> mov al,1). VM bytecode at 0x405e00 with 24 opcodes.
  23 constraints on 24 key bytes solved with z3. CHECK handler = KDF(key)^cipher == target.
  Success prints activation record = the flag.
