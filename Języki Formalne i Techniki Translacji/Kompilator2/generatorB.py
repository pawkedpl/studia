from table import SymbolTable


class Code:
    def __init__(self, name, arg=None, comment=None):
        self.name = name
        self.arg = arg
        self.comment = comment

    def to_string(self):
        if self.arg is None:
            s = f"{self.name}"
        else:
            s = f"{self.name} {self.arg}"
        if self.comment:
            s += f"    # {self.comment}"
        return s


class CodeGeneratorBase:

    def __init__(self, program, debug=False):
        self.program = program
        self.debug = debug
        self.table = SymbolTable()
        self.code = []
        self.scope = ""
        self.procs = {}          # nazwa -> {entry, formals, lineno, ret_pos}
        self.param_modes = {}    # pełna_nazwa -> I/O/INOUT/T
        self.in_main = False
        self._is_last_in_main = False
        self.iterators = {}      # full_name -> position (FOR)
        self.current_proc = None
        self.active_for_iterators = []
        self.current_proc_name = None
        self.proc_order = {}
        self.array_bounds = {}


    # =========================
    #  POMOCNICZE
    # =========================

    def emit_const(self, n: int):
        """Ustawia rejestr 'a' na wartość n –(najpierw INC, potem SHL/INC dla kolejnych bitów)."""
        if n == 0:
            # 0: po prostu wyzeruj rejestr
            return [Code("RST a")]

        # binarna reprezentacja liczby
        bits = bin(int(n))[2:]  # np. 100 -> "1100100"

        out = [Code("RST a")]

        # pierwszy (najbardziej znaczący) bit:
        # dla liczb naturalnych zawsze jest '1'
        if bits[0] == "1":
            out.append(Code("INC a"))

        # kolejne bity: SHL a, a jeśli bit==1 to dodatkowo INC a
        for b in bits[1:]:
            out.append(Code("SHL a"))
            if b == "1":
                out.append(Code("INC a"))

        return out



    def comms_to_list(self, comms):
        if comms is None:
            return []
        tag = comms[0]
        if tag == "comms_SINGLE":
            return [comms[1]]
        if tag == "comms_REC":
            return self.comms_to_list(comms[1]) + [comms[2]]
        print("Error: unknown comms tag:", tag)
        return []

    # =========================
    #  DEKLARACJE
    # =========================

    def decs_to_table(self, decs):
        if decs is None:
            return
        tag = decs[0]

        if tag == "decs_PID":
            name, ln = decs[1], decs[2]
            self.table.add_symbol(self.scope + name, ln)

        elif tag == "decs_REC_PID":
            self.decs_to_table(decs[1])
            name, ln = decs[2], decs[3]
            self.table.add_symbol(self.scope + name, ln)

        elif tag == "decs_ARRAY":
            name, low, high, ln = decs[1], decs[2], decs[3], decs[4]
            full = self.scope + name
            if low > high:
                print(f"Error in line {ln}: invalid array bounds {name}[{low}:{high}].")
            self.table.add_symbol(full, ln)
            # zapamiętujemy zakres
            self.array_bounds[full] = (low, high)

        elif tag == "decs_REC_ARRAY":
            self.decs_to_table(decs[1])
            name, low, high, ln = decs[2], decs[3], decs[4], decs[5]
            full = self.scope + name
            if low > high:
                print(f"Error in line {ln}: invalid array bounds {name}[{low}:{high}].")
            self.table.add_symbol(full, ln)
            # zapamiętujemy zakres
            self.array_bounds[full] = (low, high)

        else:
            ln = decs[-1]
            print(f"Error in line {ln}: unknown declarations tag {tag}.")


    # =========================
    #  DOSTĘP DO ZMIENNYCH
    # =========================
    
    def get_var_pos(self, identifier):
        tag = identifier[0]
        if tag != "id_PID":
            ln = identifier[-1]
            print(f"Error in line {ln}: only simple variables supported.")
            return None

        name = identifier[1]
        ln = identifier[2]
        sym = self.table.get_symbol(self.scope + name, ln)
        if sym is None:
            return None
        return sym["position"]
    
    # =========================
    #  TABLICE – ADRES ELEMENTU
    # =========================

    def _array_element_address_to_ra(self, identifier):
        """
        Dla identyfikatora:
          - id_ARR_NUM  (tab[NUM])
          - id_ARR_PID  (tab[i])
        ustawia w rejestrze ra ADRES elementu tablicy, zgodnie z zakresem [low:high].

        Używa rb i rc jako rejestrów pomocniczych.
        """
        itag = identifier[0]
        arr_name = identifier[1]
        ln = identifier[-1]
        full = self.scope + arr_name

        # zakres tablicy
        low, high = self.array_bounds.get(full, (0, None))

        # baza tablicy w pamięci
        sym_arr = self.table.get_symbol(full, ln)
        if sym_arr is None:
            return
        base_pos = sym_arr["position"]

        # --- RA = offset (indeks - low) ---
        if itag == "id_ARR_NUM":
            idx = identifier[2]
            if high is not None and (idx < low or idx > high):
                print(f"Error in line {ln}: index {idx} out of bounds for {arr_name}[{low}:{high}].")
            offset = max(idx - low, 0)
            self.code.extend(self.emit_const(offset))

        elif itag == "id_ARR_PID":
            idx_name = identifier[2]
            sym_i = self.table.get_symbol(self.scope + idx_name, ln)
            if sym_i is None:
                return
            # ra = i
            self.code.append(Code("LOAD", sym_i["position"]))
            if low != 0:
                # ra = i - low
                self.code.append(Code("SWP", "c"))      # rc = i
                self.code.extend(self.emit_const(low))  # ra = low
                self.code.append(Code("SWP", "b"))      # rb = low
                self.code.append(Code("SWP", "c"))      # ra = i
                self.code.append(Code("SUB", "b"))      # ra = i - low
        else:
            print(f"Error in line {ln}: unsupported array id tag {itag}.")
            return

        # --- teraz ra = offset, trzeba dodać bazę ---
        # rozróżniamy:
        #   - zwykła tablica: base_pos = adres elementu o indeksie 'low'
        #   - parametr T tab: pod base_pos jest WSKAŹNIK na bazę tablicy
        is_param_T = (full in self.param_modes and self.param_modes[full] == "T")

        if is_param_T:
            # rc = offset
            self.code.append(Code("SWP", "c"))
            # ra = MEM[base_pos] (wskaźnik na początek tablicy)
            self.code.append(Code("LOAD", base_pos))
            # rb = base
            self.code.append(Code("SWP", "b"))
            # ra = offset
            self.code.append(Code("SWP", "c"))
        else:
            # rc = offset
            self.code.append(Code("SWP", "c"))
            # ra = stała base_pos
            self.code.extend(self.emit_const(base_pos))
            # rb = base_pos
            self.code.append(Code("SWP", "b"))
            # ra = offset
            self.code.append(Code("SWP", "c"))

        # ra = base + offset
        self.code.append(Code("ADD", "b"))
        # wynik: ra = adres elementu tablicy

    # =========================
    #  SPRAWDZANIE, CZY ZMIENNA JEST PRZYPISANA
    # =========================

    def _check_assigned(self, full_name, ln, shown_name=None):
        """
        Sprawdza, czy zmienna (lub parametr) ma ustawione assigned == True.
        """
        sym = self.table.get_symbol(full_name, ln)
        if sym is None:
            return
        if not sym.get("assigned", True):
            name = shown_name or full_name
            print(f"Error in line {ln}: variable {name} may be used before assignment.")


    # =========================
    #  VALUE / EXPRESSION
    # =========================

    def value_to_acc(self, value):
        tag = value[0]

        # ---------- stała NUM ----------
        if tag == "val_NUM":
            n = value[1]
            self.code.extend(self.emit_const(n))
            return

        # ---------- identyfikator ----------
        if tag == "val_ID":
            identifier = value[1]
            itag = identifier[0]

            # ===== skalar x =====
            if itag == "id_PID":
                name, ln = identifier[1], identifier[2]
                full = self.scope + name
                pos = self.get_var_pos(identifier)
                if pos is None:
                    return

                # parametry formalne IN / OUT / INOUT — trzymamy adres zmiennej
                if full in self.param_modes and self.param_modes[full] != "T":
                    # w komórce "pos" jest adres to najpierw go ładujemy,
                    # potem dopiero odczytujemy wartość przez RLOAD
                    self.code.append(Code("LOAD", pos))
                    self.code.append(Code("RLOAD a"))
                else:
                    # zwykła zmienna lokalna / globalna
                    self.code.append(Code("LOAD", pos))
                return

            # ===== tablica s[NUM] =====
            if itag == "id_ARR_NUM":
                # indeks jako stała
                idx = identifier[2]
                # a := idx
                self.code.extend(self.emit_const(idx))
                # a := base + idx  (base w r[b])
                self.code.append(Code("ADD", "b"))
                # a := s[idx]
                self.code.append(Code("RLOAD a"))
                return

            # ===== tablica s[i] =====
            if itag == "id_ARR_PID":
                idx_name = identifier[2]
                ln       = identifier[3]
                sym_i = self.table.get_symbol(self.scope + idx_name, ln)
                if sym_i is None:
                    return
                # a := i
                self.code.append(Code("LOAD", sym_i["position"]))
                # a := base + i
                self.code.append(Code("ADD", "b"))
                # a := s[i]
                self.code.append(Code("RLOAD a"))
                return

        print("Error: unknown value tag:", tag)


        print("Error: unknown value tag:", tag)


        print("Error: unknown value tag:", tag)


    def calculate_expression(self, expr):
        tag = expr[0]

        if tag == "expr_VAL":
            self.value_to_acc(expr[1])
            return

        if tag != "expr_OP":
            print("Error: unknown expression tag:", tag)
            return

        v1, op, v2 = expr[1], expr[2], expr[3]

        # =========================
        #  +  (w tym specjalny przypadek x+x)
        # =========================
        if op == "+":

            # --- SPECJALNY CASE: i + i (ta sama zmienna skalarna) ---
            # generujemy:
            #   LOAD i
            #   ADD a
            try:
                if (
                    v1[0] == "val_ID"
                    and v2[0] == "val_ID"
                    and v1[1][0] == "id_PID"
                    and v2[1][0] == "id_PID"
                    and v1[1][1] == v2[1][1]      # ta sama nazwa
                ):
                    self.value_to_acc(v1)         # ra = i
                    self.code.append(Code("ADD", "a"))
                    return
            except Exception:
                pass

            # --- wersja ogólna x + y ---
            # używamy rc:
            #   (ra := second, rc := second, ra := first, ra += rc)
            self.value_to_acc(v2)                 # ra = v2
            self.code.append(Code("SWP", "c"))    # rc = v2
            self.value_to_acc(v1)                 # ra = v1
            self.code.append(Code("ADD", "c"))    # ra = v1 + v2
            return

        # =========================
        #  - 
        # =========================
        if op == "-":
            # ra = v2, rb = v2, ra = v1 - v2
            self.value_to_acc(v2)
            self.code.append(Code("SWP", "b"))
            self.value_to_acc(v1)
            self.code.append(Code("SUB", "b"))
            return

        # =========================
        #  *  (pełne mnożenie)
        # =========================
        if op == "*":
            ln = expr[-1]
            self._emit_mul(v1, v2, ln)
            return

        # =========================
        #  /  (pełne dzielenie z: dziel. przez 0 to 0)
        # =========================
        if op == "/":
            ln = expr[-1]
            self._emit_div(v1, v2, ln)
            return

        # =========================
        #  %  (reszta z dzielenia, %0 to 0)
        # =========================
        if op == "%":
            ln = expr[-1]
            self._emit_mod(v1, v2, ln)
            return

        print("Error: unsupported operator:", op)


    def _emit_mul(self, v1, v2, ln):
        """
        Oblicza v1 * v2 w rejestrze ra algorytmem O(log min(v1, v2)):
        rosyjskie mnożenie:
            res = 0
            a = v1
            b = v2
            while b > 0:
                if b jest nieparzyste: res += a
                a = a * 2
                b = b // 2
        """

        base = self.table.mem_pos + 30
        addr_a       = base      # a
        addr_b       = base + 1  # b
        addr_res     = base + 2  # res
        addr_half    = base + 3  # half = b // 2
        addr_rebuild = base + 4  # rebuild = 2 * half

        # a = v1
        self.value_to_acc(v1)
        self.code.append(Code("STORE", addr_a))

        # b = v2
        self.value_to_acc(v2)
        self.code.append(Code("STORE", addr_b))

        # res = 0
        self.code.extend(self.emit_const(0))
        self.code.append(Code("STORE", addr_res))

        # --------- pętla ----------
        loop_start = len(self.code)

        # jeśli b == 0 to koniec
        self.code.append(Code("LOAD", addr_b))
        jzero_done = len(self.code)
        self.code.append(Code("JZERO", 0))  

        # half = b // 2
        self.code.append(Code("LOAD", addr_b))
        self.code.append(Code("SHR a"))
        self.code.append(Code("STORE", addr_half))

        # rebuild = 2 * half
        self.code.append(Code("LOAD", addr_half))
        self.code.append(Code("SHL a"))
        self.code.append(Code("STORE", addr_rebuild))

        self.code.append(Code("LOAD", addr_rebuild))
        self.code.append(Code("SWP", "c"))
        self.code.append(Code("LOAD", addr_b))
        self.code.append(Code("SUB", "c"))

        jpos_odd = len(self.code)
        self.code.append(Code("JPOS", 0))   # do wypełnienia

        # --------- przypadek parzysty b: tylko aktualizujemy a, b ---------
        # a = a * 2
        self.code.append(Code("LOAD", addr_a))
        self.code.append(Code("SHL a"))
        self.code.append(Code("STORE", addr_a))

        # b = half
        self.code.append(Code("LOAD", addr_half))
        self.code.append(Code("STORE", addr_b))

        # skacz na początek pętli
        self.code.append(Code("JUMP", loop_start))

        # --------- przypadek nieparzysty b: res += a, potem jak wyżej ---------
        odd_label = len(self.code)

        # res += a
        self.code.append(Code("LOAD", addr_res))
        self.code.append(Code("SWP", "b"))      # rb = res
        self.code.append(Code("LOAD", addr_a))  # ra = a
        self.code.append(Code("ADD", "b"))      # ra = a + res
        self.code.append(Code("STORE", addr_res))

        # a = a * 2
        self.code.append(Code("LOAD", addr_a))
        self.code.append(Code("SHL a"))
        self.code.append(Code("STORE", addr_a))

        # b = half
        self.code.append(Code("LOAD", addr_half))
        self.code.append(Code("STORE", addr_b))

        # wróć na początek pętli
        self.code.append(Code("JUMP", loop_start))

        # --------- koniec: b == 0 ---------
        done_label = len(self.code)

        # podmieniamy adresy skoków
        self.code[jzero_done].arg = done_label
        self.code[jpos_odd].arg = odd_label

        # na koniec wynik w ra
        self.code.append(Code("LOAD", addr_res))

    def _emit_div(self, v1, v2, ln):

        base     = self.table.mem_pos + 20
        dividend = base        # v1
        divisor  = base + 1    # v2
        quotient = base + 2    # wynik

        # -------------------
        # zapisujemy v1 i v2
        # -------------------
        self.value_to_acc(v1)
        self.code.append(Code("STORE", dividend))

        self.value_to_acc(v2)
        self.code.append(Code("STORE", divisor))

        # q := 0
        self.code.extend(self.emit_const(0))
        self.code.append(Code("STORE", quotient))

        # jeśli divisor = 0 to od razu wynik 0
        self.code.append(Code("LOAD", divisor))
        jzero_div0 = len(self.code)
        self.code.append(Code("JZERO", 0))   # do uzupełnienia

        # -------------------
        # pętla: while dividend >= divisor
        # -------------------
        loop_start = len(self.code)

        # if divisor > dividend → wyjście z pętli
        # liczymy (divisor - dividend) i patrzymy na JPOS
        self.code.append(Code("LOAD", dividend))   # ra = dividend
        self.code.append(Code("SWP", "c"))         # rc = dividend
        self.code.append(Code("LOAD", divisor))    # ra = divisor
        self.code.append(Code("SUB", "c"))         # ra = max(divisor - dividend, 0)
        jpos_break = len(self.code)
        self.code.append(Code("JPOS", 0))          # jeśli >0 → divisor > dividend

        # dividend := dividend - divisor
        self.code.append(Code("LOAD", divisor))    # ra = divisor
        self.code.append(Code("SWP", "c"))         # rc = divisor
        self.code.append(Code("LOAD", dividend))   # ra = dividend
        self.code.append(Code("SUB", "c"))         # ra = max(dividend - divisor, 0)
        self.code.append(Code("STORE", dividend))  # dividend := dividend - divisor

        # quotient := quotient + 1
        self.code.append(Code("LOAD", quotient))   # ra = quotient
        self.code.append(Code("SWP", "b"))         # rb = quotient
        self.code.extend(self.emit_const(1))       # ra = 1
        self.code.append(Code("ADD", "b"))         # ra = quotient + 1
        self.code.append(Code("STORE", quotient))  # quotient := quotient + 1

        # skok na początek pętli
        self.code.append(Code("JUMP", loop_start))

        # miejsce wyjścia z pętli (gdy divisor > dividend)
        loop_end = len(self.code)
        self.code[jpos_break].arg = loop_end

        # normalny wynik: ra := quotient
        self.code.append(Code("LOAD", quotient))
        jmp_done = len(self.code)
        self.code.append(Code("JUMP", 0))          # przeskakujemy nad blok div-by-zero

        # -------------------
        # przypadek dzielenia przez zero
        # -------------------
        divzero_label = len(self.code)
        # v1 / 0 → 0
        self.code.append(Code("RST a"))

        # wspólny koniec
        done_label = len(self.code)

        # uzupełniamy skoki
        self.code[jmp_done].arg = done_label
        self.code[jzero_div0].arg = divzero_label

    def _emit_mod(self, v1, v2, ln):

        # rezerwujemy sobie 2 pomocnicze komórki 
        base = self.table.mem_pos + 10
        dividend = base      # v1
        divisor  = base + 1  # v2

        # zapis v1 do dividend
        self.value_to_acc(v1)
        self.code.append(Code("STORE", dividend))

        # zapis v2 do divisor
        self.value_to_acc(v2)
        self.code.append(Code("STORE", divisor))

        # if divisor = 0: skok do obsługi dzielenia przez zero
        self.code.append(Code("LOAD", divisor))
        jzero_div0 = len(self.code)
        self.code.append(Code("JZERO", 0))  

        # ---------- pętla: while divisor <= dividend ----------
        loop_start = len(self.code)

        # if divisor > dividend to wyjście z pętli
        # liczymy divisor - dividend i sprawdzamy JPOS
        self.code.append(Code("LOAD", dividend))   # ra = dividend
        self.code.append(Code("SWP", "c"))         # rc = dividend
        self.code.append(Code("LOAD", divisor))    # ra = divisor
        self.code.append(Code("SUB", "c"))         # ra = max(divisor - dividend, 0)
        jpos_break = len(self.code)
        self.code.append(Code("JPOS", 0))          # jeśli >0 → divisor > dividend

        # dividend := dividend - divisor
        self.code.append(Code("LOAD", divisor))    # ra = divisor
        self.code.append(Code("SWP", "c"))         # rc = divisor
        self.code.append(Code("LOAD", dividend))   # ra = dividend
        self.code.append(Code("SUB", "c"))         # ra = max(dividend - divisor, 0)
        self.code.append(Code("STORE", dividend))  # dividend := dividend - divisor

        # skok na początek pętli
        self.code.append(Code("JUMP", loop_start))

        # miejsce wyjścia z pętli
        loop_end = len(self.code)
        self.code[jpos_break].arg = loop_end

        # normalny wynik: ra := dividend (reszta)
        self.code.append(Code("LOAD", dividend))
        jmp_done = len(self.code)
        self.code.append(Code("JUMP", 0))   # przeskakujemy nad blok dzielenia przez 0

        # ---------- przypadek dzielenia przez 0 ----------
        divzero_label = len(self.code)
        # v1 % 0 → 0
        self.code.append(Code("RST a"))

        # wspólny "done": tu trafiają obie ścieżki
        done_label = len(self.code)

        # uzupełniamy skoki
        self.code[jmp_done].arg = done_label
        self.code[jzero_div0].arg = divzero_label



    # =========================
    #  WARUNKI
    # =========================

    def gen_condition_gt(self, cond):
        v1, v2 = cond[1], cond[3]

        if v2[0] == "val_NUM" and v2[1] == 0:
            # a := wartość v1
            self.value_to_acc(v1)
            return

        # --- OGÓLNY PRZYPADEK: x > y  =>  a := x - y ---
        self.value_to_acc(v2)         # a := y
        self.code.append(Code("SWP c"))  # rb := y
        self.value_to_acc(v1)         # a := x
        self.code.append(Code("SUB c"))  # a := x - y


    def gen_condition_eq_zero(self, cond):
        v1 = cond[1]
        self.value_to_acc(v1)

    # =========================
    #  DISPATCH KOMEND
    # =========================

    def gc_command(self, command):
        tag = command[0]
        if tag == "comm_READ":
            self.gc_comm_READ(command)
        elif tag == "comm_WRITE":
            self.gc_comm_WRITE(command)
        elif tag == "comm_ASSIGN":
            self.gc_comm_ASSIGN(command)
        elif tag == "comm_IF":
            self.gc_comm_IF(command)
        elif tag == "comm_IF_ELSE":
            self.gc_comm_IF_ELSE(command)
        elif tag == "comm_WHILE":
            self.gc_comm_WHILE(command)
        elif tag == "comm_REPEAT":
            self.gc_comm_REPEAT(command)
        elif tag == "comm_CALL":
            self.gc_comm_CALL(command)
        elif tag == "comm_FOR_UP":
            self.gc_comm_FOR_UP(command)
        elif tag == "comm_FOR_DOWN":
            self.gc_comm_FOR_DOWN(command)
        else:
            print(f"Error: unsupported command {tag}")

    # =========================
    #  READ / WRITE / ASSIGN
    # =========================

    def gc_comm_READ(self, command):
        identifier = command[1]
        itag = identifier[0]
        ln_stmt = command[-1]

        # ===== READ tab[i] / tab[NUM] =====
        if itag in ("id_ARR_PID", "id_ARR_NUM"):
            # ra = adres tablicy[...]
            self._array_element_address_to_ra(identifier)
            # rc = adres
            self.code.append(Code("SWP", "c"))
            # wczytaj wartość i zapisz pod tym adresem
            self.code.append(Code("READ"))
            self.code.append(Code("RSTORE", "c"))
            return


        # ===== READ x (skalar) =====
        pos = self.get_var_pos(identifier)
        if pos is None:
            return

        name = identifier[1]
        full = self.scope + name
        mode = self.param_modes.get(full, "INOUT")

        if mode == "IN":
            ln = command[-1]
            print(f"Error in line {ln}: cannot READ into IN parameter.")
            return

        if full in self.param_modes and self.param_modes[full] != "T":
            # parametr formalny (adres w pos)
            self.code.append(Code("LOAD", pos))
            self.code.append(Code("SWP", "b"))
            self.code.append(Code("READ"))
            self.code.append(Code("RSTORE", "b"))
        else:
            self.code.append(Code("READ"))
            self.code.append(Code("STORE", pos))

        # po READ mamy gwarantowane przypisanie
        self.table.mark_assigned(full, ln_stmt)

    def gc_comm_WRITE(self, command):
        self.value_to_acc(command[1])
        self.code.append(Code("WRITE"))

    def gc_comm_ASSIGN(self, command):
        identifier, expr = command[1], command[2]
        itag = identifier[0]

        # ===== s[i] := expr =====
        if itag in ("id_ARR_PID", "id_ARR_NUM"):
            ln = identifier[-1]

            # 1) policz INDEKS ]
            if itag == "id_ARR_NUM":
                idx = identifier[2]
                # ra = idx
                self.code.extend(self.emit_const(idx))
            else:  # id_ARR_PID, np. s[i]
                idx_name = identifier[2]
                sym_i = self.table.get_symbol(self.scope + idx_name, ln)
                if sym_i is None:
                    return
                # ra = i
                self.code.append(Code("LOAD", sym_i["position"]))

            # 2) base + index do adres elementu w rc
            #    (base tablicy jest w rb)
            self.code.append(Code("ADD", "b"))   # ra = base + index
            self.code.append(Code("SWP", "c"))   # rc = addr, ra – wolny

            # 3) policz WARTOŚĆ wyrażenia w ra
            self.calculate_expression(expr)

            # 4) zapisz pod adresem z rc
            self.code.append(Code("RSTORE", "c"))
            return

        # ===== x := expr (skalar) =====
        pos = self.get_var_pos(identifier)
        if pos is None:
            return

        name = identifier[1]
        full = self.scope + name
        mode = self.param_modes.get(full, "INOUT")

        if mode == "IN":
            ln = command[-1]
            print(f"Error in line {ln}: cannot assign to IN parameter.")
            return

        self.calculate_expression(expr)

        if full in self.param_modes:
            # parametr formalny (adres w pos)
            self.code.append(Code("SWP", "b"))
            self.code.append(Code("LOAD", pos))
            self.code.append(Code("SWP", "b"))
            self.code.append(Code("RSTORE", "b"))
        else:
            self.code.append(Code("STORE", pos))



    # =========================
    #  IF / ELSE
    # =========================

    def gc_comm_IF(self, command):
        cond, comms = command[1], command[2]
        op = cond[2]

        # x > y
        if op == ">":
            self.gen_condition_gt(cond)
            jzero = len(self.code)
            self.code.append(Code("JZERO", 0))
            for c in self.comms_to_list(comms):
                self.gc_command(c)
            end = len(self.code)
            self.code[jzero].arg = end
            return

        # x >= y
        if op in ("GE", ">="):
            fake = ("cond", cond[3], ">", cond[1], cond[4])
            self.gen_condition_gt(fake)
            jpos = len(self.code)
            self.code.append(Code("JPOS", 0))
            for c in self.comms_to_list(comms):
                self.gc_command(c)
            end = len(self.code)
            self.code[jpos].arg = end
            return

        # x = y
        if op == "=":
            v1, v2, ln = cond[1], cond[3], cond[4]

            # test x>y -> wyjście
            self.gen_condition_gt(cond)
            jpos1 = len(self.code)
            self.code.append(Code("JPOS", 0))

            # test y>x -> wyjście
            fake = ("cond", v2, ">", v1, ln)
            self.gen_condition_gt(fake)
            jpos2 = len(self.code)
            self.code.append(Code("JPOS", 0))

            # jeśli doszliśmy tutaj, to x = y
            for c in self.comms_to_list(comms):
                self.gc_command(c)

            end = len(self.code)
            self.code[jpos1].arg = end
            self.code[jpos2].arg = end
            return

        # x != y
        if op == "!=":
            v1, v2, ln = cond[1], cond[3], cond[4]

            # x>y -> od razu THEN
            self.gen_condition_gt(cond)
            jpos1 = len(self.code)
            self.code.append(Code("JPOS", 0))

            # y>x -> od razu THEN
            fake = ("cond", v2, ">", v1, ln)
            self.gen_condition_gt(fake)
            jpos2 = len(self.code)
            self.code.append(Code("JPOS", 0))

            # x = y -> skok za THEN
            j_eq = len(self.code)
            self.code.append(Code("JUMP", 0))

            then_start = len(self.code)
            for c in self.comms_to_list(comms):
                self.gc_command(c)

            end = len(self.code)
            self.code[jpos1].arg = then_start
            self.code[jpos2].arg = then_start
            self.code[j_eq].arg = end
            return

        ln = cond[-1]
        print(f"Error in line {ln}: IF supports only '>', '>=', '=', '!='.")

    def gc_comm_IF_ELSE(self, command):
        cond, then_c, else_c = command[1], command[2], command[3]
        op = cond[2]

        # x > y
        if op == ">":
            self.gen_condition_gt(cond)
            jzero = len(self.code)
            self.code.append(Code("JZERO", 0))

            for c in self.comms_to_list(then_c):
                self.gc_command(c)

            jump_end = len(self.code)
            self.code.append(Code("JUMP", 0))

            else_start = len(self.code)
            for c in self.comms_to_list(else_c):
                self.gc_command(c)

            end = len(self.code)
            self.code[jzero].arg = else_start
            self.code[jump_end].arg = end
            return

        # x >= y
        if op in ("GE", ">="):
            fake = ("cond", cond[3], ">", cond[1], cond[4])
            self.gen_condition_gt(fake)
            jpos = len(self.code)
            self.code.append(Code("JPOS", 0))

            for c in self.comms_to_list(then_c):
                self.gc_command(c)

            jump_end = len(self.code)
            self.code.append(Code("JUMP", 0))

            else_start = len(self.code)
            for c in self.comms_to_list(else_c):
                self.gc_command(c)

            end = len(self.code)
            self.code[jpos].arg = else_start
            self.code[jump_end].arg = end
            return

        # x = y
        if op == "=":
            v1, v2, ln = cond[1], cond[3], cond[4]

            # x>y -> ELSE
            self.gen_condition_gt(cond)
            jpos1 = len(self.code)
            self.code.append(Code("JPOS", 0))

            # y>x -> ELSE
            fake = ("cond", v2, ">", v1, ln)
            self.gen_condition_gt(fake)
            jpos2 = len(self.code)
            self.code.append(Code("JPOS", 0))

            # jeśli doszliśmy tutaj, to x = y → THEN
            for c in self.comms_to_list(then_c):
                self.gc_command(c)

            jump_end = len(self.code)
            self.code.append(Code("JUMP", 0))

            else_start = len(self.code)
            for c in self.comms_to_list(else_c):
                self.gc_command(c)

            end = len(self.code)
            self.code[jpos1].arg = else_start
            self.code[jpos2].arg = else_start
            self.code[jump_end].arg = end
            return

        # x != y
        if op == "!=":
            v1, v2, ln = cond[1], cond[3], cond[4]

            # x>y -> THEN
            self.gen_condition_gt(cond)
            jpos1 = len(self.code)
            self.code.append(Code("JPOS", 0))

            # y>x -> THEN
            fake = ("cond", v2, ">", v1, ln)
            self.gen_condition_gt(fake)
            jpos2 = len(self.code)
            self.code.append(Code("JPOS", 0))

            # x = y -> ELSE
            j_eq = len(self.code)
            self.code.append(Code("JUMP", 0))

            then_start = len(self.code)
            for c in self.comms_to_list(then_c):
                self.gc_command(c)

            jump_end = len(self.code)
            self.code.append(Code("JUMP", 0))

            else_start = len(self.code)
            for c in self.comms_to_list(else_c):
                self.gc_command(c)

            end = len(self.code)
            self.code[jpos1].arg = then_start
            self.code[jpos2].arg = then_start
            self.code[j_eq].arg = else_start
            self.code[jump_end].arg = end
            return

        ln = cond[-1]
        print(f"Error in line {ln}: IF-ELSE supports only '>', '>=', '=', '!='.")

    # =========================
    #  WHILE
    # =========================

    def gc_comm_WHILE(self, command):
        cond, comms = command[1], command[2]
        op = cond[2]

        start = len(self.code)

        # x > y
        if op == ">":
            self.gen_condition_gt(cond)
            jzero = len(self.code)
            self.code.append(Code("JZERO", 0))
            for c in self.comms_to_list(comms):
                self.gc_command(c)
            self.code.append(Code("JUMP", start))
            out = len(self.code)
            self.code[jzero].arg = out
            return

        # x >= y
        if op in ("GE", ">="):
            fake = ("cond", cond[3], ">", cond[1], cond[4])
            self.gen_condition_gt(fake)
            jpos = len(self.code)
            self.code.append(Code("JPOS", 0))
            for c in self.comms_to_list(comms):
                self.gc_command(c)
            self.code.append(Code("JUMP", start))
            out = len(self.code)
            self.code[jpos].arg = out
            return

        # x = y
        if op == "=":
            v1, v2, ln = cond[1], cond[3], cond[4]

            # test x>y -> wyjście
            self.gen_condition_gt(cond)
            jpos1 = len(self.code)
            self.code.append(Code("JPOS", 0))

            # test y>x -> wyjście
            fake = ("cond", v2, ">", v1, ln)
            self.gen_condition_gt(fake)
            jpos2 = len(self.code)
            self.code.append(Code("JPOS", 0))

            # ciało
            for c in self.comms_to_list(comms):
                self.gc_command(c)
            self.code.append(Code("JUMP", start))

            out = len(self.code)
            self.code[jpos1].arg = out
            self.code[jpos2].arg = out
            return

        # x != y
        if op == "!=":
            v1, v2, ln = cond[1], cond[3], cond[4]

            # pętla WHILE x!=y:
            # jeśli x>y lub y>x to ciało
            # jeśli x=y to wyjście

            # x>y -> ciało
            self.gen_condition_gt(cond)
            jpos1 = len(self.code)
            self.code.append(Code("JPOS", 0))

            # y>x -> ciało
            fake = ("cond", v2, ">", v1, ln)
            self.gen_condition_gt(fake)
            jpos2 = len(self.code)
            self.code.append(Code("JPOS", 0))

            # x = y -> wyjście
            j_eq = len(self.code)
            self.code.append(Code("JUMP", 0))

            body_start = len(self.code)
            for c in self.comms_to_list(comms):
                self.gc_command(c)
            self.code.append(Code("JUMP", start))

            out = len(self.code)
            self.code[jpos1].arg = body_start
            self.code[jpos2].arg = body_start
            self.code[j_eq].arg = out
            return

        ln = cond[-1]
        print(f"Error in line {ln}: WHILE supports only '>', '>=', '=', '!='.")


    # =========================
    #  REPEAT
    # =========================

    def gc_comm_REPEAT(self, command):
        comms, cond = command[1], command[2]

        op = cond[2]
        if not (op == "=" and cond[3][0] == "val_NUM" and cond[3][1] == 0):
            ln = cond[-1]
            print(f"Error in line {ln}: REPEAT supports only 'x=0'.")
            return

        special_pdf_like = (
            self.in_main
            and self._is_last_in_main
            and cond[1][0] == "val_ID"
        )

        start = len(self.code)
        for c in self.comms_to_list(comms):
            self.gc_command(c)

        if special_pdf_like:
            ident = cond[1][1]
            pos = self.get_var_pos(ident)
            if pos is not None:
                self.code.append(Code("LOAD", pos))
                self.code.append(Code("JPOS", start))
                return

        self.gen_condition_eq_zero(cond)
        jzero = len(self.code)
        self.code.append(Code("JZERO", 0))
        self.code.append(Code("JUMP", start))
        out = len(self.code)
        self.code[jzero].arg = out

    # =========================
    #  FOR PĘTLE
    # =========================

    def _ensure_iterator_symbol(self, name, ln):
        """
        Tworzy (jeśli trzeba) iterator i w aktualnym scope — bez błędów "not declared".
        Dodatkowo tworzy ukryty licznik i__cnt (używany przez generację FOR),
        żeby SymbolTable nie zgłaszał błędów dla tych wewnętrznych nazw.
        """
        # pełne nazwy w danym scope
        full_iter = self.scope + name              # np. "licz__i"
        full_cnt  = self.scope + name + "__cnt"    # np. "licz__i__cnt"

        # --- iterator i ---
        if full_iter not in self.iterators:
            self.table.add_symbol(full_iter, ln)
            sym_iter = self.table.get_symbol(full_iter, ln)
            self.iterators[full_iter] = sym_iter["position"]

        # --- ukryty licznik i__cnt ---
        # (nie używasz go w IMP, to tylko techniczna komórka w pamięci)
        if full_cnt not in self.iterators:
            self.table.add_symbol(full_cnt, ln)
            sym_cnt = self.table.get_symbol(full_cnt, ln)
            self.iterators[full_cnt] = sym_cnt["position"]

        # zwracamy pozycję właściwego iteratora i
        return self.iterators[full_iter]


    def gc_comm_FOR_UP(self, command):
        _, pid, v_from, v_to, comms, ln = command
        i_pos = self._ensure_iterator_symbol(pid, ln)
        full_iter = self.scope + pid

        # pomocnicza komórka na licznik i'
        cnt_full = full_iter + "__cnt"
        sym_cnt = self.table.get_symbol(cnt_full, ln)
        if sym_cnt is None:
            self.table.add_symbol(cnt_full, ln)
            sym_cnt = self.table.get_symbol(cnt_full, ln)
        cnt_pos = sym_cnt["position"]

        # ===== i := FROM =====
        self.value_to_acc(v_from)
        self.code.append(Code("STORE", i_pos))

        # ===== i' := ... =====

        if (
            v_from[0] == "val_NUM" and v_from[1] == 2 and
            v_to[0] == "val_ID"
        ):
            self.value_to_acc(v_to)
            # i' := TO - 1  (n-1)
            self.code.append(Code("DEC a"))
            self.code.append(Code("STORE", cnt_pos))
        else:
            self.value_to_acc(v_from)
            self.code.append(Code("SWP b"))   # rb = FROM
            self.value_to_acc(v_to)           # ra = TO
            self.code.append(Code("SUB b"))   # ra = TO-FROM (>=0)
            self.code.append(Code("INC a"))   # +1
            self.code.append(Code("STORE", cnt_pos))

        # ===== Pętla FOR =====
        loop_test = len(self.code)

        # LOAD i'
        self.code.append(Code("LOAD", cnt_pos))
        jzero = len(self.code)
        self.code.append(Code("JZERO", 0))    # skok za FOR, jeśli i' == 0

        # i'-- na początku iteracji
        self.code.append(Code("DEC a"))
        self.code.append(Code("STORE", cnt_pos))

        # zaznaczamy aktywny iterator do sprawdzania zakazu modyfikacji
        self.active_for_iterators.append(full_iter)

        # ciało pętli
        for c in self.comms_to_list(comms):
            self.gc_command(c)

        # koniec ciała pętli
        self.active_for_iterators.pop()

        # i := i+1
        self.code.append(Code("LOAD", i_pos))
        self.code.append(Code("INC a"))
        self.code.append(Code("STORE", i_pos))

        # skok na początek testu
        self.code.append(Code("JUMP", loop_test))
        end = len(self.code)
        self.code[jzero].arg = end



    def gc_comm_FOR_DOWN(self, command):
        _, pid, v_from, v_to, comms, ln = command
        i_pos = self._ensure_iterator_symbol(pid, ln)
        full_iter = self.scope + pid

        # pomocnicza komórka na licznik i'
        cnt_full = full_iter + "__cnt"
        sym_cnt = self.table.get_symbol(cnt_full, ln)
        if sym_cnt is None:
            self.table.add_symbol(cnt_full, ln)
            sym_cnt = self.table.get_symbol(cnt_full, ln)
        cnt_pos = sym_cnt["position"]

        # ===== i := FROM =====
        self.value_to_acc(v_from)
        self.code.append(Code("STORE", i_pos))

        # ===== i' := ... =====

        if (
            v_from[0] == "val_ID" and
            v_to[0] == "val_NUM" and v_to[1] == 2
        ):
            # i' := FROM - 1 (np. n-1)
            self.value_to_acc(v_from)
            self.code.append(Code("DEC a"))
            self.code.append(Code("STORE", cnt_pos))
        else:
            # ogólny przypadek: i' := FROM - TO + 1
            self.value_to_acc(v_to)
            self.code.append(Code("SWP b"))   # rb = TO
            self.value_to_acc(v_from)         # ra = FROM
            self.code.append(Code("SUB b"))   # ra = FROM-TO
            self.code.append(Code("INC a"))   # +1
            self.code.append(Code("STORE", cnt_pos))

        # ===== Pętla FOR (DOWNTO) =====
        loop_test = len(self.code)

        self.code.append(Code("LOAD", cnt_pos))
        jzero = len(self.code)
        self.code.append(Code("JZERO", 0))

        self.code.append(Code("DEC a"))
        self.code.append(Code("STORE", cnt_pos))

        self.active_for_iterators.append(full_iter)

        for c in self.comms_to_list(comms):
            self.gc_command(c)

        self.active_for_iterators.pop()

        # i := i-1
        self.code.append(Code("LOAD", i_pos))
        self.code.append(Code("DEC a"))
        self.code.append(Code("STORE", i_pos))

        self.code.append(Code("JUMP", loop_test))
        end = len(self.code)
        self.code[jzero].arg = end



 