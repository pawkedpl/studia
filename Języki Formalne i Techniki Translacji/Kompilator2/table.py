class SymbolTable:
    def __init__(self):
        self.table = {}
        self.mem_pos = 0
        # memory layout:
        # 0 – accumulator
        # 1..9 – registers for generator
        # 10..99 – helper registers
        # 100+ – variables, arrays, refs, procedures

    # ======================================================
    # --- Zwykłe zmienne ---
    # ======================================================

    def add_symbol(self, name, lineno=-1):
        if name in self.table:
            print(f"\nError in line {lineno}: redeclaration of {name}.\n")
            return
        
        self.table[name] = {
            'position': self.mem_pos,
            'is_array': False,
            'start_idx': 0,
            'end_idx': 0,
            'assigned': True,         # zwykła zmienna jest OK od razu
            'is_reference': False,
            'is_iterator': False,
            'mode': 'VAR'             # zwykła zmienna
        }

        self.mem_pos += 1

    # ======================================================
    # --- Tablice ---
    # ======================================================

    def add_array(self, name, start_idx, end_idx, lineno=-1):
        if name in self.table:
            print(f"\nError in line {lineno}: redeclaration of {name}.\n")
            return

        start_idx = int(start_idx)
        end_idx = int(end_idx)

        if end_idx < start_idx:
            print(f"\nError in line {lineno}: invalid array range [{start_idx}:{end_idx}].\n")
            return

        # długość = indeksy od 0 do end_idx
        length = end_idx + 1

        self.table[name] = {
            'position': self.mem_pos,
            'is_array': True,
            'start_idx': start_idx,
            'end_idx': end_idx,
            'assigned': True,
            'is_reference': False,
            'is_iterator': False,
            'mode': 'VAR'
        }

        self.mem_pos += length + 1

    # ======================================================
    # --- Parametry formalne (skalarne) ---
    # ======================================================

    def add_symbol_ref(self, name, lineno=-1, mode='INOUT'):
        """Parametr formalny skalarny (IN, OUT, INOUT)."""

        if name in self.table:
            print(f"\nError in line {lineno}: redeclaration of {name}.\n")
            return

        # OUT jest początkowo nieprzypisany
        assigned = (mode != 'OUT')

        self.table[name] = {
            'position': self.mem_pos,
            'is_array': False,
            'start_idx': 0,
            'end_idx': 0,
            'assigned': assigned,
            'is_reference': True,
            'is_iterator': False,
            'mode': mode     # 'IN' | 'OUT' | 'INOUT'
        }

        self.mem_pos += 1

    # ======================================================
    # --- Parametry formalne tablicowe (T x) ---
    # ======================================================

    def add_array_ref(self, name, lineno=-1, mode='INOUT'):
        """Parametr formalny tablicowy (T x) – zawsze przez referencję."""

        if name in self.table:
            print(f"\nError in line {lineno}: redeclaration of {name}.\n")
            return

        assigned = (mode != 'OUT')

        self.table[name] = {
            'position': self.mem_pos,
            'is_array': True,
            'start_idx': 0,
            'end_idx': 0,
            'assigned': assigned,
            'is_reference': True,
            'is_iterator': False,
            'mode': mode
        }

        self.mem_pos += 1

    # ======================================================
    # --- Procedury ---
    # ======================================================

    def add_procedure(self, name, arguments, lineno=-1):
        """Wstawia wpis procedury + komórkę na adres powrotu."""

        if name in self.table:
            print(f"\nError in line {lineno}: redeclaration of {name}.\n")
            return

        self.table[name] = {
            'position': self.mem_pos,
            'is_array': False,
            'start_idx': 0,
            'end_idx': 0,
            'assigned': True,
            'is_reference': False,
            'arguments': arguments,
            'is_iterator': False,
            'mode': 'PROC'
        }

        # rezerwujemy slot na adres wejścia procedury
        self.mem_pos += 1

        # dodajemy slot procedury_rtrn
        self.add_symbol(name + "_rtrn", lineno)

    # ======================================================
    # --- Iterator pętli FOR ---
    # ======================================================

    def add_iterator(self, name, lineno=-1):
        """Iterator pętli – lokalny dla pętli, nie wolno go modyfikować."""

        if name in self.table:
            # jeśli został wcześniej nadpisany z innego scope'u
            self.table[name]['assigned'] = True
            self.table[name]['is_iterator'] = True
            self.table[name]['mode'] = 'ITER'
            return

        self.table[name] = {
            'position': self.mem_pos,
            'is_array': False,
            'start_idx': 0,
            'end_idx': 0,
            'assigned': True,
            'is_reference': False,
            'is_iterator': True,
            'mode': 'ITER'
        }

        self.mem_pos += 1

    # ======================================================
    # --- Pobieranie symbolu ---
    # ======================================================

    def get_symbol(self, name, lineno=-1):
        if name not in self.table:
            print(f"\nError in line {lineno}: {name} not declared.\n")
            return None
        return self.table[name]

    # ======================================================
    # --- Znajdowanie pozycją pamięci (debug) ---
    # ======================================================

    def find_name(self, position):
        for x in self.table:
            if self.table[x]['position'] == position:
                return x

    # ======================================================
    # --- Oznaczanie przypisania ---
    # ======================================================

    def mark_assigned(self, name, lineno=-1):
        if name in self.table:
            self.table[name]['assigned'] = True

    # ======================================================
    # --- Debug ---
    # ======================================================

    def display(self):
        for x in self.table:
            print(f"{x} → {self.table[x]}")
