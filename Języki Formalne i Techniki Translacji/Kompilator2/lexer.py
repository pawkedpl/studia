from sly import Lexer


class MyLexer(Lexer):
    # Nazwy tokenów
    tokens = {
        'NUM',
        'PID',

        'PROGRAM', 'PROCEDURE', 'IS', 'IN', 'END',
        'IF', 'THEN', 'ELSE', 'ENDIF',
        'WHILE', 'DO', 'ENDWHILE',
        'REPEAT', 'UNTIL',
        'FOR', 'FROM', 'TO', 'DOWNTO', 'ENDFOR',
        'READ', 'WRITE',

        'GE', 'LE', 'NEQ',  # >=, <=, <>
        'EQ',               # =
        'ASSIGN',           # :=
    }

    # Pojedyncze znaki jako literały
    literals = [
        '+', '-', '*', '/', '%',
        '(', ')', ',', ';',
        '[', ']', ':',
        '<', '>'
    ]

    # Białe znaki
    ignore = ' \t'

    # Komentarze: # ... do końca linii
    @_(r'\#.*')
    def COMMENT(self, t):
        pass

    # Nowe linie
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    # Liczby naturalne
    @_(r'\d+')
    def NUM(self, t):
        t.value = int(t.value)
        return t

    # Słowa kluczowe / identyfikatory
    @_(r'[A-Za-z_][A-Za-z_0-9]*')
    def PID(self, t):
        kw = t.value.upper()
        if kw in {
            'PROGRAM', 'PROCEDURE', 'IS', 'IN', 'END',
            'IF', 'THEN', 'ELSE', 'ENDIF',
            'WHILE', 'DO', 'ENDWHILE',
            'REPEAT', 'UNTIL',
            'FOR', 'FROM', 'TO', 'DOWNTO', 'ENDFOR',
            'READ', 'WRITE'
        }:
            t.type = kw
        else:
            # zwykły identyfikator – w lowercase
            t.value = t.value.lower()
        return t

    # Operatory złożone —  kolejność ma znaczenie
    @_(r'>=')
    def GE(self, t):
        return t

    @_(r'<=')
    def LE(self, t):
        return t

    @_(r'!=')
    def NEQ(self, t):
        return t

    @_(r':=')
    def ASSIGN(self, t):
        return t

    @_(r'=')
    def EQ(self, t):
        return t

    # Błędy leksykalne
    def error(self, t):
        print(f"Nieoczekiwany znak '{t.value[0]}' w linii {self.lineno}")
        self.index += 1
