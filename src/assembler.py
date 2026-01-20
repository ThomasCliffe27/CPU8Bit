class HashTable:
    def __init__(self, size: int) -> None:
        self.table = [None] * size
        self.size = size

    def hash_function(self, input: str) -> int:
        hashVal = 2166136261
        for char in input:
            hashVal ^= ord(char)
            hashVal *= 16777619
            hashVal &= 0xFFFFFFFF
        return hashVal % self.size
    
    def add(self, label: str, pos: int) -> None:
        index = start = self.hash_function(label)
        while self.table[index] is not None:
            if self.table[index][0] == label:
                raise ValueError(f"Duplicate label: {label}")
            index += 1
            index %= self.size
            if index == start:
                raise MemoryError(f"Hash table has run out of locations. Size: {self.size}")
        self.table[index] = [label, pos]

    def lookup(self, label: str) -> int:
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
    machine_code = bytearray(65536)
    line_number = 0
    global mem_pos
    mem_pos = 0

    def increment_mem_pos() -> None:
        global mem_pos
        mem_pos += 1
        if mem_pos >= 65536:
            raise OverflowError(f"Assembly error. Memory overflow error. mem_pos: {mem_pos}")

    def parse_reg(parts: list[str], idx: int) -> int:
        reg_tok = parts[idx].rstrip(",").upper() 
        if not reg_tok.startswith("R") or not reg_tok[1:].isdigit():
            raise ValueError(f"Bad register: {parts[idx]!r} on line {line_number}")

        reg = int(reg_tok[1:])
        if reg < 0 or reg > 3:
            raise ValueError(f"Register out of range: R{reg} on line {line_number}")
        
        return reg
    
    def parse_imm(parts: list[str], idx: int) -> int:
        imm_tok = parts[idx]
        if imm_tok.startswith("#"):
            imm_tok = imm_tok[1:]

        try:
            imm = int(imm_tok, 0) & 0xFF
        except ValueError:
            raise ValueError(f"Bad immediate {parts[idx]!r} on line {line_number}")
        
        return imm
    
    def parse_addr(parts: list[str], idx: int, brackets: bool, labels: HashTable) -> tuple[int, int]:
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
                addr_str = addr_str.replace(" ", "")
                label, modifier = addr_str, 0
                if "+" in addr_str:
                    label, off = addr_str.split("+", 1)
                    modifier = int(off, 0)

                addr = labels.lookup(label) + modifier
            except NameError:
                raise ValueError(f"Unknown label {addr_str!r} on line {line_number}")

        if not (0 <= addr <= 0xFFFF):
            raise ValueError(f"Address out of range {addr:#x} on line {line_number}")

        lo = addr & 0xFF
        hi = (addr >> 8) & 0xFF

        return lo, hi

    def handle_mnemonic(parts: list[str], labels: HashTable) -> None:
        global mem_pos
        mnemonic = parts[0].upper()

        if mnemonic.endswith(":"): #label
            return
        
        elif mnemonic.startswith("."): #directives
            if mnemonic == ".ORG":
                mem_pos = int(parts[1], 0)

            elif mnemonic == ".BYTE":
                for part in parts:
                    if part.startswith("."):
                        continue
                    machine_code[mem_pos] = int(part.strip(","), 0)
                    increment_mem_pos()

            elif mnemonic == ".WORD":
                lo, hi = parse_addr(parts, 1, False, labels)
                machine_code[mem_pos] = lo
                increment_mem_pos()
                machine_code[mem_pos] = hi
                increment_mem_pos()

        elif mnemonic == "NOP":
            machine_code[mem_pos] = (0x00)
            increment_mem_pos()

        elif mnemonic == "LDI":
            if len(parts) < 3:
                raise ValueError(f"Bad LDI syntax: {raw_line!r} on line {line_number}")

            reg = parse_reg(parts, 1)
            imm = parse_imm(parts, 2)

            machine_code[mem_pos] = (0x10 + reg)
            increment_mem_pos()
            machine_code[mem_pos] = (imm)
            increment_mem_pos()

        elif mnemonic == "LD":
            if len(parts) < 3:
                raise ValueError(f"Bad LD syntax: {raw_line!r} on line {line_number}")
            
            reg = parse_reg(parts, 1)
            lo, hi = parse_addr(parts, 2, True, labels)

            machine_code[mem_pos] = (0x20 + reg)
            increment_mem_pos()
            machine_code[mem_pos] = (lo)
            increment_mem_pos()
            machine_code[mem_pos] = (hi)
            increment_mem_pos()

        elif mnemonic == "ST":
            if len(parts) < 3:
                raise ValueError(f"Bad ST syntax: {raw_line!r} on line {line_number}")

            reg = parse_reg(parts, 1)
            lo, hi = parse_addr(parts, 2, True, labels)

            machine_code[mem_pos] = (0x30 + reg)
            increment_mem_pos()
            machine_code[mem_pos] = (lo)
            increment_mem_pos()
            machine_code[mem_pos] = (hi)
            increment_mem_pos()

        elif mnemonic == "ADD":
            if len(parts) < 3:
                raise ValueError(f"Bad ADD syntax: {raw_line!r} on line {line_number}")

            reg = parse_reg(parts, 1)
            
            if parts[2].upper().startswith("R"): #ADD r,r2
                reg2 = parse_reg(parts, 2)
                machine_code[mem_pos] = (0x50 + reg)
                increment_mem_pos()
                machine_code[mem_pos] = (0x00 + reg2)
                increment_mem_pos()

            else: #ADD r,imm
                imm = parse_imm(parts, 2)
                machine_code[mem_pos] = (0x40 + reg)
                increment_mem_pos()
                machine_code[mem_pos] = (imm)
                increment_mem_pos()

        elif mnemonic == "SUB":
            if len(parts) < 3:
                raise ValueError(f"Bad SUB syntax: {raw_line!r} on line {line_number}")

            reg = parse_reg(parts, 1)
            imm = parse_imm(parts, 2)

            machine_code[mem_pos] = (0x60 + reg)
            increment_mem_pos()
            machine_code[mem_pos] = (imm)
            increment_mem_pos()

        elif mnemonic == "AND":
            if len(parts) < 3:
                raise ValueError(f"Bad AND syntax: {raw_line!r} on line {line_number}")

            reg = parse_reg(parts, 1)
            imm = parse_imm(parts, 2)

            machine_code[mem_pos] = (0x70 + reg)
            increment_mem_pos()
            machine_code[mem_pos] = (imm)
            increment_mem_pos()

        elif mnemonic == "OR":
            if len(parts) < 3:
                raise ValueError(f"Bad OR syntax: {raw_line!r} on line {line_number}")

            reg = parse_reg(parts, 1)
            imm = parse_imm(parts, 2)

            machine_code[mem_pos] = (0x80 + reg)
            increment_mem_pos()
            machine_code[mem_pos] = (imm)
            increment_mem_pos()

        elif mnemonic == "XOR":
            if len(parts) < 3:
                raise ValueError(f"Bad XOR syntax: {raw_line!r} on line {line_number}")

            reg = parse_reg(parts, 1)
            imm = parse_imm(parts, 2)

            machine_code[mem_pos] = (0x90 + reg)
            increment_mem_pos()
            machine_code[mem_pos] = (imm)
            increment_mem_pos()

        elif mnemonic == "JMP":
            if len(parts) < 2:
                raise ValueError(f"Bad JMP syntax: {raw_line!r} on line {line_number}")
            
            lo, hi = parse_addr(parts, 1, False, labels)

            machine_code[mem_pos] = (0xA0)
            increment_mem_pos()
            machine_code[mem_pos] = (lo)
            increment_mem_pos()
            machine_code[mem_pos] = (hi)
            increment_mem_pos()

        elif mnemonic == "JZ":
            if len(parts) < 2:
                raise ValueError(f"Bad JZ syntax: {raw_line!r} on line {line_number}")
            
            lo, hi = parse_addr(parts, 1, False, labels)

            machine_code[mem_pos] = (0xA1)
            increment_mem_pos()
            machine_code[mem_pos] = (lo)
            increment_mem_pos()
            machine_code[mem_pos] = (hi)
            increment_mem_pos()

        elif mnemonic == "JNZ":
            if len(parts) < 2:
                raise ValueError(f"Bad JNZ syntax: {raw_line!r} on line {line_number}")
            
            lo, hi = parse_addr(parts, 1, False, labels)

            machine_code[mem_pos] = (0xA2)
            increment_mem_pos()
            machine_code[mem_pos] = (lo)
            increment_mem_pos()
            machine_code[mem_pos] = (hi)
            increment_mem_pos()

        elif mnemonic == "HLT":
            machine_code[mem_pos] = (0xFF)
            increment_mem_pos()

        else:
            raise ValueError(f"Unknown mnemonic: {mnemonic} on line {line_number}")

    def handle_raw_line(raw_line: str, line_number: int, labels: HashTable) -> None:
        line = raw_line.rstrip("\r\n")
        line = line.split(";", 1)[0].strip()
        line = line.replace(",", " ")

        if not line:
            return

        parts = line.split()
        handle_mnemonic(parts, labels)
        
    def instruction_len(mnemonic: str) -> int:
        mnemonic = mnemonic.upper()
        if mnemonic in ("NOP", "HLT"):
            return 1
        if mnemonic in ("LDI", "ADD", "SUB", "AND", "OR", "XOR"):
            return 2
        if mnemonic in ("LD", "ST", "JMP", "JZ", "JNZ"):
            return 3
        return 0

    def generate_label_table(file_name: str) -> HashTable:
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

                if first.startswith("."):
                    if first.lower() == ".org":
                        pos = int(parts[1], 0)
                        if not (0 <= pos <= 0xFFFF):
                            raise ValueError(f".org value error. Line: {line}")
                    elif first.lower() == ".byte":
                        pos += len(parts) - 1
                    elif first.lower() == ".word":
                        pos += 2
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
    for b in range(0, 100):
        print(f"0x{machine_code[b]:02X}")
