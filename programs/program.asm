.org 0x0000
JMP start

.org 0x0200
data:
.byte 0x11, 0x22, 0x33
.word data

.org 0x0100
start:
LD R0, [data]       ; 0x11
LD R1, [data+1]     ; 0x22
LD R2, [data+2]     ; 0x33
LD R3, [data+4]
HLT
