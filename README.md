# 8-bit CPU Emulator

A simple 8-bit CPU emulator with:

- 4 general-purpose 8-bit registers (`R0`–`R3`)
- 16-bit program counter (`PC`)
- 16-bit memory address register (`MAR`)
- Zero flag (`Z`) and Carry flag (`C`)
- 64 KB memory (`65536` bytes)

---

## Registers

- `R0`–`R3`: 4 general-purpose 8-bit registers
- `PC`: 16-bit program counter
- `IR`: 8-bit instruction register
- `MAR`: 16-bit memory address register
- `Z`: zero flag
- `C`: carry flag
- `HALT`: halt state (CPU stops executing)

---

## Flags

Flags are updated **after** the destination register is written.

### Zero flag (`Z`)

- `Z = 1` if the result of the last operation is `0`
- otherwise `Z = 0`

### Carry flag (`C`)

- **ADD:** `C = 1` if carry out (`sum >= 256`), else `C = 0`
- **SUB:** `C = 1` if **no borrow** (`result >= 0`), else `C = 0`

### Instructions that update flags

- `LDI`, `LD`, `LDX`, `MOV`: set `Z`, leave `C`
- `ADD`: set `Z` and `C`
- `SUB`: set `Z` and `C` (`C = 1` means no borrow)
- `AND`, `OR`, `XOR`: set `Z`, leave `C`

### Instructions that do not change flags

- `ST`, `STX`, `JMP`, `JZ`, `JNZ`, `NOP`, `HLT`

---

## Memory

- `65536` bytes RAM
- Program is loaded into the same memory space
- Addresses are stored in **little-endian** order:

```text
[opcode][low byte][high byte]
```

Example: address `0x1234` is stored as `34 12`.

---

## Instruction Set

```text
NOP              - do nothing                            - 1 byte
LDI r, imm       - load immediate into register          - 2 bytes  [opcode][imm]
LD  r, [addr]    - load from memory into register        - 3 bytes  [opcode][addr]
ST  r, [addr]    - store register into memory            - 3 bytes  [opcode][addr]
ADD r, imm       - add immediate to register             - 2 bytes  [opcode][imm]
ADD r, r2        - add register r2 to register r         - 2 bytes  [opcode][reg]
SUB r ,imm       - subtract immediate from register      - 2 bytes  [opcode][imm]
AND r, imm       - bitwise AND immediate with register   - 2 bytes  [opcode][imm]
OR  r, imm       - bitwise OR immediate with register    - 2 bytes  [opcode][imm]
XOR r, imm       - bitwise XOR immediate with register   - 2 bytes  [opcode][imm]
JMP addr         - jump to address                       - 3 bytes  [opcode][addr]
JZ  addr         - jump if Z = 1                         - 3 bytes  [opcode][addr]
JNZ addr         - jump if Z = 0                         - 3 bytes  [opcode][addr]
MOV r, r2        - copy r2 into r                        - 2 bytes  [opcode][reg]
LDX r, [R1:R2]   - load from memory into register        - 2 bytes  [opcode][reg,reg]
STX r, [R1:R2]   - store register into memory            - 2 bytes  [opcode][reg,reg]
HLT              - halt program                          - 1 byte
```

---

## Opcode Encoding

### Register-based instructions

For all instructions referencing a register, the **high nibble** is the command and the **low nibble** selects the register.

Example (`LDI r,imm`):

- `0x10` → `LDI R0`
- `0x11` → `LDI R1`
- `0x12` → `LDI R2`
- `0x13` → `LDI R3`

### `Opcode r,r2` encoding

For `opcode r,r2`, register `r` is the **low nibble** of the opcode and register `r2` is the **low nibble** of the next byte (high nibble ignored).

Example:

```text
0x50 0x03  ->  R0 = R0 + R3
```

### `Opcode r, [R1:R2]` encoding

For `opcode r, [R1:R2]`, register `r` is the **low nibble** of the opcode, register `R1` is the **high nibble** of the next byte and register R2 is the **low nibble** of the same byte.

Example:

```text
0xC0 0x12  ->  R0 = value at memory address stored at (R1 << 8) + R2
```

### Error behaviour

Any opcode not defined, or any register id not in `0–3`, will:

- `HALT`
- return an error

---

## Opcode Map

```text
0x00 - NOP
0x1_ - LDI r, imm   (0x10-0x13 only)
0x2_ - LD  r, [addr]
0x3_ - ST  r, [addr]
0x4_ - ADD r, imm
0x5_ - ADD r, r2
0x6_ - SUB r, imm
0x7_ - AND r, imm
0x8_ - OR  r, imm
0x9_ - XOR r, imm
0xA0 - JMP addr
0xA1 - JZ  addr
0xA2 - JNZ addr
0xB_ - MOV r, r2
0xC_ - LDX r, [R1:R2]
0xD_ - STX r, [R1:R2]
0xFF - HLT
```
