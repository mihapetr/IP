from vepar import *

# TODO: razvrstat tipove na smislen nacin
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

# TODO: uskladit s novom verzijom iz robertovog modula
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
# naredba -> pridruzivanje | petlja | kondicional | forsira | vrijedi | test | TOČKAZ
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
# test -> IME UPITNIK SVIJET TOČKAZ

# TODO: nadopunit ostale metode za formule, petlje i grananje
class P(Parser):
    def start(p):
        naredbe = [p.naredba()]
        while not p > KRAJ: naredbe.append(p.naredba())
        return Program(naredbe)
    def naredba(p):
        if ime := p >= T.IME:
            if p >= T.JEDNAKO:
                formula = p.formula()
                p >> T.TOČKAZ
                return Pridruživanje(ime, formula)
            if p >= T.UPITNIK:
                w = p >> T.SVIJET
                p >> T.TOČKAZ
                return Test(w, rt.mem[ime])
        if w := p >= T.SVIJET:
            simb = p >> { T.FORSIRA, T.NEFORSIRA }
            lista_pvar = []
            if p >= T.V_OTV:
                lista_pvar.append(p >> T.PVAR)
                while p >= ZAREZ: lista_pvar.append(p >> T.PVAR)
                p >> T.V_ZATV
            else: lista_pvar.append(p >> T.PVAR)
            return Forsira(w, lista_pvar) if simb ^ T.FORSIRA else Neforsira(w, lista_pvar)
        if pvar := p >= T.PVAR:
            simb = p >> { T.VRIJEDI, T.NEVRIJEDI }
            lista_svijet = []
            if p >= T.V_OTV:
                lista_pvar.append(p >> T.SVIJET)
                while p >= ZAREZ: lista_pvar.append(p >> T.SVIJET)
                p >> T.V_ZATV
            else: lista_pvar.append(p >> T.SVIJET)
            return Vrijedi(pvar, lista_svijet) if simb ^ T.VRIJEDI else Nevrijedi(p, lista_svijet)
        
class Program(AST):
    naredbe: 'naredba[]'
    def izvrši(self):
        rt.mem = Memorija()
        for naredba in self.naredbe: naredba.izvrši()
    
class Pridruživanje(AST):
    definiendum: 'lijevi'
    definiens: 'desni'
    def izvrši(self):
        rt.mem[self.definiendum] = self.definiens

class Svijet:
    sljedbenici: set(Svijet)
    činjenice: set(T.PVAR)

# TODO: testirati test metodu (za to treba unos iz datoteke)
class Test(AST):
    svijet: Svijet
    formula: 'formula'
    def izvrši(self):
        F = self.formula
        if F ^ T.PVAR:
            return F in self.svijet.činjenice
        elif F ^ Negacija:
            return not F.ispod.izvrši()
        elif F ^ Disjunkcija:
            return F.lijeva.izvrši() or F.desna.izvrši()
        elif F ^ Konjunkcija:
            return F.lijeva.izvrši() and F.desna.izvrši()
        elif F ^ Kondicional:
            return F.lijeva.izvrši() <= F.desna.izvrši()
        elif F ^ Bikondicional:
            return F.lijeva.izvrši() == F.desna.izvrši()
        elif F ^ Diamond:
            for sljedbenik in self.svijet.sljedbenici:
                if Test(sljedbenik, F.ispod).izvrši(): return True
            return False
        elif F ^ Box:
            for sljedbenik in self.svijet.sljedbenici:
                if not Test(sljedbenik, F.ispod).izvrši(): return False
            return True

class Forsira(AST):
    svijet: Svijet
    pvars: list(T.PVAR)
    def izvrši():
        for pvar in self.pvars:
            self.svijet.činjenice.add(pvar)

class Neforsira(AST):
    svijet: Svijet
    pvars: list(T.PVAR)
    def izvrši():
        for pvar in self.pvars:
            self.svijet.činjenice.discard(pvar)

class Vrijedi(AST):
    pvar: T.PVAR
    svjetovi: list(Svijet)
    def izvrši():
        for svijet in self.svjetovi:
            svijet.činjenice.add(self.pvar)

class Nevrijedi(AST):
    pvar: T.PVAR
    svjetovi: list(Svijet)
    def izvrši():
        for svijet in self.svjetovi:
            svijet.činjenice.discard(self.pvar)