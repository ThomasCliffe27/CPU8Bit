class HashTable:
    def __init__(self, size):
        self.table = [None] * size
        self.size = size

    def hash_function(self, input: str):
        hashVal = 2166136261
        for char in input:
            hashVal ^= ord(char)
            hashVal *= 16777619
            hashVal &= 0xFFFFFFFF
        return hashVal % self.size
    
    def add(self, label, pos):
        index = start = self.hash_function(label)
        while self.table[index] is not None:
            if self.table[index][0] == label:
                raise ValueError(f"Duplicate label: {label}")
            index += 1
            index %= self.size
            if index == start:
                raise MemoryError(f"Hash table has run out of locations. Size: {self.size}")
        self.table[index] = [label, pos]

    def lookup(self, label):
        index = start = self.hash_function(label)
        while True:
            if self.table[index] is None:
                raise NameError(f"Label not in hash table. Label: {label}")
            if self.table[index][0] == label:
                return self.table[index][1]
            index += 1
            index %= self.size
            if index == start:
                raise NameError(f"Label not in hash table. Label: {label}")

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
    
    def parse_addr(parts, idx, brackets, labels):
        addr_tok = parts[idx].strip()

        if brackets:
            if not (addr_tok.startswith("[") and addr_tok.endswith("]")):
                raise ValueError(f"Address must be in [brackets]: {parts[idx]!r} on line {line_number}")

            addr_str = addr_tok[1:-1].strip()

        else:
            if (addr_tok.startswith("[") and addr_tok.endswith("]")):
                raise ValueError(f"Address should not be in [brackets]: {parts[idx]!r} on line {line_number}")
            addr_str = addr_tok

        try:
            addr = int(addr_str, 0)
        except ValueError:
            if labels is None:
                raise ValueError(f"Unknown label/address {addr_str!r} on line {line_number}")
            try:
                addr = labels.lookup(addr_str)
            except NameError:
                raise ValueError(f"Unknown label {addr_str!r} on line {line_number}")

        if not (0 <= addr <= 0xFFFF):
            raise ValueError(f"Address out of range {addr:#x} on line {line_number}")

        lo = addr & 0xFF
        hi = (addr >> 8) & 0xFF

        return lo, hi

    def handle_raw_line(raw_line, line_number, labels):
        line = raw_line.rstrip("\r\n")
        line = line.split(";", 1)[0].strip()

        if not line:
            return

        parts = line.split()
        mnemonic = parts[0].upper()

        if parts[0].endswith(":"):
            return

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
            lo, hi = parse_addr(parts, 2, True, labels)

            machine_code.append(0x20 + reg)
            machine_code.append(lo)
            machine_code.append(hi)

        elif mnemonic == "ST":
            if len(parts) < 3:
                raise ValueError(f"Bad ST syntax: {raw_line!r} on line {line_number}")

            reg = parse_reg(parts, 1)
            lo, hi = parse_addr(parts, 2, True, labels)

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
            
            lo, hi = parse_addr(parts, 1, False, labels)

            machine_code.append(0xA0)
            machine_code.append(lo)
            machine_code.append(hi)

        elif mnemonic == "JZ":
            if len(parts) < 2:
                raise ValueError(f"Bad JZ syntax: {raw_line!r} on line {line_number}")
            
            lo, hi = parse_addr(parts, 1, False, labels)

            machine_code.append(0xA1)
            machine_code.append(lo)
            machine_code.append(hi)

        elif mnemonic == "JNZ":
            if len(parts) < 2:
                raise ValueError(f"Bad JNZ syntax: {raw_line!r} on line {line_number}")
            
            lo, hi = parse_addr(parts, 1, False, labels)

            machine_code.append(0xA2)
            machine_code.append(lo)
            machine_code.append(hi)

        elif mnemonic == "HLT":
            machine_code.append(0xFF)

        else:
            raise ValueError(f"Unknown mnemonic: {mnemonic} on line {line_number}")

    def instruction_len(mnemonic: str):
        mnemonic = mnemonic.upper()
        if mnemonic in ("NOP", "HLT"):
            return 1
        if mnemonic in ("LDI", "ADD", "SUB", "AND", "OR", "XOR"):
            return 2
        if mnemonic in ("LD", "ST", "JMP", "JZ", "JNZ"):
            return 3
        return 0

    def generate_label_table(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            #initial passthrough to get labels
            num_labels = 0
            
            #Get the number of labels
            for raw_line in f:
                line = raw_line.rstrip("\r\n")
                line = line.split(";", 1)[0].strip()

                if not line:
                    continue

                parts = line.split()
                mnemonic = parts[0]
                if mnemonic.endswith(":"):
                    num_labels += 1
            f.seek(0)

            labels = HashTable(max(4, num_labels * 2))
            pos = 0
            for raw_line in f:
                line = raw_line.rstrip("\r\n")
                line = line.split(";", 1)[0].strip()

                if not line:
                    continue

                parts = line.split()
                first = parts[0]
            
                if first.endswith(":"):
                    labels.add(first[:-1], pos)
                    continue

                mnemonic = first.upper()
                pos += instruction_len(mnemonic)
            return (labels)

    with open(file_name, "r", encoding="utf-8") as f:

        labels = generate_label_table(file_name)

        #write to bytearray
        for raw_line in f:
            line_number += 1
            handle_raw_line(raw_line, line_number, labels)
        
    return machine_code

if __name__ == "__main__":
    machine_code = assemble("programs/program.asm")
    for b in machine_code:
        print(f"0x{b:02X}")

