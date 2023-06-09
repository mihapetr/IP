from vepar import *

class T(TipoviTokena):
    NEG, KONJ, DISJ, O_OTV, O_ZATV = '~&|()'
    KOND, BIKOND = '->', '<->'
    BOX, DIAMOND = '[]', '<>'
    #inertni tokeni iznad su dovoljni za formule, ovi ispod su već za jezik
    TOČKAZ, V_OTV, V_ZATV, ZAREZ, UPITNIK, JEDNAKO, MANJE = ';{},?=<'
    FOR, IF, ELSE, WHILE = 'for', 'if', 'else', 'while'
    INT = 'int'
    FORSIRA, NEFORSIRA, VRIJEDI, NEVRIJEDI = '|=', '|~', '=|', '~|'
    class PVAR(Token):
        def optim(self): return self
        def ispis(self): return self.sadržaj.translate(subskript)
        def optim1(self): return self
    class BROJ(Token):
        def vrijednost(self): return int(self)
    class SVIJET(Token): pass
    class IME(Token): pass

@lexer
def ml(lex):
    for znak in lex:
        if znak.isspace() : lex.zanemari()
        elif znak == '[':
            lex >> ']'
            yield lex.token(T.BOX)
        elif znak == '<':
            if lex >= '>' : yield lex.token(T.DIAMOND)
            elif lex >= '-':
                lex >> '>'
                yield lex.token(T.BIKOND)
            else: yield lex.token(T.MANJE)
        elif znak == 'P':
            lex.prirodni_broj('')
            yield lex.token(T.PVAR)
        elif znak.isdecimal():
            lex.prirodni_broj('')
            yield lex.token(T.BROJ)
        elif znak == '-':
            lex >> '>'
            yield lex.token(T.KOND)
        elif znak == '~':
            if lex >= '|': yield lex.token(T.NEVRIJEDI)
            else: yield lex.token(T.NEG)
        elif znak == '=':
            if lex >= '|': yield lex.token(T.VRIJEDI)
            else: yield lex.token(T.JEDNAKO)
        elif znak == '|':
            if lex >= '=': yield lex.token(T.FORSIRA)
            elif lex >= '~': yield lex.token(T.NEFORSIRA)
            else: yield lex.token(T.DISJ)
        elif znak == '#':
            lex - '\n'
            lex.zanemari()
        elif znak == '@':
            lex + str.isalnum
            yield lex.token(T.SVIJET)
        else: yield lex.literal_ili(T.IME)

### BKG ###
# start -> naredba | start naredba
# naredba -> pridruzivanje | petlja | kondicional | forsira | vrijedi | TOČKAZ
# pridruzivanje -> IME JEDNAKO formula TOČKAZ | INT IME JEDNAKO BROJ TOČKAZ
# formula -> PVAR | NEG formula | DIAMOND formula | BOX formula | O_OTV formula binvez formula O_ZATV
# binvez -> KONJ | DISJ | KOND | BIKOND
# petlja -> for naredba | for V_OTV start V_ZATV | while naredba | while V_OTV start V_ZATV
# kondicional -> if naredba | if V_OTV start V_ZATV
# forsira -> SVIJET FORSIRA V_OTV lista_pvar V_ZATV | SVIJET NEFORSIRA V_OTV lista_pvar V_ZATV
# vrijedi -> PVAR VRIJEDI V_OTV lista_svijet V_ZATV | PVAR NEVRIJEDI V_OTV lista_svijet V_ZATV
# lista_pvar -> PVAR | PVAR, lista_pvar
# lista_svijet -> SVIJET | SVIJET, lista_svijet
# for -> FOR O_OTV pridruzivanje uvjet TOČKAZ inkrement O_ZATV
# while -> WHILE O_OTV uvjet O_ZATV
# if -> IF O_OTV uvjet O_ZATV