LDI R0, #8 ;Generates the nth fibonacci number
SUB R0, #2

;Starting values 
LDI R1, #1 
LDI R2, #1 

loop:
;eqv to MOV R3, R1
LDI R3, #0
ADD R3, R1

ADD R1, R2

;eqv to MOV R2, R3
LDI R2, #0
ADD R2, R3 

SUB R0, #1 
JNZ loop

HLT
