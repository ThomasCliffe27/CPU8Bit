;Sets R3 to exp(a, b) / a^b

LDI R0, #2 ;a
LDI R1, #3 ;b   imm here is the power
SUB R1, #1 ;to make the program calculate correctly

ST R0, [0x1000]
ST R0, [0x1001]

loop:
  LD R0, [0x1000]
  LD R2, [0x1001]
  LDI R3, #0

  sub_loop:
    ADD R3, R2
    SUB R0, #1
    JNZ sub_loop

  ST R3, [0x1001]
  SUB R1, #1
  JNZ loop

HLT
