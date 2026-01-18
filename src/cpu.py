class CPU8Bit:
    def __init__(self, memory_size=65536):
        #8 bit registers R0, R1, R2, R3
        self.reg = [0, 0, 0, 0]

        #8 bit Instruction Register
        self.IR = 0

        #1 bit flags
        self.Z = 0
        self.C = 0

        #16 bit registers
        self.PC = 0
        self.MAR = 0

        #memory: 8 bit memory
        self.mem = [0] * memory_size

        self.halted = False

        # Exact opcode handlers (1 opcode = 1 meaning)
        self.opcode_handlers = {
            0x00: self.handle_nop,
            0xFF: self.handle_hlt,
            0xA0: self.handle_jmp,
            0xA1: self.handle_jz,
            0xA2: self.handle_jnz,
        }

        # High-nibble handlers (0x1_ means a family of instructions)
        self.hi_handlers = {
            0x10: self.handle_ldi,
            0x20: self.handle_ld,
            0x30: self.handle_st,
            0x40: self.handle_add_imm,
            0x50: self.handle_add_reg,
            0x60: self.handle_sub_imm,
            0x70: self.handle_and_imm,
            0x80: self.handle_or_imm,
            0x90: self.handle_xor_imm,
        }


    '''
    Start of instructions
    '''

    def handle_nop(self, opcode, operand):
        pass

    def handle_ldi(self, opcode, operand):
        r = opcode & 0x0F
        if r > 3:
            self.halted = True
            raise ValueError(f"Invalid register in opcode {opcode:02X}")

        self.reg[r] = operand & 0xFF
        self.set_z_flag(self.reg[r])

    def handle_ld(self, opcode, operand):
        r = opcode & 0x0F
        if r > 3:
            self.halted = True
            raise ValueError(f"Invalid register in opcode {opcode:02X}")

        self.reg[r] = self.mem[self.MAR] & 0xFF
        self.set_z_flag(self.reg[r])

    def handle_st(self, opcode, operand):
        r = opcode & 0x0F
        if r > 3:
            self.halted = True
            raise ValueError(f"Invalid register in opcode {opcode:02X}")

        self.mem[self.MAR] = self.reg[r]

    def handle_add_imm(self, opcode, operand):
        r = opcode & 0x0F
        if r > 3:
            self.halted = True
            raise ValueError(f"Invalid register in opcode {opcode:02X}")

        result = self.reg[r] + operand
        self.reg[r] = result & 0xFF
        self.set_c_flag_add(result)
        self.set_z_flag(self.reg[r])

    def handle_add_reg(self, opcode, operand):
        r = opcode & 0x0F
        if r > 3:
            self.halted = True
            raise ValueError(f"Invalid register in opcode {opcode:02X}")
        
        r2 = operand & 0x0F
        if r2 > 3:
            self.halted = True
            raise ValueError(f"Invalid register2 {operand:02X}")


        result = self.reg[r] + self.reg[r2]
        self.reg[r] = result & 0xFF
        self.set_c_flag_add(result)
        self.set_z_flag(self.reg[r])

    def handle_sub_imm(self, opcode, operand):
        r = opcode & 0x0F
        if r > 3:
            self.halted = True
            raise ValueError(f"Invalid register in opcode {opcode:02X}")

        result = self.reg[r] - operand
        self.reg[r] = result & 0xFF
        self.set_c_flag_sub(result)
        self.set_z_flag(self.reg[r])

    def handle_and_imm(self, opcode, operand):
        r = opcode & 0x0F
        if r > 3:
            self.halted = True
            raise ValueError(f"Invalid register in opcode {opcode:02X}")

        result = self.reg[r] & operand
        self.reg[r] = result & 0xFF
        self.set_z_flag(self.reg[r])

    def handle_or_imm(self, opcode, operand):
        r = opcode & 0x0F
        if r > 3:
            self.halted = True
            raise ValueError(f"Invalid register in opcode {opcode:02X}")

        result = self.reg[r] | operand
        self.reg[r] = result & 0xFF
        self.set_z_flag(self.reg[r])

    def handle_xor_imm(self, opcode, operand):
        r = opcode & 0x0F
        if r > 3:
            self.halted = True
            raise ValueError(f"Invalid register in opcode {opcode:02X}")

        result = self.reg[r] ^ operand
        self.reg[r] = result & 0xFF
        self.set_z_flag(self.reg[r])

    def handle_jmp(self, opcode, operand):
        self.PC = self.MAR

    def handle_jz(self, opcode, operand):
        if self.Z:
            self.PC = self.MAR

    def handle_jnz(self, opcode, operand):
        if not self.Z:
            self.PC = self.MAR

    def handle_hlt(self, opcode, operand):
        self.halted = True

    '''
    End of instructions
    '''


    def set_z_flag(self, result):
        if result == 0:
            self.Z = 1
        else:
            self.Z = 0

    def set_c_flag_add(self, result):
        if result > 255:
            self.C = 1
        else:
            self.C = 0

    def set_c_flag_sub(self, result):
        if result < 0:
            self.C = 0
        else:
            self.C = 1

    def load_program(self, program, start=0):
        for i, byte in enumerate(program):
            self.mem[(start + i) & 0xFFFF] = byte & 0xFF

    def execute(self, opcode, operand):
        #exact instructions first
        if opcode in self.opcode_handlers:
            self.opcode_handlers[opcode](opcode, operand)
            return

        #else use the high nibble
        hi = opcode & 0xF0
        handler = self.hi_handlers.get(hi)
        if handler is None:
            self.halted = True
            raise ValueError(f"Unknown opcode {opcode:02X}")

        handler(opcode, operand)


    def step(self):
        if self.halted:
            return

        #fetch opcode
        opcode = self.mem[self.PC & 0xFFFF]
        self.IR = opcode
        self.PC = (self.PC + 1) & 0xFFFF

        operand = None

        hi = opcode & 0xF0
        lo = opcode & 0x0F


        #fetch operands and MAR and advance PC
        if opcode in (0x00, 0xFF):
            pass

        elif hi in (0x20, 0x30):   # LD/ST r,addr
            loB = self.mem[self.PC]
            self.PC = (self.PC + 1) & 0xFFFF
            hiB = self.mem[self.PC]
            self.PC = (self.PC + 1) & 0xFFFF
            self.MAR = (hiB << 8) | loB  

        elif opcode in (0xA0, 0xA1, 0xA2):  # JMP/JZ/JNZ addr
            loB = self.mem[self.PC]
            self.PC = (self.PC + 1) & 0xFFFF
            hiB = self.mem[self.PC]
            self.PC = (self.PC + 1) & 0xFFFF
            self.MAR = (hiB << 8) | loB

        else:
            # 2-byte instructions
            operand = self.mem[self.PC]
            self.PC = (self.PC + 1) & 0xFFFF


        #execute 
        self.execute(opcode, operand)

        
    def run(self, max_cycles=1000):
        cycles = 0
        while not self.halted and cycles < max_cycles:
            print(f"PC={self.PC:04X} IR={self.IR:02X} R0={self.reg[0]:02X} R1={self.reg[1]:02X} R2={self.reg[2]:02X} R3={self.reg[3]:02X} Z={self.Z} C={self.C}")
            self.step()
            cycles += 1
            
from assembler import assemble

machine_code = assemble("programs/program.asm")

cpu = CPU8Bit()
cpu.load_program(machine_code)
cpu.run()