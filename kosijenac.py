from vepar import *
import csv

class T(TipoviTokena):
    # Tokeni za modalne formule
    NEG, KONJ, DISJ, O_OTV, O_ZATV = '~&|()'
    KOND, BIKOND = '->', '<->'
    BOX, DIAMOND = '[]', '<>'
    class PVAR(Token):
        def optim(self): return self
        def ispis(self): return self.sadržaj.translate(subskript)
        def optim1(self): return self
        def vrijednost(self, w): return (self in w.činjenice)
    # Tokeni za svijetove i modele
    FORSIRA, NEFORSIRA, VRIJEDI, NEVRIJEDI = '|=', '|~', '=|', '~|'
    # FORSIRA_AL, NEFORSIRA_AL, VRIJEDI_AL, NEVRIJEDI_AL = '||-', '||~', '-||', '~||'
    class SVIJET(Token):
        sljedbenici: set(T.SVIJET)
        činjenice: set(T.PVAR)
        def vrijednost(self): return self.sadržaj
    class MODEL(Token):
        nosač: set(T.SVIJET)
        def vrijednost(self): return self.sadržaj
    class IMED(Token):
        def vrijednost(self): return str(self.sadržaj[1:-1])
    # Tokeni za jezik
    TOČKAZ, ZAREZ, V_OTV, V_ZATV, UPITNIK = ';,{}?'
    FOR, IF, ELSE, WHILE, ISPIŠI, KORISTI = 'for', 'if', 'else', 'while', 'ispiši', 'koristi'
    INT, NAT, FORMULA = 'int', 'nat', 'formula'
    JEDNAKO, PLUS,  MINUS, PUTA, NA = '=+-*^'
    JJEDNAKO, PLUSP, PLUSJ, MINUSM, MINUSJ = '==', '++', '+=', '--', '-='
    MANJE, MMANJE, VEĆE = '<', '<<', '>'
    class BROJ(Token):
        def vrijednost(self): return int(self.sadržaj)
    class IME(Token):
        def vrijednost(self): return rt.mem[self]

@lexer
def ml(lex):
    for znak in lex:
        if znak.isspace() : lex.zanemari()
        elif znak == '[':
            lex >> ']'
            yield lex.token(T.BOX)
        elif znak == '<':
            if lex >= '>' : yield lex.token(T.DIAMOND)
            elif lex >= '<': yield lex.token(T.MMANJE)
            elif lex >= '-':
                lex >> '>'
                yield lex.token(T.BIKOND)
            else: yield lex.token(T.MANJE)
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        elif znak == '-':
            if lex >= '>': yield lex.token(T.KOND)
            elif lex >= '-': yield lex.token(T.MINUSM)
            elif lex >= '=': yield lex.token(T.MINUSJ)
            elif lex >= '|':
                lex >> '|'
                yield lex.token(T.VRIJEDI)
            else: yield lex.token(T.MINUS)
        elif znak == '+':
            if lex >= '+': yield lex.token(T.PLUSP)
            elif lex >= '=': yield lex.token(T.PLUSJ)
            else: yield lex.token(T.PLUS)
        elif znak == '~':
            if lex >= '|': 
                yield lex.token(T.NEVRIJEDI if lex >= '|' else T.NEVRIJEDI)
            else: yield lex.token(T.NEG)
        elif znak == '=':
            if lex >= '|': yield lex.token(T.VRIJEDI)
            else: lex.token(T.JJEDNAKO if lex >= '=' else T.JEDNAKO)
        elif znak == '|':
            if lex >= '=': yield lex.token(T.FORSIRA)
            elif lex >= '~': yield lex.token(T.NEFORSIRA)
            elif lex >= '|':
                if lex >= '-': yield lex.token(T.FORSIRA)
                elif lex >= '~': yield lex.token(T.NEFORSIRA)
            else: yield lex.token(T.DISJ)
        elif znak == '#':
            lex - '\n'
            lex.zanemari()
        elif znak == '$':
            lex.zanemari()
            lex + { str.isalnum, '_' }
            yield lex.token(T.PVAR)
        elif znak == '@':
            lex.zanemari()
            lex + { str.isalnum, '_' }
            yield lex.token(T.SVIJET)
        elif znak.isupper():
            lex * { str.isalnum, '_' }
            yield lex.token(T.MODEL)
        elif znak == '\"' or znak == '\'':
            lex + (lambda char: char != znak and char != '.')
            lex >> '.'
            lex >> 'm'
            lex >> 'i'
            lex >> 'r'
            lex >> znak
            yield lex.token(T.IMED)
        elif znak.isalnum() or znak == '_':
            lex * { str.isalnum, '_' }
            yield lex.literal_ili(T.IME)
        else: yield lex.literal

### BKG ###
# start -> naredbe naredba
# naredbe -> '' | naredbe naredba
# naredba  -> petlja | grananje | ispis TOČKAZ | unos TOČKAZ | pridruživanje TOČKAZ | deklaracija TOČKAZ
# naredba -> forsira TOČKAZ | vrijedi TOČKAZ | provjera TOČKAZ | koristi TOČKAZ | TOČKAZ
# pridruživanje -> IME JEDNAKO formula | IME JEDNAKO izraz
# deklaracija -> FORMULA IME JEDNAKO formula | INT IME JEDNAKO izraz | NAT IME JEDNAKO izraz
# formula -> PVAR | NEG formula | DIAMOND formula | BOX formula | O_OTV formula binvez formula O_ZATV
# binvez -> KONJ | DISJ | KOND | BIKOND
# for_operator -> MANJE | VEĆE
# promjena -> PLUSP | MINUSM | PLUSJ BROJ | MINUSJ BROJ
# for -> FOR O_OTV IME# JEDNAKO BROJ TOČKAZ IME# for_operator BROJ TOČKAZ IME# promjena O_ZATV
# blok -> V_OTV naredbe V_ZATV | naredba
# petlja -> for blok
# varijabla -> IME | BROJ
# if_operator -> JJEDNAKO | MANJE | VEĆE
# uvjet -> varijabla | varijabla if_operator varijabla 
# grananje -> IF O_OTV uvjet O_ZATV blok (ELSE blok)?
# varijable -> '' | varijable MMANJE varijabla
# ispis -> ISPIŠI varijable 
# izraz -> član | izraz (PLUS|MINUS) član
# član -> faktor | član PUTA faktor
# faktor -> baza | baza NA faktor | MINUS faktor
# baza -> BROJ | IME(aritmetičkog tipa) | O_OTV izraz O_ZATV 
# tip -> INT | NAT | FORMULA
# forsira -> SVIJET FORSIRA V_OTV lista_pvar V_ZATV | SVIJET NEFORSIRA V_OTV lista_pvar V_ZATV
# forsira -> SVIJET FORSIRA PVAR | SVIJET NEFORSIRA PVAR
# vrijedi -> PVAR VRIJEDI V_OTV lista_svijet V_ZATV | PVAR NEVRIJEDI V_OTV lista_svijet V_ZATV
# vrijedi -> PVAR VRIJEDI SVIJET | PVAR NEVRIJEDI SVIJET
# lista_pvar -> PVAR | PVAR ZAREZ lista_pvar
# lista_svijet -> SVIJET | SVIJET ZAREZ lista_svijet
# provjera -> IME UPITNIK SVIJET | formula UPITNIK SVIJET
# koristi -> KORISTI MODEL
# unos -> MODEL MMANJE IMED

class P(Parser):
    def start(p):
        naredbe = [p.naredba()]
        while not p > KRAJ: naredbe.append(p.naredba())
        return Program(naredbe)

    def naredba(p):
        if p > T.FOR: return p.petlja()
        if p > T.ISPIŠI: return p.ispis()
        if p > T.IF: return p.grananje()
        if p > {T.INT, T.NAT, T.FORMULA}: return p.deklaracija()
        if ime := p >= T.IME:
            if p >= T.JEDNAKO: return p.pridruživanje(ime)
            if p >= T.UPITNIK: return p.provjera(ime)
        if p > T.SVIJET: return p.forsira()
        if p > T.PVAR: return p.vrijedi()
        if p > T.KORISTI: return p.koristi()
        if p > T.MODEL: return p.unos()
        if br := p >= T.BREAK:
            p >> T.TOČKAZ
            return br
        if cont := p >= T.CONTINUE:
            p >> T.TOČKAZ
            return cont
        raise SintaksnaGreška('Nepoznata naredba')

    def koristi(p):
        p >> T.KORISTI
        model = p >> T.MODEL
        p >> T.TOČKAZ
        return Koristi(model)

    def unos(p):
        model = p >> T.MODEL
        datoteke = []
        while p >= T.MMANJE: datoteke.append(p >> T.IMED)
        p >> T.TOČKAZ
        return Unos(model, datoteke)

    def ispis(p):
        p >> T.ISPIŠI
        varijable = []
        while p >= T.MMANJE: varijable.append(p >> {T.IME, T.BROJ})
        p >> T.TOČKAZ
        return Ispis(varijable)

    def petlja(p):
        kriva_varijabla = SemantičkaGreška('Sva tri dijela for-petlje moraju imati istu varijablu')
        
        p >> T.FOR, p >> T.O_OTV
        i = p >> T.IME
        p >> T.JEDNAKO
        početak = p >> {T.BROJ, T.IME}
        p >> T.TOČKAZ

        if (p >> T.IME) != i: raise kriva_varijabla
        for_operator = p >> {T.MANJE, T.VEĆE} 
        granica = p >> T.BROJ
        p >> T.TOČKAZ

        if (p >> T.IME) != i: raise kriva_varijabla
        if minus_ili_plus := p >= {T.PLUSP, T.MINUSM}: promjena = nenavedeno
        elif minus_ili_plus := p >> {T.PLUSJ, T.MINUSJ}: promjena = p >> T.BROJ
        p >> T.O_ZATV

        blok = p.blok()
        return Petlja(i, početak, for_operator, granica, promjena, minus_ili_plus, blok)
    
    #blok može biti ili jedna naredba ili {naredbe*} !!!
    def blok(p):
        naredbe = []
        if p >= T.V_OTV:
            while not p >= T.V_ZATV:
                naredbe.append(p.naredba())
        else: naredbe.append(p.naredba())

        return Blok(naredbe)
    
    def grananje(p):
        p >> T.IF, p >> T.O_OTV
        uvjet = p.uvjet()
        p >> T.O_ZATV
        if_blok = p.blok()
        else_blok = nenavedeno
        if p >= T.ELSE: else_blok = p.blok()
        return Grananje(uvjet, if_blok, else_blok)
    
    def uvjet(p):
        lijeva_strana = p >> {T.IME, T.BROJ}
        op = p >> {T.JJEDNAKO, T.MANJE, T.VEĆE}
        desna_strana = p >> {T.IME, T.BROJ}
        return Uvjet(lijeva_strana, op, desna_strana)
    
    def pridruživanje(p, ime):
        formula = p.formula()
        p >> T.TOČKAZ
        return Pridruživanje(ime, formula)

    def provjera(p, ime):
        w = p >> T.SVIJET
        p >> T.TOČKAZ
        return Provjera(w, ime.vrijednost())
    
    def deklaracija(p):
        tip = p >> {T.INT, T.NAT, T.FORMULA}
        ime = p >> T.IME
        p >> T.JEDNAKO
        vrij = p.formula()  # treba nekako povezat brojeve i formule
        p >> T.TOČKAZ
        return Deklaracija(tip, ime, vrij)

    def izraz(p):
        t = p.član()
        while op := p >= {T.PLUS, T.MINUS}: t = Op(op, t, p.član())
        return t
    
    def član(p):
        t = p.faktor()
        while op := p >= T.PUTA: t = Op(op, t, p.faktor())
        return t
    
    def faktor(p):
        if op := p >= T.MINUS: return Op(op, nenavedeno, p.faktor())
        baza = p.baza()
        if p >= T.NA: return Potencija(baza, p.faktor())
        else: return baza

    def baza(p):
        if elementarni := p >= {T.BROJ, T.IME}: 
            return elementarni
        elif p >> T.O_OTV:
            u_zagradi = p.izraz()
            p >> T.O_ZATV
            return u_zagradi

    def formula(p):
        if varijabla := p >= T.PVAR: return varijabla
        elif p > {T.BOX, T.DIAMOND, T.NEG}:
            klasa, ispod = p.unvez(), p.formula()
            return klasa(ispod)
        elif p >> T.O_OTV:
            l, klasa, d = p.formula(), p.binvez(), p.formula()
            p >> T.O_ZATV
            return klasa(l, d)

    def unvez(p):
        if p >= T.NEG: return Negacija
        elif p >= T.DIAMOND: return Diamond
        elif p >= T.BOX: return Box
        else: raise p.greška()
    
    def binvez(p):
        if p >= T.KONJ: return Konjunkcija
        elif p >= T.DISJ: return Disjunkcija
        elif p >= T.KOND: return Kondicional
        elif p >= T.BIKOND: return Bikondicional
        else: raise p.greška()

    def forsira(p):
        w = p >> T.SVIJET
        simb = p >> { T.FORSIRA, T.NEFORSIRA }
        lista_pvar = []
        if p >= T.V_OTV:
            lista_pvar.append(p >> T.PVAR)
            while p >= ZAREZ: lista_pvar.append(p >> T.PVAR)
            p >> T.V_ZATV
        else: lista_pvar.append(p >> T.PVAR)
        return Forsira(w, lista_pvar, simb)
        
    def vrijedi(p):
        pvar = p >> T.PVAR
        simb = p >> { T.VRIJEDI, T.NEVRIJEDI }
        lista_svijet = []
        if p >= T.V_OTV:
            lista_pvar.append(p >> T.SVIJET)
            while p >= ZAREZ: lista_pvar.append(p >> T.SVIJET)
            p >> T.V_ZATV
        else: lista_pvar.append(p >> T.SVIJET)
        return Vrijedi(pvar, lista_svijet, simb)

##############################################
############## *** AST-ovi *** ###############
##############################################

class Program(AST):
    naredbe: 'naredba[]'
    def izvrši(self):
        rt.mem = Memorija()
        for naredba in self.naredbe: naredba.izvrši()

class Koristi(AST):
    model: T.MODEL
    def izvrši(self):
        rt.mem['model'] = self.model

# TODO: opisati unos iz datoteke.
class Unos(AST):
    model: T.MODEL
    datoteke: list(T.IMED)
    def izvrši(self):
        for dat in self.datoteke:
            with open(dat.vrijednost().replace('.mir', '.csv'), newline='') as csv_dat:
                reader = csv.reader(csv_dat, delimiter=' ')
                prvi_red = next(reader)
                tip = prvi_red[0]
                for i in range(1, len(prvi_red)):
                    novi = T.SVIJET()
                    novi.sadržaj = prvi_red[i]
                    self.model.nosač.add(novi)
                for redak in reader:
                    

    
class Pridruživanje(AST):
    definiendum: T.IME
    definiens: 'formula'
    def izvrši(self):
        rt.mem[self.definiendum] = self.definiens

class Ispis(AST):
    varijable: list(T.IME)
    def izvrši(ispis):
        for varijabla in ispis.varijable:
            print(varijabla.vrijednost(), end=' ')

class Unarna(AST):
    ispod: 'formula'

    def optim(self):
        klasa = type(self)
        ispod_opt = self.ispod.optim()
        if ispod_opt ^ Negacija and self ^ Negacija: return ispod_opt.ispod
        else: return klasa(ispod_opt) 
    
    def optim1(self):
        klasa = type(self)
        if isinstance(self, Diamond):
            ispod_opt = self.ispod.optim1()
            nova_klasa = Negacija(ispod_opt)
            nova_klasa = Box(nova_klasa)
            return Negacija(nova_klasa)
        else: return self

    def ispis(self): 
        return self.veznik + self.ispod.ispis()

class Negacija(Unarna):
    veznik = '¬'
    def vrijednost(self, w): return not self.ispod.vrijednost(w)
    
class Diamond(Unarna):
    veznik = '◆'
    def vrijednost(self, w):
        for sljedbenik in w.sljedbenici:
            if self.ispod.vrijednost(sljedbenik): return True
        return False

class Box(Unarna):
    veznik = '■'
    def vrijednost(self, w):
        for sljedbenik in self.svijet.sljedbenici:
            if not self.ispod.vrijednost(sljedbenik): return False
        return True

class Binarna(AST):
    lijevo: 'formula'
    desno: 'formula'

    def optim(self):
        klasa = type(self)
        lijevo_opt = self.lijevo.optim()
        desno_opt = self.desno.optim()
        return klasa(lijevo_opt, desno_opt)
    
    def optim1(self):
        lijevo_opt = self.lijevo.optim1()
        desno_opt = self.desno.optim1()
        if isinstance(self, Konjunkcija):
            nova_klasa = Negacija(desno_opt)
            nova_klasa = Kondicional(lijevo_opt, nova_klasa)
            return Negacija(nova_klasa)
        elif isinstance(self, Disjunkcija):
            nova_klasa = Negacija(lijevo_opt)
            return Kondicional(nova_klasa, desno_opt)
        elif isinstance(self, Bikondicional):
            lijeva_klasa = Kondicional(lijevo_opt, desno_opt)
            desna_klasa = Kondicional(desno_opt, lijevo_opt)
            desna_klasa = Negacija(desna_klasa)
            nova_klasa = Kondicional(lijeva_klasa, desna_klasa)
            return Negacija(nova_klasa)
        else: return self

    def ispis(self): return '(' + self.lijevo.ispis() + self.veznik + self.desno.ispis() + ')'

class Disjunkcija(Binarna):
    veznik = '∨'
    def vrijednost(self, w): return self.lijevo.vrijednost(w) or self.desno.vrijednost(w)

class Konjunkcija(Binarna):
    veznik = '∧'
    def vrijednost(self, w): return self.lijevo.vrijednost(w) and self.desno.vrijednost(w) 

class Kondicional(Binarna):
    veznik = '→'
    def vrijednost(self, w): return self.lijevo.vrijednost(w) <= self.desno.vrijednost(w) 

class Bikondicional(Binarna):
    veznik = '↔'
    def vrijednost(self, w): return self.lijevo.vrijednost(w) == self.desno.vrijednost(w) 

class Provjera(AST):
    svijet: T.SVIJET
    formula: 'formula'
    def izvrši(self): return self.formula.vrijednost(self.svijet)

class Forsira(AST):
    svijet: T.SVIJET
    pvars: list(T.PVAR)
    simbol: 'T.FORSIRA | T.NEFORSIRA'
    def izvrši(self):
        for pvar in self.pvars:
            if self.simbol == T.FORSIRA:
                self.svijet.činjenice.add(pvar)
            elif self.simbol == T.NEFORSIRA: 
                self.svijet.činjenice.discard(pvar)

class Vrijedi(AST):
    pvar: T.PVAR
    svjetovi: list(T.SVIJET)
    simbol: 'T.VRIJEDI | T.NEVRIJEDI'
    def izvrši(self):
        for svijet in self.svjetovi:
            if self.simbol == T.VRIJEDI:
                svijet.činjenice.add(self.pvar)
            elif self.simbol == T.NEVRIJEDI:
                svijet.činjenice.discard(self.pvar)
