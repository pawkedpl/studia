from generatorB import CodeGeneratorBase, Code


class CodeGenerator(CodeGeneratorBase):
    """
    Cienki wrapper na CodeGeneratorBase:
    - obsługa listy procedur,
    - parametry (I/O/INOUT/ew. T),
    - CALL,
    - generate_code (skok nad procedury do maina).
    """

    # =========================
    #  PROCEDURY – struktury pomocnicze
    # =========================

    def procs_to_list(self, procs):
        if procs == "procs_EMPTY":
            return []
        tag = procs[0]
        if tag in ("procs_LONG", "procs_SHORT"):
            lst = self.procs_to_list(procs[1])
            lst.append(procs)
            return lst
        print("Error: unknown procs tag:", tag)
        return []

    def args_decl_to_list(self, args_decl):
        if args_decl is None:
            return []
        tag = args_decl[0]

        # PROCEDURE p(I x, O y, INOUT z, T s, .)
        if tag == "ard_PID":
            # (ard_PID, name, mode, lineno)
            return [(args_decl[1], args_decl[2], args_decl[3])]

        if tag == "ard_REC_PID":
            # (ard_REC_PID, poprzednie, name, mode, lineno)
            lst = self.args_decl_to_list(args_decl[1])
            lst.append((args_decl[2], args_decl[3], args_decl[4]))
            return lst

        # pojedynczy parametr tablicowy T s
        if tag == "ard_ARRAY":
            # (ard_ARRAY, name, lineno)
            name, ln = args_decl[1], args_decl[2]
            return [(name, "T", ln)]

        # wiele parametrów, np. T s, I n
        if tag == "ard_REC_ARRAY":
            # (ard_REC_ARRAY, poprzednie, name, lineno)
            lst = self.args_decl_to_list(args_decl[1])
            name, ln = args_decl[2], args_decl[3]
            lst.append((name, "T", ln))
            return lst

        print("Error: unknown args_decl tag:", tag)
        return []

    def get_proc_declarations(self, proc):
        tag = proc[0]
        return proc[3] if tag == "procs_LONG" else None

    def get_proc_commands(self, proc):
        tag = proc[0]
        return proc[4] if tag == "procs_LONG" else proc[3]

    # =========================
    #  GENERACJA CIAŁA PROCEDURY
    # =========================

    def gen_procedure(self, proc):
        head = proc[2]
        pname = head[1]
        args_decl = head[2]
        head_ln = head[3]

        old_scope = self.scope
        self.scope = pname + "__"

        # RET
        ret_full = self.scope + "__RET__"
        self.table.add_symbol(ret_full, head_ln)
        ret_sym = self.table.get_symbol(ret_full, head_ln)
        ret_pos = ret_sym["position"]

        # parametry formalne
        formals = []
        for (name, mode, ln) in self.args_decl_to_list(args_decl):
            full = self.scope + name

            if mode == "T":
                # parametr tablicowy T x – zawsze przez referencję
                self.table.add_array_ref(full, ln, "INOUT")
                self.param_modes[full] = "T"
            else:
                # skalar: IN / OUT / INOUT
                self.table.add_symbol_ref(full, ln, mode)
                self.param_modes[full] = mode

            sym = self.table.get_symbol(full, ln)
            pos = sym["position"]

            formals.append({
                "name": name,
                "full": full,
                "pos": pos,
                "mode": self.param_modes[full],
            })


        # deklaracje lokalne
        self.decs_to_table(self.get_proc_declarations(proc))

        entry = len(self.code)
        self.procs[pname] = {
            "entry": entry,
            "formals": formals,
            "lineno": head_ln,
            "ret_pos": ret_pos,
        }

        # --------- PROLOG ---------
        self.code.append(Code("STORE", ret_pos))
        if formals:
            f0 = formals[0]
            self.code.append(Code("LOAD", f0["pos"]))
            self.code.append(Code("SWP", "b"))

        # ====== TU: ustawiamy aktualną procedurę ======
        prev_proc = self.current_proc_name
        self.current_proc_name = pname

        # --------- CIAŁO PROCEDURY ---------
        for c in self.comms_to_list(self.get_proc_commands(proc)):
            self.gc_command(c)

        # przywróć poprzednią wartość (np. None albo nazwę procedury wywołującej)
        self.current_proc_name = prev_proc
        # ====== KONIEC BLOKU ======

        # --------- EPILOG ---------
        self.code.append(Code("LOAD", ret_pos))
        self.code.append(Code("RTRN"))

        self.scope = old_scope


    # =========================
    #  CALL
    # =========================

    def get_args_list_from_call(self, args_ast):
        if args_ast is None:
            return []
        tag = args_ast[0]
        if tag == "ar_PID":
            return [args_ast[1]]
        if tag == "ar_REC":
            lst = self.get_args_list_from_call(args_ast[1])
            lst.append(args_ast[2])
            return lst
        print("Error: unknown args tag in call:", tag)
        return []

    def gc_comm_CALL(self, command):
        pcall   = command[1]
        call_ln = pcall[3]
        pname   = pcall[1]
        args_ast = pcall[2]

        if pname not in self.procs:
            print(f"Error in line {call_ln}: procedure {pname} not defined.")
            return

        meta    = self.procs[pname]
        entry   = meta["entry"]
        formals = meta["formals"]

        actuals = self.get_args_list_from_call(args_ast)
        if len(actuals) != len(formals):
            print(f"Error in line {call_ln}: wrong number of arguments in call to {pname}.")
            return

        # poprzedni adres dla optymalizacji "INC a"
        prev_nonref_addr = None
        prev_was_nonref  = False

        # ustawienie wskaźników faktycznych (adresów zmiennych/tablic)
        for formal, actual_name in zip(formals, actuals):
            fpos        = formal["pos"]
            fmode       = formal["mode"]              # 'IN', 'OUT', 'INOUT' albo 'T'
            formal_full = formal["full"]

            actual_full = self.scope + actual_name
            asym = self.table.get_symbol(actual_full, call_ln)
            if asym is None:
                return

            actual_addr   = asym["position"]
            actual_mode   = asym.get("mode", "INOUT")          # 'IN', 'OUT', 'INOUT', 'VAR'
            actual_is_ref = asym.get("is_reference", False)    # True dla parametrów formalnych

            # przeniesienie informacji o tablicach (jeśli array_bounds)
            if hasattr(self, "array_bounds") and actual_full in self.array_bounds:
                self.array_bounds[formal_full] = self.array_bounds[actual_full]

            # ========= SPRAWDZENIE ZGODNOŚCI TRYBÓW =========

            # 1) IN może być przekazany tylko do IN
            if actual_mode == "IN" and fmode != "IN":
                print(
                    f"Error in line {call_ln}: IN parameter {actual_name} "
                    f"can be passed only to IN argument of {pname}."
                )

            # 2) OUT nie może być przekazany na miejsce IN
            if actual_mode == "OUT" and fmode == "IN":
                print(
                    f"Error in line {call_ln}: OUT parameter {actual_name} "
                    f"cannot be passed as IN argument to {pname}."
                )
            if actual_is_ref:
                # kopiujemy wskaźnik z komórki parametru wywołującego
                self.code.append(Code("LOAD", actual_addr))
                self.code.append(Code("STORE", fpos))

                prev_was_nonref = False

            else:
                # zwykła zmienna / tablica zadeklarowana w tym zakresie
                base_addr = actual_addr
                if (
                    hasattr(self, "array_bounds")
                    and actual_full in self.array_bounds
                ):
                    low, high = self.array_bounds[actual_full]
                    # &s[0] = adres komórki dla s[low] - low
                    base_addr = actual_addr - low

                # ---- OPT: jeśli kolejny adres = poprzedni + 1, użyj tylko INC a ----
                if prev_was_nonref and base_addr == prev_nonref_addr + 1:
                    # w rejestrze 'a' nadal jest poprzednia stała (STORE nie ją zmienia)
                    self.code.append(Code("INC a"))
                else:
                    self.code.extend(self.emit_const(base_addr))

                self.code.append(Code("STORE", fpos))
                prev_nonref_addr = base_addr
                prev_was_nonref  = True

        # CALL entry
        self.code.append(Code("CALL", entry))



    # =========================
    #  GENERATE_CODE
    # =========================

    def generate_code(self):
        if self.program[0] != "prall":
            print("Error: unexpected program root tag.")
            return []

        procs_list = self.procs_to_list(self.program[1])
        self.proc_order = {}
        for idx, p in enumerate(procs_list):
            head = p[2]          # (head, nazwa, args, lineno)
            pname = head[1]
            self.proc_order[pname] = idx

        # są procedury to skok nad nie do main
        if procs_list:
            self.code.append(Code("JUMP", 0, "skok do programu (main)"))
            jump_index = 0

            # generuj procedury
            for p in procs_list:
                self.gen_procedure(p)

            # MAIN
            self.scope = ""
            main = self.program[2]
            if main[0] == "mn_LONG":
                self.decs_to_table(main[1])
                comms = main[2]
            else:
                comms = main[1]

            comm_list = self.comms_to_list(comms)
            self.in_main = True
            main_entry = len(self.code)

            for i, c in enumerate(comm_list):
                self._is_last_in_main = (i == len(comm_list) - 1)
                self.gc_command(c)

            self.in_main = False
            self._is_last_in_main = False
            self.code.append(Code("HALT"))

            self.code[jump_index].arg = main_entry

        else:
            # brak procedur to sam main
            self.scope = ""
            main = self.program[2]
            if main[0] == "mn_LONG":
                self.decs_to_table(main[1])
                comms = main[2]
            else:
                comms = main[1]

            comm_list = self.comms_to_list(comms)
            self.in_main = True

            for i, c in enumerate(comm_list):
                self._is_last_in_main = (i == len(comm_list) - 1)
                self.gc_command(c)

            self.code.append(Code("HALT"))
            self.in_main = False
            self._is_last_in_main = False

        return [c.to_string() for c in self.code]
