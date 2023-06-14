# korštenje main funkcije importane iz miha_module pozivom: main()
# jedina funkcija koja se poziva u main.py na kraju skripte
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
        def vrijednost(self, w): return (self in w.činjenice)
    class TRUE(Token):
        literal = "T"
        def vrijednost(self, w): return True
    class FALSE(Token):
        literal = "F"
        def vrijednost(self, w): return False
    # Tokeni za svijetove i modele
    FORSIRA, NEFORSIRA, VRIJEDI, NEVRIJEDI = '|=', '|~', '=|', '~|'
    class SVIJET(Token):
        sljedbenici: 'set(T.SVIJET)'
        činjenice: 'set(T.PVAR)'
        def vrijednost(self): return self.sadržaj
        def ispis(self):
            za_ispis = self.sadržaj + ': {'
            for sljedbenik in self.sljedbenici:
                za_ispis += ' ' + sljedbenik.sadržaj
            za_ispis += '; '
            for pvar in self.činjenice:
                za_ispis += pvar.sadržaj + ' '
            za_ispis += '} '
            return za_ispis.translate(subskript)
    class MODEL(Token):
        pvars: 'set(T.PVAR)'
        nosač: 'set(T.SVIJET)'
        def vrijednost(self): return self.sadržaj
        def ispis(self):
            za_ispis = self.sadržaj + ': {'
            for svijet in self.nosač:
                za_ispis += ' ' + svijet.sadržaj
            za_ispis += '; '
            for pvar in self.pvars:
                za_ispis += pvar.sadržaj + ' '
            za_ispis += '} '
            return za_ispis.translate(subskript)
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
    FOR, IF, ELSE, WHILE, ISPIŠI, UNESI, KORISTI, FOREACH = 'for', 'if', 'else', 'while', 'ispiši', 'unesi', 'koristi', 'foreach'
    INT, NAT, FORMULA = 'int', 'nat', 'formula'
    JEDNAKO, PLUS,  MINUS, PUTA, NA = '=+-*^'
    JJEDNAKO, PLUSP, PLUSJ, MINUSM, MINUSJ = '==', '++', '+=', '--', '-='
    MANJE, MMANJE, VEĆE = '<', '<<', '>'
    class BROJ(Token):
        def vrijednost(self): return int(self.sadržaj)
        def ispis(self): return self.sadržaj
    class IME(Token):
        def vrijednost(self): return rt.mem[self][0]
        def tip_varijable(self): return rt.mem[self][1]
        def ispis(self):
            if (len(rt.mem[self]) == 1):
                return rt.mem[self][0]
            elif self.tip_varijable() ^ {T.INT, T.NAT}:
                return self.vrijednost()
            elif self.tip_varijable() ^ T.FORMULA: 
                return self.vrijednost().ispis()
            else: raise SemantičkaGreška("Traženje nepoznate vrijednosti!")
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
        elif znak == '/':
            lex >> '/'
            lex - '\n'
            lex.zanemari()
        elif znak == '#':
            lex >> str.isalpha
            lex * { str.isalnum, '_' }
            yield lex.token(T.IME)
        elif znak == '$':
            lex + { str.isalnum, '_' }
            yield lex.token(T.PVAR)
        elif znak == '@':
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
# naredba  -> petlja | grananje | ispis TOČKAZ | pridruživanje TOČKAZ | deklaracija TOČKAZ | BREAK TOČKAZ | CONTINUE TOČKAZ
# for_operator -> MANJE | VEĆE ##NAPOMENA: ovdje nadodati ako zelimo jos nesto u for_operatoru (možda još !=)
# izraz -> član | izraz (PLUS|MINUS) član
# član -> faktor | član PUTA faktor
# faktor -> baza | baza NA faktor | MINUS faktor
# baza -> BROJ | IME(aritmetičkog tipa) | O_OTV izraz O_ZATV
# promjena -> PLUSP | MINUSM | PLUSJ izraz | MINUSJ izraz
# for -> FOR O_OTV IME# JEDNAKO izraz TOČKAZ IME# for_operator izraz TOČKAZ IME# promjena O_ZATV
# blok -> V_OTV naredbe V_ZATV | naredba
# petlja -> for blok
# varijabla -> IME | BROJ
# if_operator -> JJEDNAKO | MANJE | VEĆE  ##NAPOMENA: ovdje nadodati ako zelimo jos nesto u if_operatoru (možda još !=)
# uvjet -> varijabla | varijabla if_operator varijabla 
# grananje -> IF O_OTV uvjet O_ZATV blok (ELSE blok)?
# ispis_varijabla -> IME (aritmetičko) | BROJ
# varijable -> '' | varijable MMANJE ispis_varijabla
# ispis -> ISPIŠI varijable  
# tip -> INT | NAT (ovo je odvojeno iako je pravilo trivijalno jer će biti još tipova s desne strane; vjerojatno ću još od aritmetičkih dodati nat i to će biti dovoljno)
# pridruživanje -> IME (aritmetičkog tipa) JEDNAKO izraz
# deklaracija -> tip IME JEDNAKO izraz 
# formula -> PVAR | TRUE | FALSE | NEG formula | DIAMOND formula | BOX formula | O_OTV formula binvez formula O_ZATV 
# binvez -> KONJ | DISJ | KOND | BIKOND

### DODAO SAM SLJEDEĆA PRAVILA KOJA SU PROIZAŠLA IZ JOSIPOVOG PROŠIRENJA ###
### kasnije ćemo ih dodati gore - ovdje sam ih stavio samo da bude vidljivo što sam napravio ###
# formula -> IME (formule)
# pridruživanje -> IME (formule) JEDNAKO IME (formule)
# deklaracija -> FORMULA IME JEDNAKO formula 
# ispis_varijabla -> IME (formula)
# uvjet -> IME (formule) JJEDNAKO IME (formule)

# NAPOMENA (1): uočiti da formule možemo ispisivati samo ako su unutar neke varijable te isto tako
# u if_uvjetu možemo uspoređivati varijable koje predstavljaju neke formule. Dakle, jezik ne
# podržava nešto poput ispiši << ($P0 -> #P1); ili if (($P0 -> #P1) == ($P0 -> #P1)) ... Vjerojatno
# smo trebali za ime formule uvesti poseban token IMEF, ali sada je vjerojatno kasno za sve to

### OSTATAK PRAVILA KOJA TREBA DODATI U PARSER I ZA NJIH ODGOVARAJUĆE AST-ove ###
# naredba -> unos TOČKAZ | forsira TOČKAZ | vrijedi TOČKAZ | provjera TOČKAZ | koristi TOČKAZ | TOČKAZ
# lista_pvar -> PVAR | PVAR ZAREZ lista_pvar
# forsira -> SVIJET (FORSIRA | NEFORSIRA) V_OTV lista_pvar V_ZATV 
# forsira -> SVIJET (FORSIRA | NEFORSIRA) PVAR 
# lista_svijet -> SVIJET | SVIJET ZAREZ lista_svijet
# vrijedi -> PVAR (VRIJEDI | NEVRIJEDI) V_OTV lista_svijet V_ZATV
# vrijedi -> PVAR (VRIJEDI | NEVRIJEDI) SVIJET
# provjera -> formula UPITNIK SVIJET
# koristi -> KORISTI MODEL V_OTV lista_svijet TOČKAZ lista_pvar V_ZATV
# unos -> MODEL (MMANJE IMED)+

# NAPOMENA (2): uočiti da su gornja pravila neovisna o svemu dosad implementiranom. Nema nikakvih 
# višeznačnosti te je dovoljno dodavati elif-ove u metodu naredba() u parseru te nakon toga
# kreirati potrebne metode i AST-ove. Također, ne znam jesi li mijenjao klasu T pa malo pogledaj
# je li sve kako treba biti (verzija je sinocnji merge)

# NAPOMENA (3): uočiti da nisam mijenjao AST-ove vezane uz formule, iako si ih ti promijenio. Kada
# budeš to ažurirao, samo neka metoda ispis() bude i dalje pod tim imenom te da i dalje radi
# ono što radi u ovoj verziji koda. To se odnosi i na metodu ispis() u tokenu T.IME. 


### 14.6.2023. ###

# naredba -> FOREACH (SVIJET | PVAR) blok


class P(Parser):
    def start(p):
        naredbe = [p.naredba()]
        while not p > KRAJ: naredbe.append(p.naredba())
        return Program(naredbe)
    
    def naredba(p):
        if p > T.FOR: return p.for_petlja()
        if p > T.FOREACH: return p.foreach_petlja()
        if p > T.ISPIŠI: return p.ispis()
        if p > T.IF: return p.grananje()
        if p > {T.INT, T.NAT, T.FORMULA}: return p.deklaracija()
        if ime := p >= T.IME:
            if p >= T.JEDNAKO: return p.pridruživanje(ime)
            if p >= T.UPITNIK: return p.provjera(ime) 
        if p > T.SVIJET: return p.forsira()
        if p > T.PVAR: return p.vrijedi()
        if p > T.KORISTI: return p.koristi()
        if p > T.UNESI: return p.unos()
        if br := p >= T.BREAK:
            p >> T.TOČKAZ
            return br
        if cont := p >= T.CONTINUE:
            p >> T.TOČKAZ
            return cont
        return p.formula()
    
    def foreach_petlja(p):
        p >> T.FOREACH
        ime = p >> {T.SVIJET, T.PVAR}
        blok = p.blok()
        return Foreach_petlja(ime, blok)

    def koristi(p):
        p >> T.KORISTI
        model = p >> T.MODEL
        model.nosač = set()
        model.pvars = set()
        p >> T.V_OTV
        svijet = p >> T.SVIJET
        svijet.sljedbenici = set()
        svijet.činjenice = set()
        model.nosač.add(svijet)
        while p >= T.ZAREZ:
            svijet = p >> T.SVIJET
            svijet.sljedbenici = set()
            svijet.činjenice = set()
            model.nosač.add(svijet)
        p >> T.TOČKAZ
        pvar = p >> T.PVAR
        model.pvars.add(pvar)
        while p >= T.ZAREZ:
            pvar = p >> T.PVAR
            model.pvars.add(pvar)
        p >> T.V_ZATV
        p >> T.TOČKAZ
        return Koristi(model)

    def unos(p):
        p >> T.UNESI
        datoteke = []
        while p >= T.MMANJE: datoteke.append(p >> T.IMED)
        p >> T.TOČKAZ
        return Unos(datoteke)

    def provjera(p, ime):
        w = p >> T.SVIJET
        p >> T.TOČKAZ
        return Provjera(w, ime)
    
    def for_petlja(p):
        kriva_varijabla = SemantičkaGreška('Sva tri dijela for-petlje moraju imati istu varijablu')
        
        p >> T.FOR, p >> T.O_OTV
        i = p >> T.IME #NAPOMENA: mozda ovdje ipak stavit uvjet da ime mora imati # kao prvi znak
        p >> T.JEDNAKO
        početak = p.izraz() ## u AST for_petlja pazimo ako se vrati ime formule
        p >> T.TOČKAZ

        if (p >> T.IME) != i: raise kriva_varijabla
        for_operator = p >> {T.MANJE, T.VEĆE} # ovdje se lako doda ako hocemo podrzati jos neke operatore
        granica = p.izraz() ## u AST for_petlja pazimo ako se vrati ime formule
        p >> T.TOČKAZ

        if (p >> T.IME) != i: raise kriva_varijabla
        if minus_ili_plus := p >= {T.PLUSP, T.MINUSM}: promjena = nenavedeno
        elif minus_ili_plus := p >> {T.PLUSJ, T.MINUSJ}: promjena = p.izraz() ## u AST for_petlja pazimo ako se vrati ime formule
        p >> T.O_ZATV

        blok = p.blok()
        return For_Petlja(i, početak, for_operator, granica, promjena, minus_ili_plus, blok)
    
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
    
    def pridruživanje(p, ime_varijable):
        # provjera koji nam je tip s lijeve strane (samo formule još dolaze)
        if ime_varijable.sadržaj[0] == '#': ## ako pridružujemo aritmetičkom izrazu
            vrijednost = p.izraz()
        elif ime_varijable.sadržaj[0].islower(): ## ako pridružujemo formuli
            vrijednost = p.formula()
        else: raise SintaksnaGreška(f"Pridruživanje nije podržano za varijablu {ime_varijable.sadržaj}")
        p >> T.TOČKAZ
        return Pridruživanje(ime_varijable, vrijednost)
    
    def deklaracija(p):
        tip = p >> {T.INT, T.NAT, T.FORMULA} #kad budemo imali vise tipova, onda cemo imati p > {T.INT, T.FORMULA...}
        ime = p >> T.IME
        p >> T.JEDNAKO
        if tip ^ {T.INT, T.NAT}: ## ako deklariramo aritmetički izraz
            vrij = p.izraz()
        elif tip ^ T.FORMULA: ## ako deklariramo varijablu
            vrij = p.formula() 
        else: raise SintaksnaGreška(f"Za tip {tip} nije podržana deklaracija!")
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
        if varijabla := p >= {T.PVAR, T.IME}: return varijabla
        elif konstanta := p >= {T.TRUE, T.FALSE}: return konstanta
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
            while p >= T.ZAREZ: lista_pvar.append(p >> T.PVAR)
            p >> T.V_ZATV
        else: lista_pvar.append(p >> T.PVAR)
        p >> T.TOČKAZ
        return Forsira(w, lista_pvar, simb)
        
    def vrijedi(p):
        pvar = p >> T.PVAR
        simb = p >> { T.VRIJEDI, T.NEVRIJEDI }
        lista_svijet = []
        if p >= T.V_OTV:
            lista_svijet.append(p >> T.SVIJET)
            while p >= T.ZAREZ: lista_svijet.append(p >> T.SVIJET)
            p >> T.V_ZATV
        else: lista_svijet.append(p >> T.SVIJET)
        p >> T.TOČKAZ
        return Vrijedi(pvar, lista_svijet, simb)

class Program(AST):
    naredbe: 'barem jedna naredba'

    def izvrši(program):
        try:
            for naredba in program.naredbe: naredba.izvrši()
        except PrekidBreak: raise SemantičkaGreška('Nedozvoljen break izvan petlje!')
        except PrekidContinue: raise SemantičkaGreška('Nedozvoljen continue izvan petlje!')

class Koristi(AST):
    model: T.MODEL
    def izvrši(self):
        rt.mem['using'] = self.model

class Unos(AST):
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
                        if novi := rt.mem['using'].nađi_svijet('@' + prvi_red[i]):
                            if novi in svjetovi:
                                raise IOError('Svijet se navodi dvaput.')
                            else: svjetovi.append(novi)
                        else: raise IOError('Svijet nije deklariran.')
                else:
                    for i in range(1, len(prvi_red)):
                        if nova := rt.mem['using'].nađi_pvar('$' + prvi_red[i]):
                            if nova in pvars:
                                raise IOError('Propozicionalna varijabla navodi se dvaput.')
                            else: pvars.append(nova)
                        else: raise IOError('Propozicionalna varijabla nije deklarirana.')
                for redak in reader:
                    lijevi = rt.mem['using'].nađi_svijet('@' + redak[0])
                    for i in range(1, len(redak)):
                        if str.upper(redak[i][0]) in ['T', '1', 'Y', 'I', 'D', 'O']:
                            if tip == 'rel':
                                lijevi.sljedbenici.add(svjetovi[i - 1])
                            else: lijevi.činjenice.add(pvars[i - 1])
                        elif str.upper(redak[i][0]) in ['F', '0', 'N', 'L', 'N', 'X']:
                            if tip == 'rel':
                                lijevi.sljedbenici.discard(svjetovi[i - 1])
                            else: lijevi.činjenice.discard(pvars[i - 1])
                        else: raise IOError('Neispravna oznaka istinitosti u tablici.')

class Foreach_petlja(AST):
    ime: '(SVIJET | PVAR)'
    blok: 'naredba+'

    def izvrši(self):
        if 'using' not in rt.mem:
            raise SemantičkaGreška("Potrebno je prvo deklarirati model!")
        
        for element in rt.mem['using'].nosač if self.ime ^ T.SVIJET else rt.mem['using'].pvars:
            try: 
                if self.ime ^ T.SVIJET:
                    self.ime.sljedbenici = element.sljedbenici
                    self.ime.činjenice = element.činjenice
                    rt.mem['temp'] = self.ime
                elif self.ime ^ T.PVAR:
                    rt.mem['temp'] = element
                else: raise SemantičkaGreška("Nepodržan tip podatka unutar foreach petlje!")
                self.blok.izvrši()
            except PrekidBreak: break
            except PrekidContinue: continue
        
        del rt.mem['temp']
                        
class For_Petlja(AST):
    varijabla: 'IME'
    početak: 'izraz'
    operator: '(<|>)' #mogli bi bit još podržani <= ili >=, ali nije da time dobivamo na ekspresivnosti jezika; eventualno dodati !=
    granica: 'izraz'
    promjena: 'izraz?'
    predznak: '(+|-)'
    blok: 'naredba*'

    def izvrši(petlja):
        # je formula s desne strane semantička ili sintaksna greška?
        neadekvatna_desna_strana = SemantičkaGreška("Greška: nad formulama nisu definirane aritmetičke operacije!")
        kv = petlja.varijabla
        
        # donja tri uvjeta provjeravaju da se s desne strane ne nađe formula
        if petlja.početak ^ T.IME and petlja.početak.sadržaj[0] != '#':
            raise neadekvatna_desna_strana
        elif petlja.granica ^ T.IME and petlja.granica.sadržaj[0] != '#':
            raise neadekvatna_desna_strana
        elif petlja.promjena ^ T.IME and petlja.promjena.sadržaj[0] != '#':
            raise neadekvatna_desna_strana 
        
        rt.mem[kv] = [petlja.početak.vrijednost()] # NAPOMENA: ovdje ime moze biti bilo koje i ne mora biti deklarirano (vidjet sta ako neko unese formulu npr.); vidi jel stvara probleme
        while rt.mem[kv][0] < petlja.granica.vrijednost() if petlja.operator ^ T.MANJE else rt.mem[kv][0] > petlja.granica.vrijednost():
            try:
                petlja.blok.izvrši()
            except PrekidBreak: break
            except PrekidContinue: #nazalost dupliciram kod radi ispravnog rada continue, kasnije mozemo popraviti
                prom = petlja.promjena
                if petlja.predznak ^ T.MINUSJ or petlja.predznak ^ T.MINUSM:
                    rt.mem[kv][0] -= prom.vrijednost() if prom else 1
                else: rt.mem[kv][0] += prom.vrijednost() if prom else 1
                continue
            prom = petlja.promjena
            if petlja.predznak ^ T.MINUSJ or petlja.predznak ^ T.MINUSM:
                rt.mem[kv][0] -= prom.vrijednost() if prom else 1
            else: rt.mem[kv][0] += prom.vrijednost() if prom else 1
        
        del rt.mem[kv]

class Blok(AST):
    naredbe: 'naredba*'
    
    def izvrši(blok):
        for naredba in blok.naredbe:
            naredba.izvrši()

class Ispis(AST):
    varijable: 'IME*'

    def izvrši(ispis):
        for varijabla in ispis.varijable:
            if varijabla ^ {T.INT, T.NAT, T.FORMULA, T.BROJ, T.IME}:
                if 'temp' in rt.mem:
                    print(rt.mem['temp'].ispis())
                else: print(varijabla.ispis(), end = ' ') 
            elif varijabla ^ {T.SVIJET}:
                if svijet := rt.mem['using'].nađi_svijet(varijabla.sadržaj):
                    print(svijet.ispis())
                elif 'temp' in rt.mem:
                    print(rt.mem['temp'].ispis())
                else: raise SemantičkaGreška(f'Svijet {varijabla.sadržaj} nije deklariran.')
            elif varijabla ^ {T.MODEL}:
                if rt.mem['using'].sadržaj == varijabla.sadržaj:
                    print(rt.mem['using'].ispis())
                else: raise SemantičkaGreška(f'Model {varijabla.sadržaj} nije trenutno u uporabi.')
            else: raise SemantičkaGreška("Neočekivana varijabla za ispis!")
            ## ovo dobro ispisuje int, nat i formula; PAZI ZA MODEL I SVIJET

class Uvjet(AST):
    lijeva: '(IME|BROJ)'
    operator: '(==|<|>)'
    desna: '(IME|BROJ)'

    def ispunjen(uvjet): # NAPOMENA: možda ovo dolje moze ostati i za tip formula (iako je glupo, bolje za njih samo ==, ali lako promijenimo sto zelimo); ponovno: definirati metodu vrijednost za formulu na koji nacin vec zelimo
        # ovo ispod prolazi za formule i s jedne i druge strane
        if uvjet.lijeva ^ T.IME and uvjet.lijeva.sadržaj[0].islower():
            if not uvjet.operator ^ T.JJEDNAKO:
                raise SemantičkaGreška("Nepodržan operator na tipu formula!")
            elif uvjet.desna ^ T.IME and not uvjet.desna.sadržaj[0].islower():
                raise SemantičkaGreška("Uspoređivanje formule s nekompatibilnim tipom!")
            else: return uvjet.lijeva.ispis() == uvjet.desna.ispis() 

        # ovo ispod bez problema prolazi za aritmetičke vrijednosti s lijeve i desne strane
        if uvjet.operator ^ T.JJEDNAKO:
            return uvjet.lijeva.vrijednost() == uvjet.desna.vrijednost() 
        elif uvjet.operator ^ T.VEĆE:
            return uvjet.lijeva.vrijednost() > uvjet.desna.vrijednost()
        elif uvjet.operator ^ T.MANJE:
            return uvjet.lijeva.vrijednost() < uvjet.desna.vrijednost()
        else: raise SintaksnaGreška('Nepodržan if-uvjet!')

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
        if pridruživanje.varijabla in rt.mem:
            if pridruživanje.varijabla.sadržaj[0] == '#': # ovo se odnosi na pridruživanje aritmetičkim varijablama (int, nat)
                if pridruživanje.vrij ^ T.IME and pridruživanje.vrij.sadržaj[0] != '#':
                    raise SemantičkaGreška("Greška: nepravilno pridruživanje aritmetičkoj varijabli!")
                elif rt.mem[pridruživanje.varijabla][1] ^ T.NAT and pridruživanje.vrij.vrijednost() < 0:
                    greska = GreskaTipova()
                    greska.krivi_tip(pridruživanje.varijabla.sadržaj, Tip.N, Tip.Z)
                else: rt.mem[pridruživanje.varijabla][0] = pridruživanje.vrij.vrijednost()
            elif pridruživanje.varijabla.sadržaj[0].islower(): # ovo se odnosi na pridruživanje formulama
                if pridruživanje.vrij ^ T.IME and not pridruživanje.vrij.sadržaj[0].islower():
                    raise SemantičkaGreška("Greška: nepravilno pridruživanje varijabli formula!")
                else: rt.mem[pridruživanje.varijabla][0] = pridruživanje.vrij
        else: return rt.mem[pridruživanje.varijabla] #jer ovo vraca bas ono upozorenje koje nam treba

class Deklaracija(AST):
    tip: 'neki od podrzanih tipova'
    ime: 'IME'
    vrij: 'varijabla | BROJ'

    # prilikom deklaracije, kljucevi se preslikavaju u listu s dva elementa (par): vrijednost, tip
    def izvrši(deklaracija):
        if deklaracija.ime in rt.mem: ## ako se dogodila redeklaracija
            raise deklaracija.ime.redeklaracija()
        elif deklaracija.tip ^ {T.NAT, T.INT}: ## ako deklariramo aritmeticki tip
            if deklaracija.tip ^ T.NAT and deklaracija.vrij.vrijednost() < 0: 
                tip1 = Tip.N
                tip2 = Tip.Z
                greska = GreskaTipova()
                greska.krivi_tip(deklaracija.ime.sadržaj, tip1, tip2)
            elif not deklaracija.ime.sadržaj[0] == '#': raise SemantičkaGreška("Neispravan naziv varijable aritmetičkog tipa!")
            elif deklaracija.vrij ^ T.IME and not deklaracija.vrij.sadržaj[0] == '#': raise SemantičkaGreška(f'Nepodudaranje tipova prilikom deklaracije aritmetičke varijable {deklaracija.ime.sadržaj}!')
            else: rt.mem[deklaracija.ime] = [deklaracija.vrij.vrijednost(), deklaracija.tip]
        elif deklaracija.tip ^ T.FORMULA: ## ako deklariramo formulu
            if deklaracija.vrij ^ T.IME and not deklaracija.vrij.sadržaj[0].islower(): raise SemantičkaGreška(f'Nepodudaranje tipova prilikom deklaracije formule {deklaracija.ime.sadržaj}!')
            elif not deklaracija.ime.sadržaj.islower() or deklaracija.ime.sadržaj[0] == '#': raise SemantičkaGreška("Neispravan naziv varijable tipa formula!")
            else: rt.mem[deklaracija.ime] = [deklaracija.vrij, deklaracija.tip]
        else: raise SemantičkaGreška("Nepodržani tip varijable!") # ne bi smjelo do ovoga doći jer za to imamo provjeru u odg. metodi

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
        for sljedbenik in w.sljedbenici:
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
    ime: 'ime formule'
    def izvrši(self):
        if svijet := rt.mem['using'].nađi_svijet(self.svijet.sadržaj):
            t = ' ⊩ ' if self.ime.vrijednost().vrijednost(svijet) else ' ⊮ '
            print(svijet.sadržaj + t + self.ime.vrijednost().ispis())
        else: raise SemantičkaGreška(f'Svijet {self.svijet.sadržaj} nije deklariran.')

class Forsira(AST):
    svijet: T.SVIJET
    pvars: 'list(T.PVAR)'
    simbol: 'T.FORSIRA | T.NEFORSIRA'
    def izvrši(self):
        if svijet := rt.mem['using'].nađi_svijet(self.svijet.sadržaj):
            for pvar in self.pvars:
                if self.simbol ^ T.FORSIRA:
                    svijet.činjenice.add(pvar.sadržaj)
                elif self.simbol ^ T.NEFORSIRA: 
                    svijet.činjenice.discard(pvar.sadržaj)
        else: raise SemantičkaGreška(f'Svijet {self.svijet.sadržaj} nije deklariran.')

class Vrijedi(AST):
    pvar: T.PVAR
    svjetovi: 'list(T.SVIJET)'
    simbol: 'T.VRIJEDI | T.NEVRIJEDI'
    def izvrši(self):
        for s in self.svjetovi:
            if svijet := rt.mem['using'].nađi_svijet(s.sadržaj):
                if self.simbol ^ T.VRIJEDI:
                    svijet.činjenice.add(self.pvar.sadržaj)
                elif self.simbol ^ T.NEVRIJEDI:
                    svijet.činjenice.discard(self.pvar.sadržaj)
            else: raise SemantičkaGreška(f'Svijet {self.svijet.sadržaj} nije deklariran.')

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
    
rt.mem = Memorija()

### ISPOD JE SVE ZA REALIZACIJU KORISNIČKOG UNOSA ###

# u interaktivnom nacinu rada treba omoguciti korisnikov unos u konzolu:
# PROVJERI_DOKAZ dokaz.txt (npr.) nakon cega se poziva unos_dokaza(dokaz.txt)
# sve formule su spremljene u varijablama fi, i = 1, ..., k gdje je k broj
# formula u dokazu. Uočiti: za vrijeme interkativnog rada nakon učitavanja
# datoteke u kojem se nalazi dokaz te varijable više nisu "slobodne" za 
# deklaraciju!!
def unos_dokaza(ime_txt_dat):
    with open(ime_txt_dat, 'r') as file:
        lines = file.readlines()

    i = 1
    formule = []
    for line in lines:
        formule.append('formula f' + str(i) + " = " + line)
        i += 1

    naredbe = ""    
    for line in formule:
        naredbe += line

    P(naredbe).izvrši() 

# u interaktivnom nacinu rada omoguciti unos programa koji je natipkan u 
# nekoj .txt datoteci. Ako je program napisan u program.txt, onda se 
# poziva s unos_programa("program.txt")
def unos_programa(ime_txt_dat):
    with open(ime_txt_dat, 'r') as file:
        lines = file.readlines()
    naredbe = ""    
    for line in lines:
        naredbe += line
    
    P(naredbe).izvrši() 

unos_programa("program2.txt") # da ne moramo stalno u VSC pisati program vec u .txt