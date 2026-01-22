; Write 0xAB to address 0x1234 using STX, then load it back with LDX

LDI R1, #0x12
LDI R2, #0x34

LDI R0, #0xAB
STX R0, [R1:R2]

LDI R3, #0x00
LDX R3, [R1:R2]

ST  R3, [0x0100]
HLT
