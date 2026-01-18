def assemble(file_name: str) -> bytearray:
    machine_code = bytearray()
    line_number = 0

    def parse_reg(parts, idx):
        reg_tok = parts[idx].rstrip(",").upper() 
        if not reg_tok.startswith("R") or not reg_tok[1:].isdigit():
            raise ValueError(f"Bad register: {parts[idx]!r} on line {line_number}")

        reg = int(reg_tok[1:])
        if reg < 0 or reg > 3:
            raise ValueError(f"Register out of range: R{reg} on line {line_number}")
        
        return reg
    
    def parse_imm(parts, idx):
        imm_tok = parts[idx]
        if imm_tok.startswith("#"):
            imm_tok = imm_tok[1:]

        try:
            imm = int(imm_tok, 0) & 0xFF
        except ValueError:
            raise ValueError(f"Bad immediate {parts[idx]!r} on line {line_number}")
        
        return imm
    
    def parse_addr(parts, idx, brackets):
        addr_tok = parts[idx].strip()

        if brackets:
            if not (addr_tok.startswith("[") and addr_tok.endswith("]")):
                raise ValueError(f"Address must be in [brackets]: {parts[idx]!r} on line {line_number}")

            addr_str = addr_tok[1:-1].strip()

        else:
            if (addr_tok.startswith("[") and addr_tok.endswith("]")):
                raise ValueError(f"Address should not in [brackets]: {parts[idx]!r} on line {line_number}")
            addr_str = addr_tok

        try:
            addr = int(addr_str, 0)
        except ValueError:
            raise ValueError(f"Bad address {parts[idx]!r} on line {line_number}")

        if not (0 <= addr <= 0xFFFF):
            raise ValueError(f"Address out of range {addr:#x} on line {line_number}")

        lo = addr & 0xFF
        hi = (addr >> 8) & 0xFF

        return lo, hi


    with open(file_name, "r", encoding="utf-8") as f:
        for raw_line in f:
            line_number += 1

            line = raw_line.rstrip("\r\n")
            line = line.split(";", 1)[0].strip()

            if not line:
                continue

            parts = line.split()
            mnemonic = parts[0].upper()

            if mnemonic == "NOP":
                machine_code.append(0x00)

            elif mnemonic == "LDI":
                if len(parts) < 3:
                    raise ValueError(f"Bad LDI syntax: {raw_line!r} on line {line_number}")

                reg = parse_reg(parts, 1)
                imm = parse_imm(parts, 2)

                machine_code.append(0x10 + reg)
                machine_code.append(imm)

            elif mnemonic == "LD":
                if len(parts) < 3:
                    raise ValueError(f"Bad LD syntax: {raw_line!r} on line {line_number}")
                
                reg = parse_reg(parts, 1)
                lo, hi = parse_addr(parts, 2, True)

                machine_code.append(0x20 + reg)
                machine_code.append(lo)
                machine_code.append(hi)

            elif mnemonic == "ST":
                if len(parts) < 3:
                    raise ValueError(f"Bad ST syntax: {raw_line!r} on line {line_number}")

                reg = parse_reg(parts, 1)
                lo, hi = parse_addr(parts, 2, True)

                machine_code.append(0x30 + reg)
                machine_code.append(lo)
                machine_code.append(hi)

            elif mnemonic == "ADD":
                if len(parts) < 3:
                    raise ValueError(f"Bad ADD syntax: {raw_line!r} on line {line_number}")

                reg = parse_reg(parts, 1)
                
                if parts[2].upper().startswith("R"): #ADD r,r2
                    reg2 = parse_reg(parts, 2)
                    machine_code.append(0x50 + reg)
                    machine_code.append(0x00 + reg2)

                else: #ADD r,imm
                    imm = parse_imm(parts, 2)
                    machine_code.append(0x40 + reg)
                    machine_code.append(imm)

            elif mnemonic == "SUB":
                if len(parts) < 3:
                    raise ValueError(f"Bad SUB syntax: {raw_line!r} on line {line_number}")

                reg = parse_reg(parts, 1)
                imm = parse_imm(parts, 2)

                machine_code.append(0x60 + reg)
                machine_code.append(imm)

            elif mnemonic == "AND":
                if len(parts) < 3:
                    raise ValueError(f"Bad AND syntax: {raw_line!r} on line {line_number}")

                reg = parse_reg(parts, 1)
                imm = parse_imm(parts, 2)

                machine_code.append(0x70 + reg)
                machine_code.append(imm)

            elif mnemonic == "OR":
                if len(parts) < 3:
                    raise ValueError(f"Bad OR syntax: {raw_line!r} on line {line_number}")

                reg = parse_reg(parts, 1)
                imm = parse_imm(parts, 2)

                machine_code.append(0x80 + reg)
                machine_code.append(imm)

            elif mnemonic == "XOR":
                if len(parts) < 3:
                    raise ValueError(f"Bad XOR syntax: {raw_line!r} on line {line_number}")

                reg = parse_reg(parts, 1)
                imm = parse_imm(parts, 2)

                machine_code.append(0x90 + reg)
                machine_code.append(imm)

            elif mnemonic == "JMP":
                if len(parts) < 2:
                    raise ValueError(f"Bad JMP syntax: {raw_line!r} on line {line_number}")
                
                lo, hi = parse_addr(parts, 1, False)

                machine_code.append(0xA0)
                machine_code.append(lo)
                machine_code.append(hi)

            elif mnemonic == "JZ":
                if len(parts) < 2:
                    raise ValueError(f"Bad JZ syntax: {raw_line!r} on line {line_number}")
                
                lo, hi = parse_addr(parts, 1, False)

                machine_code.append(0xA1)
                machine_code.append(lo)
                machine_code.append(hi)

            elif mnemonic == "JNZ":
                if len(parts) < 2:
                    raise ValueError(f"Bad JNZ syntax: {raw_line!r} on line {line_number}")
                
                lo, hi = parse_addr(parts, 1, False)

                machine_code.append(0xA2)
                machine_code.append(lo)
                machine_code.append(hi)

            elif mnemonic == "HLT":
                machine_code.append(0xFF)

            else:
                raise ValueError(f"Unknown mnemonic: {mnemonic} on line {line_number}")
            

    return machine_code

if __name__ == "__main__":
    machine_code = assemble("programs/program.asm")
    for b in machine_code:
        print(f"0x{b:02X}")
