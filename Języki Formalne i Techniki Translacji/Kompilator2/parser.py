from sly import Parser
from lexer import MyLexer


class MyParser(Parser):
    tokens = MyLexer.tokens

    precedence = (
        ('left', '+', '-'),
        ('left', '*', '/', '%'),
    )

    # =========================================
    #  PROGRAM
    # =========================================

    @_('procedures main')
    def program(self, p):
        return ('prall', p.procedures, p.main)

    @_('main')
    def program(self, p):
        return ('prall', "procs_EMPTY", p.main)

    # =========================================
    #  LISTA PROCEDUR
    # =========================================

    @_('procedure')
    def procedures(self, p):
        return p.procedure

    @_('procedures procedure')
    def procedures(self, p):
        proc = p.procedure
        tag = proc[0]         # procs_LONG / procs_SHORT
        prev = p.procedures
        return (tag, prev, *proc[2:])

    # =========================================
    #  PROCEDURA
    # =========================================

    @_('PROCEDURE PID "(" args_decl_opt ")" IS declarations IN commands END')
    def procedure(self, p):
        head = ('head', p.PID, p.args_decl_opt, p.lineno)
        return ('procs_LONG', "procs_EMPTY", head, p.declarations, p.commands)

    @_('PROCEDURE PID "(" args_decl_opt ")" IS IN commands END')
    def procedure(self, p):
        head = ('head', p.PID, p.args_decl_opt, p.lineno)
        return ('procs_SHORT', "procs_EMPTY", head, p.commands)

    # =========================================
    #  ARGUMENTY FORMALNE PROCEDUR
    #  (T s, I n, O c lub po prostu x, y ...)
    # =========================================

    @_('args_items')
    def args_decl_opt(self, p):
        return p.args_items

    @_('')
    def args_decl_opt(self, p):
        return None

    # lista argumentów
    @_('arg_item')
    def args_items(self, p):
        # pojedynczy
        return p.arg_item

    @_('args_items "," arg_item')
    def args_items(self, p):
        # dokładamy kolejny: ('ard_REC_PID', prev, name, mode, lineno)
        prev = p.args_items
        item = p.arg_item   # ('ard_PID', name, mode, ln)
        return ('ard_REC_PID', prev, item[1], item[2], item[3])

    # jeden parametr:
    #   I a   /   O c   /   T s   /   n
    @_('PID PID')
    def arg_item(self, p):
        mode = self._mode_from_pid(p.PID0)
        name = p.PID1
        return ('ard_PID', name, mode, p.lineno)

    @_('PID')
    def arg_item(self, p):
        # brak przedrostka → domyślnie INOUT
        mode = 'INOUT'
        name = p.PID
        return ('ard_PID', name, mode, p.lineno)

    def _mode_from_pid(self, pid):
        # pid to string w lowercase
        if pid == 'i':
            return 'IN'
        if pid == 'o':
            return 'OUT'
        if pid == 't':
            # T – tablica, ale tryb przekazywania jak INOUT
            return 'INOUT'
        # cokolwiek innego traktujemy jako brak przedrostka
        return 'INOUT'

    # =========================================
    #  MAIN
    # =========================================

    @_('PROGRAM IS declarations IN commands END')
    def main(self, p):
        return ('mn_LONG', p.declarations, p.commands, p.lineno)

    @_('PROGRAM IS IN commands END')
    def main(self, p):
        return ('mn_SHORT', p.commands, p.lineno)

    # =========================================
    #  DEKLARACJE (w tym tablice)
    # =========================================

    @_('PID')
    def declarations(self, p):
        return ('decs_PID', p.PID, p.lineno)

    @_('PID "[" NUM ":" NUM "]"')
    def declarations(self, p):
        return ('decs_ARRAY', p.PID, p.NUM0, p.NUM1, p.lineno)

    @_('declarations "," PID')
    def declarations(self, p):
        return ('decs_REC_PID', p.declarations, p.PID, p.lineno)

    @_('declarations "," PID "[" NUM ":" NUM "]"')
    def declarations(self, p):
        return ('decs_REC_ARRAY', p.declarations, p.PID, p.NUM0, p.NUM1, p.lineno)

    # =========================================
    #  LISTA KOMEND
    # =========================================

    @_('command')
    def commands(self, p):
        return ('comms_SINGLE', p.command)

    @_('commands command')
    def commands(self, p):
        return ('comms_REC', p.commands, p.command)

    # =========================================
    #  KOMENDY
    # =========================================

    # READ id;
    @_('READ identifier ";"')
    def command(self, p):
        return ('comm_READ', p.identifier, p.lineno)

    # WRITE value;
    @_('WRITE value ";"')
    def command(self, p):
        return ('comm_WRITE', p.value, p.lineno)

    # id := expr;
    @_('identifier ASSIGN expression ";"')
    def command(self, p):
        return ('comm_ASSIGN', p.identifier, p.expression, p.lineno)

    # IF cond THEN ... ENDIF
    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        return ('comm_IF', p.condition, p.commands, p.lineno)

    # IF cond THEN ... ELSE ... ENDIF
    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, p):
        return ('comm_IF_ELSE', p.condition, p.commands0, p.commands1, p.lineno)

    # WHILE cond DO ... ENDWHILE
    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        return ('comm_WHILE', p.condition, p.commands, p.lineno)

    # REPEAT ... UNTIL cond;
    @_('REPEAT commands UNTIL condition ";"')
    def command(self, p):
        return ('comm_REPEAT', p.commands, p.condition, p.lineno)

    # FOR i FROM v1 TO v2 DO ... ENDFOR
    @_('FOR PID FROM value TO value DO commands ENDFOR')
    def command(self, p):
        return ('comm_FOR_UP', p.PID, p.value0, p.value1, p.commands, p.lineno)

    # FOR i FROM v1 DOWNTO v2 DO ... ENDFOR
    @_('FOR PID FROM value DOWNTO value DO commands ENDFOR')
    def command(self, p):
        return ('comm_FOR_DOWN', p.PID, p.value0, p.value1, p.commands, p.lineno)

    # wywołanie procedury: nazwa(arg,...);
    @_('PID "(" args_opt ")" ";"')
    def command(self, p):
        call = ('pcall', p.PID, p.args_opt, p.lineno)
        return ('comm_CALL', call, p.lineno)

    # =========================================
    #  ARGUMENTY WYWOŁANIA
    # =========================================

    @_('args')
    def args_opt(self, p):
        return p.args

    @_('')
    def args_opt(self, p):
        return None

    @_('PID')
    def args(self, p):
        return ('ar_PID', p.PID)

    @_('args "," PID')
    def args(self, p):
        return ('ar_REC', p.args, p.PID)

    # =========================================
    #  IDENTYFIKATORY (skalar / tablica)
    # =========================================

    @_('PID')
    def identifier(self, p):
        return ('id_PID', p.PID, p.lineno)

    @_('PID "[" PID "]"')
    def identifier(self, p):
        return ('id_ARR_PID', p.PID0, p.PID1, p.lineno)

    @_('PID "[" NUM "]"')
    def identifier(self, p):
        return ('id_ARR_NUM', p.PID, p.NUM, p.lineno)

    # =========================================
    #  VALUE / EXPRESSION
    # =========================================

    @_('NUM')
    def value(self, p):
        return ('val_NUM', p.NUM)

    @_('identifier')
    def value(self, p):
        return ('val_ID', p.identifier)

    @_('value')
    def expression(self, p):
        return ('expr_VAL', p.value)

    @_('value "+" value')
    def expression(self, p):
        return ('expr_OP', p.value0, '+', p.value1, p.lineno)

    @_('value "-" value')
    def expression(self, p):
        return ('expr_OP', p.value0, '-', p.value1, p.lineno)

    @_('value "*" value')
    def expression(self, p):
        return ('expr_OP', p.value0, '*', p.value1, p.lineno)

    @_('value "/" value')
    def expression(self, p):
        return ('expr_OP', p.value0, '/', p.value1, p.lineno)
    
    @_('value "%" value')
    def expression(self, p):
        return ('expr_OP', p.value0, '%', p.value1, p.lineno)

    # =========================================
    #  WARUNKI
    # =========================================

    # x > y
    @_('value ">" value')
    def condition(self, p):
        return ('cond', p.value0, '>', p.value1, p.lineno)

    # x >= y
    @_('value GE value')
    def condition(self, p):
        return ('cond', p.value0, '>=', p.value1, p.lineno)

    # x = y
    @_('value EQ value')
    def condition(self, p):
        return ('cond', p.value0, '=', p.value1, p.lineno)

    # x <= y  ->  y >= x
    @_('value LE value')
    def condition(self, p):
        return ('cond', p.value1, '>=', p.value0, p.lineno)
    
    # x < y  ->  y > x
    @_('value "<" value')
    def condition(self, p):
        return ('cond', p.value1, '>', p.value0, p.lineno)

    # x != y
    @_('value NEQ value')
    def condition(self, p):
        return ('cond', p.value0, '!=', p.value1, p.lineno)


    # =========================================
    #  BŁĘDY
    # =========================================

    def error(self, p):
        if p:
            print(f"sly: Syntax error at line {p.lineno}, token={p.type}")
        else:
            print("sly: Syntax error at EOF")
