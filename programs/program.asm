LDI R0, #8 
LDI R1, #6 
LDI R2, #0 
loop:
ADD R2, R0 
SUB R1, #1 
JNZ loop
HLT
