from vepar import *
import csv

subskript = str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉')
class PrekidBreak(NelokalnaKontrolaToka): """Signal koji šalje naredba break."""
class PrekidContinue(NelokalnaKontrolaToka): """Signal koji šalje naredba continue."""

class T(TipoviTokena):
    # Tokeni za modalne formule
    NEG, KONJ, DISJ, O_OTV, O_ZATV = '~&|()'
    KOND, BIKOND = '->', '<->'
    BOX, DIAMOND = '[]', '<>'
    class PVAR(Token):
        def optim(self): return self
        def ispis(self): return self.sadržaj.translate(subskript)
        def optim1(self): return self
        def vrijednost(self, w): return (self.sadržaj in w.činjenice)
        def __eq__(self, o): return self.ispis() == o.ispis
    # Tokeni za svijetove i modele
    FORSIRA, NEFORSIRA, VRIJEDI, NEVRIJEDI = '|=', '|~', '=|', '~|'
    class SVIJET(Token):
        sljedbenici: 'set(T.SVIJET)'
        činjenice: 'set(T.PVAR)'
        def vrijednost(self): return self.sadržaj
    class MODEL(Token):
        pvars: 'set(T.PVAR)'
        nosač: 'set(T.SVIJET)'
        def vrijednost(self): return self.sadržaj
        def nađi_svijet(self, naziv): 
            for svijet in self.nosač:
                if svijet.sadržaj == naziv:
                    return svijet
            return nenavedeno
        def nađi_pvar(self, naziv): 
            for pvar in self.pvars:
                if pvar.sadržaj == naziv:
                    return pvar
            return nenavedeno
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
        def vrijednost(self): return rt.mem[self][0]
        def tip(self): return rt.mem[self][1]
    class CONTINUE(Token):
        literal = 'continue'
        def izvrši(self): raise PrekidContinue
    class BREAK(Token):
        literal = 'break'
        def izvrši(self): raise PrekidBreak

# donje dvije klase sluze samo za lijepo ispisivanje poruke prilikom nekompatibilnih tipova
# napravio sam to tako da se lako moze prosirivati kada nove tipove budemo ubacivali
class Tip(enum.Enum):
    N = 'NAT'
    Z = 'INT'

class GreskaTipova:
    def krivi_tip(self, ime, tip1, tip2):
        raise SemantičkaGreška(f"IME '{ime}': tipovi ne odgovaraju: {tip1.name} vs. {tip2.name}")

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
            else: yield lex.token(T.JJEDNAKO if lex >= '=' else T.JEDNAKO)
        elif znak == '|':
            if lex >= '=': yield lex.token(T.FORSIRA)
            elif lex >= '~': yield lex.token(T.NEFORSIRA)
            elif lex >= '|':
                if lex >= '-': yield lex.token(T.FORSIRA)
                elif lex >= '~': yield lex.token(T.NEFORSIRA)
            else: yield lex.token(T.DISJ)
        elif znak == '\\':
            lex >> '\\'
            lex - '\n'
            lex.zanemari()
        elif znak == '#':
            lex >> str.isalpha
            lex * { str.isalnum, '_' }
            yield lex.token(T.IME)
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
        else: yield lex.literal(T)
### BKG ###
# start -> naredbe naredba
# naredbe -> '' | naredbe naredba
# naredba  -> petlja | grananje | ispis TOČKAZ | unos TOČKAZ | pridruživanje TOČKAZ | deklaracija TOČKAZ
# naredba -> forsira TOČKAZ | vrijedi TOČKAZ | provjera TOČKAZ | koristi TOČKAZ | TOČKAZ
# pridruživanje -> IME JEDNAKO formula | IME JEDNAKO izraz
# deklaracija -> FORMULA IME JEDNAKO formula | INT IME JEDNAKO izraz | NAT IME JEDNAKO izraz
# formula -> PVAR | NEG formula | DIAMOND formula | BOX formula
# formula -> O_OTV formula binvez formula O_ZATV | IME (formule)
# binvez -> KONJ | DISJ | KOND | BIKOND
# for_operator -> MANJE | VEĆE
# promjena -> PLUSP | MINUSM | PLUSJ BROJ | MINUSJ BROJ
# for -> FOR O_OTV IME# JEDNAKO BROJ TOČKAZ IME# for_operator BROJ TOČKAZ IME# promjena O_ZATV
# blok -> V_OTV naredbe V_ZATV | naredba
# petlja -> for blok    
# varijabla -> IME(aritmetičko, formula, model, svijet) | BROJ | FORMULA  
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
# lista_pvar -> PVAR | PVAR ZAREZ lista_pvar
# forsira -> SVIJET FORSIRA V_OTV lista_pvar V_ZATV | SVIJET NEFORSIRA V_OTV lista_pvar V_ZATV
# forsira -> SVIJET FORSIRA PVAR | SVIJET NEFORSIRA PVAR
# lista_svijet -> SVIJET | SVIJET ZAREZ lista_svijet
# vrijedi -> PVAR VRIJEDI V_OTV lista_svijet V_ZATV | PVAR NEVRIJEDI V_OTV lista_svijet V_ZATV
# vrijedi -> PVAR VRIJEDI SVIJET | PVAR NEVRIJEDI SVIJET
# provjera -> IME (formule) UPITNIK SVIJET | formula UPITNIK SVIJET
# koristi -> KORISTI MODEL V_OTV lista_svijet TOČKAZ lista_pvar V_ZATV
# unos -> MODEL MMANJE IMED (moze ucitati vise datoteka)

# prilikom "definiranja" modela u {} navodimo popis svjetova. U model staviti metodu koja vraća 
# odgovarajući token na temelju sadržaja ispis modela ostvariti uz pomoc ispisa svjetova
# problem kompatibilnosti int i nat rijesen uz koristenje liste koja predstavlja par tipa i vrijednosti
# model -> veliko; formula -> malo; int, nat -> #  
# komentar: //

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
        return p.formula()

    def koristi(p):
        p >> T.KORISTI
        model = p >> T.MODEL
        model.nosač = []
        model.pvars = []
        p >> T.V_OTV
        svijet = p >> T.SVIJET
        svijet.sljedbenici = []
        svijet.činjenice = []
        model.nosač.append(svijet)
        while p >= T.ZAREZ:
            svijet = p >> T.SVIJET
            svijet.sljedbenici = []
            svijet.činjenice = []
            model.nosač.append(svijet)
        p >> T.TOČKAZ
        pvar = p >> T.PVAR
        model.pvars.append(pvar)
        while p >= T.ZAREZ:
            pvar = p >> T.PVAR
            model.pvars.append(pvar)
        p >> T.V_ZATV
        p >> T.TOČKAZ
        return Koristi(model)

    def unos(p):
        model = p >> T.MODEL
        datoteke = []
        while p >= T.MMANJE: datoteke.append(p >> T.IMED)
        p >> T.TOČKAZ
        return Unos(model, datoteke)
    
    def petlja(p):
        kriva_varijabla = SemantičkaGreška('Sva tri dijela for-petlje moraju imati istu varijablu')
        
        p >> T.FOR, p >> T.O_OTV
        i = p >> T.IME
        p >> T.JEDNAKO
        početak = p >> {T.BROJ, T.IME}
        p >> T.TOČKAZ

        if (p >> T.IME) != i: raise kriva_varijabla
        for_operator = p >> {T.MANJE, T.VEĆE} # ovdje se lako doda ako hocemo podrzati jos neke operatore
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
    
    def ispis(p): 
        p >> T.ISPIŠI
        varijable = []
        while p >= T.MMANJE: varijable.append(p >> {T.IME, T.BROJ, T.SVIJET, T.MODEL})
        p >> T.TOČKAZ
        return Ispis(varijable)
    
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
        op = p >> {T.JJEDNAKO, T.MANJE, T.VEĆE} #ovdje se dodaju if_operatori ako zelimo prosiriti
        desna_strana = p >> {T.IME, T.BROJ}
        return Uvjet(lijeva_strana, op, desna_strana)
    
    def pridruživanje(p):
        ime_varijable = p >> T.IME
        p >> T.JEDNAKO
        # provjera koji nam je tip s lijeve strane (samo formule još dolaze)
        if ime_varijable.tip() ^ T.FORMULA:
            vrijednost = p.formula()
        else:
            vrijednost = p.izraz()
        p >> T.TOČKAZ
        return Pridruživanje(ime_varijable, vrijednost)
    
    def deklaracija(p):
        tip = p >> {T.INT, T.NAT, T.FORMULA}
        ime = p >> T.IME
        p >> T.JEDNAKO
        # U ovisnosti sto je s lijeve strane, treba zvati odg. metodu 
        if tip ^ T.FORMULA:
            vrij = p.formula()
        else:
            vrij = p.izraz()
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
            if elementarni.tip() ^ { T.INT, T.NAT }:
                return elementarni
        elif p >> T.O_OTV:
            u_zagradi = p.izraz()
            p >> T.O_ZATV
            return u_zagradi

    def formula(p):
        if varijabla := p >= T.PVAR: return varijabla
        elif f := p >= T.IME: return f
        elif p > {T.BOX, T.DIAMOND, T.NEG}:
            klasa, ispod = p.unvez(), p.formula()
            return klasa(ispod)
        elif p >> T.O_OTV:
            l, klasa, d = p.formula(), p.binvez(), p.formula()
            p >> T.O_ZATV
            return klasa(l, d)
        raise SintaksnaGreška('Nepoznata naredba')
        
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

class Program(AST):
    naredbe: 'barem jedna naredba'

    def izvrši(program):
        try:
            for naredba in program.naredbe: naredba.izvrši()
        except PrekidBreak: raise SemantičkaGreška('Nedozvoljen break izvan petlje')
        except PrekidContinue: raise SemantičkaGreška('Nedozvoljen continue izvan petlje')

class Koristi(AST):
    model: T.MODEL
    def izvrši(self):
        rt.mem['using'] = self.model

class Unos(AST):
    model: T.MODEL
    datoteke: 'list(T.IMED)'
    def izvrši(self):
        for dat in self.datoteke:
            with open(dat.vrijednost(), newline='') as csv_dat:
                reader = csv.reader(csv_dat, delimiter=' ')
                prvi_red = next(reader)
                tip = prvi_red[0][:3]
                if tip == 'rel':
                    svjetovi = []
                elif tip == 'val': 
                    pvars = []
                else:
                    raise IOError('Neispravan tip datoteke: mora biti "rel" ili "val".')
                    return -1
                if tip == 'rel':
                    for i in range(1, len(prvi_red)):
                        if novi := self.model.nađi_svijet('@' + prvi_red[i]):
                            if novi in svjetovi:
                                raise IOError('Svijet se navodi dvaput.')
                            else: svjetovi.append(novi)
                        else: raise IOError('Svijet nije deklariran.')
                else:
                    for i in range(1, len(prvi_red)):
                        if nova := self.model.nađi_pvar('$' + prvi_red[i]):
                            if nova in pvars:
                                raise IOError('Propozicionalna varijabla navodi se dvaput.')
                            else: pvars.append(nova)
                        else: raise IOError('Propozicionalna varijabla nije deklarirana.')
                for redak in reader:
                    lijevi = redak[0]
                    for i in range(1, len(redak)):
                        if str.toupper(redak[i][0]) in ['T', '1', 'Y', 'I', 'D', 'O']:
                            if tip == 'rel':
                                lijevi.sljedbenici.append(svjetovi[i + 1])
                            else: lijevi.činjenice.append(pvars[i + 1])
                        elif str.toupper(redak[i][0]) in ['F', '0', 'N', 'L', 'N', 'X']:
                            if tip == 'rel':
                                lijevi.sljedbenici.remove(svjetovi[i + 1])
                            else: lijevi.činjenice.remove(pvars[i + 1])
                        else: raise IOError('Neispravna oznaka istinitosti u tablici.')
                        
class Petlja(AST):
    varijabla: 'IME'
    početak: 'BROJ | varijabla'
    operator: '(<|>)' #mogli bi bit još podržani <= ili >=, ali nije da time dobivamo na ekspresivnosti jezika; eventualno dodati !=
    granica: 'BROJ'
    promjena: 'BROJ?'
    predznak: '(+|-)'
    blok: 'naredba*'

    def izvrši(petlja):
        kv = petlja.varijabla
        rt.mem[kv] = petlja.početak.vrijednost()
        while rt.mem[kv] < petlja.granica.vrijednost() if petlja.operator ^ T.MANJE else rt.mem[kv] > petlja.granica.vrijednost():
            try:
                petlja.blok.izvrši()
            except PrekidBreak: break
            except PrekidContinue: #nazalost dupliciram kod radi ispravnog rada continue, kasnije mozemo popraviti
                prom = petlja.promjena
                if petlja.predznak ^ T.MINUSJ or petlja.predznak ^ T.MINUSM:
                    rt.mem[kv] -= prom.vrijednost() if prom else 1
                else: rt.mem[kv] += prom.vrijednost() if prom else 1
                continue
            prom = petlja.promjena
            if petlja.predznak ^ T.MINUSJ or petlja.predznak ^ T.MINUSM:
                rt.mem[kv] -= prom.vrijednost() if prom else 1
            else: rt.mem[kv] += prom.vrijednost() if prom else 1

class Blok(AST):
    naredbe: 'naredba*'
    
    def izvrši(blok):
        for naredba in blok.naredbe:
            naredba.izvrši()

class Ispis(AST):
    varijable: 'IME*'

    def izvrši(ispis):
        for varijabla in ispis.varijable:
            print(varijabla.vrijednost(), end = ' ')

class Uvjet(AST):
    lijeva: '(IME|BROJ)'
    operator: '(==|<|>)'
    desna: '(IME|BROJ)'

    def ispunjen(uvjet):
        if uvjet.operator ^ T.JJEDNAKO:
            return uvjet.lijeva.vrijednost() == uvjet.desna.vrijednost()
        elif uvjet.operator ^ T.VEĆE:
            return uvjet.lijeva.vrijednost() > uvjet.desna.vrijednost()
        elif uvjet.operator ^ T.MANJE:
            return uvjet.lijeva.vrijednost() < uvjet.desna.vrijednost()
        else: raise SintaksnaGreška('Nepodržan operator u if-uvjetu')

class Grananje(AST):
    uvjet: 'log'
    onda: 'naredba'
    inače: 'naredba'

    def izvrši(grananje):
        if grananje.uvjet.ispunjen(): grananje.onda.izvrši()
        elif grananje.inače: grananje.inače.izvrši()

class Pridruživanje(AST):
    varijabla: 'IME'
    vrij: '(varijabla | BROJ)'

    def izvrši(pridruživanje):
        klasa = type(pridruživanje.varijabla)
        if pridruživanje.varijabla in rt.mem:
            rt.mem[pridruživanje.varijabla] = pridruživanje.vrij.vrijednost()
        else: return rt.mem[pridruživanje.varijabla] #jer ovo vraca bas ono upozorenje koje nam treba

class Deklaracija(AST):
    tip: 'neki od podrzanih tipova'
    ime: 'IME'
    vrij: 'varijabla | BROJ'

    def izvrši(deklaracija):                                              
        # na ovaj nacin bi sva ostala nepodudaranja u tipovima mogli rjesavati
        # uoči da se ovo mora rješavat u AST-u, a ne u odgovarajućoj metodi parsera
        if deklaracija.tip ^ T.NAT and deklaracija.vrij.vrijednost() < 0: 
            tip1 = Tip.N
            tip2 = Tip.Z
            greska = GreskaTipova()
            greska.krivi_tip(deklaracija.ime.sadržaj, tip1, tip2)

        # prilagodit jos za formulu
        if deklaracija.ime in rt.mem:
            raise deklaracija.ime.redeklaracija()
        else: rt.mem[deklaracija.ime] = [deklaracija.vrij.vrijednost(), deklaracija.tip]

class Op(AST):
    op: 'T'
    lijevo: 'izraz?'
    desno: 'izraz'

    def vrijednost(self):
        if self.lijevo is nenavedeno: l = 0  
        else: l = self.lijevo.vrijednost()
        o, d = self.op, self.desno.vrijednost()
        if o ^ T.PLUS: return l + d
        elif o ^ T.MINUS: return l - d
        elif o ^ T.PUTA: return l * d

class Potencija(AST):
    baza: 'elementarni | izraz'
    eksponent: 'faktor'

    def vrijednost(self):
        return self.baza.vrijednost() ** self.eksponent.vrijednost()

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

    def __eq__(self, o): return jednaki(self.ispod, o.ispod)

    def ispis(self): 
        return self.veznik + self.ispod.ispis()
    
    #provjeri ovo
    def izvrši(self):
        return self.ispis()

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

    def __eq__(self, o): return jednaki(self.lijevo, o.lijevo) and jednaki(self.desno, o.desno)

    def ispis(self): return '(' + self.lijevo.ispis() + self.veznik + self.desno.ispis() + ')'

    #provjeri ovo
    def izvrši(self):
        return self.ispis()

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
    pvars: 'list(T.PVAR)'
    simbol: 'T.FORSIRA | T.NEFORSIRA'
    def izvrši(self):
        if self.svijet not in rt.mem['using'].nosač:
            raise SemantičkaGreška('Svijet nije deklariran.')
        for pvar in self.pvars:
            if self.simbol == T.FORSIRA:
                self.svijet.činjenice.append(pvar.sadržaj)
            elif self.simbol == T.NEFORSIRA: 
                self.svijet.činjenice.remove(pvar.sadržaj)

class Vrijedi(AST):
    pvar: T.PVAR
    svjetovi: 'list(T.SVIJET)'
    simbol: 'T.VRIJEDI | T.NEVRIJEDI'
    def izvrši(self):
        for svijet in self.svjetovi:
            if svijet not in rt.mem['using'].nosač:
                raise SemantičkaGreška('Svijet nije deklariran.')
            elif self.simbol == T.VRIJEDI:
                svijet.činjenice.append(self.pvar.sadržaj)
            elif self.simbol == T.NEVRIJEDI:
                svijet.činjenice.remove(self.pvar.sadržaj)


def optimiziraj(formula):
    """Pretvara formulu (AST) u formulu koja od veznika ima samo kondicional i negaciju; prije te pretvorbe su još uklonjene dvostruke negacije"""

    nova = formula.optim() #prije optimizacije da dobijemo samo negaciju i kondicional uklanjamo redundantne negacije
    nova = nova.optim1() #kreiramo ekvivalentnu formulu koja ima samo negaciju, kondicional i box od veznika
    return nova.optim() #nakon dobivanja ekvivalentne formule opet se mogu javiti redundantne negacije pa ih zato još jednom mičemo

def jednaki(f1, f2):
    klasa1 = type(f1)
    klasa2 = type(f2)

    if klasa1 != klasa2:
        return False
    return f1 == f2

# provjerava je li formula f shema aksioma A1
# NISAM TESTIRAO jer još nemamo implementiranu varijablu tipa formula
def shemaA1(f):
    optimiziraj(f)
    f.ispis()
    print()
    if not f ^ Kondicional:
        return False
    lijeva_formula = f.lijevo
    desna_formula = f.desno
    if not desna_formula ^ Kondicional:
        return False
    return lijeva_formula.ispis() == desna_formula.desna.ispis()
    
prikaz(kod := P('''
    koristi M { @svijet, @world, @za_warudo, @el_mundo; $pada_kisa, $ulice_su_mokre, $prolazi_cisterna };
    M << "rel_dat.mir" << "val_dat.mir";
    int br = 5;
    formula a_1 = ($pada_kisa -> $ulice_su_mokre);
    // formula nuzno_a1 = [](a_1);
    ispiši << a_1 ? @svijet << a_1 ? @world;
    // ispiši << nuzno_a1 ? @el_mundo << nuzno_a1 ? @za_warudo;
'''), 8)
kod.izvrši()