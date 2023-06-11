from vepar import *

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
        def vrijednost(self, w): return (self in w.činjenice) # pogledati komentar u AST-ovima ispis i uvjet (vezano uz naziv ove metode)
    # Tokeni za svijetove i modele
    FORSIRA, NEFORSIRA, VRIJEDI, NEVRIJEDI = '|=', '|~', '=|', '~|'
    class SVIJET(Token):
        sljedbenici: 'set(T.SVIJET)'
        činjenice: 'set(T.PVAR)'
        def vrijednost(self): return self.sadržaj
    class MODEL(Token):
        nosač: 'set(T.SVIJET)'
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
        def vrijednost(self): return rt.mem[self][0]

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

### beskontekstna gramatika
# start -> naredbe naredba
# naredbe -> '' | naredbe naredba
# naredba  -> petlja | grananje | ispis TOČKAZ | pridruživanje TOČKAZ | deklaracija TOČKAZ | BREAK TOČKAZ | CONTINUE TOČKAZ
# for_operator -> MANJE | VEĆE ##NAPOMENA: ovdje nadodati ako zelimo jos nesto u for_operatoru (možda još !=)
# promjena -> PLUSP | MINUSM | PLUSJ BROJ | MINUSJ BROJ
# for -> FOR O_OTV IME# JEDNAKO BROJ TOČKAZ IME# for_operator BROJ TOČKAZ IME# promjena O_ZATV
# blok -> V_OTV naredbe V_ZATV | naredba
# petlja -> for blok
# varijabla -> IME | BROJ
# if_operator -> JJEDNAKO | MANJE | VEĆE  ##NAPOMENA: ovdje nadodati ako zelimo jos nesto u if_operatoru (možda još !=)
# uvjet -> varijabla | varijabla if_operator varijabla 
# grananje -> IF O_OTV uvjet O_ZATV blok (ELSE blok)?
# varijable -> '' | varijable MMANJE varijabla
# ispis -> ISPIŠI varijable 
# izraz -> član | izraz (PLUS|MINUS) član
# član -> faktor | član PUTA faktor
# faktor -> baza | baza NA faktor | MINUS faktor
# baza -> BROJ | IME(aritmetičkog tipa) | O_OTV izraz O_ZATV 
# tip -> INT | NAT (ovo je odvojeno iako je pravilo trivijalno jer će biti još tipova s desne strane; vjerojatno ću još od aritmetičkih dodati nat i to će biti dovoljno)
# pridruživanje -> IME JEDNAKO izraz
# deklaracija -> tip IME JEDNAKO izraz 

## ovo ispod kasnije će se povezati s gornjim kad se uvedu varijable formula, model itd.
# formula -> PVAR | NEG formula | DIAMOND formula | BOX formula | O_OTV formula binvez formula O_ZATV 
# binvez -> KONJ | DISJ | KOND | BIKOND

class P(Parser):
    def start(p):
        naredbe = [p.naredba()]
        while not p > KRAJ: naredbe.append(p.naredba())
        return Program(naredbe)
    
    def naredba(p):
        if p > T.FOR: return p.for_petlja()
        elif p > T.ISPIŠI: return p.ispis()
        elif p > T.IF: return p.grananje()
        elif p > T.IME: return p.pridruživanje()
        elif p > {T.INT, T.NAT}: return p.deklaracija() #kad budemo imali vise tipova, onda cemo imati p > {T.INT, T.FORMULA...}
        elif br := p >= T.BREAK:
            p >> T.TOČKAZ
            return br
        elif cont := p >= T.CONTINUE:
            p >> T.TOČKAZ
            return cont
        else: raise SintaksnaGreška('Nepoznata naredba')
    
    def for_petlja(p):
        kriva_varijabla = SemantičkaGreška('Sva tri dijela for-petlje moraju imati istu varijablu')
        
        p >> T.FOR, p >> T.O_OTV
        i = p >> T.IME #NAPOMENA: mozda ovdje ipak stavit uvjet da ime mora imati # kao prvi znak
        p >> T.JEDNAKO
        početak = p.izraz()
        p >> T.TOČKAZ

        if (p >> T.IME) != i: raise kriva_varijabla
        for_operator = p >> {T.MANJE, T.VEĆE} # ovdje se lako doda ako hocemo podrzati jos neke operatore
        granica = p.izraz()
        p >> T.TOČKAZ

        if (p >> T.IME) != i: raise kriva_varijabla
        if minus_ili_plus := p >= {T.PLUSP, T.MINUSM}: promjena = nenavedeno
        elif minus_ili_plus := p >> {T.PLUSJ, T.MINUSJ}: promjena = p.izraz()
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
        while p >= T.MMANJE: varijable.append(p >> {T.IME, T.BROJ})
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
        vrijednost = p.izraz()
        p >> T.TOČKAZ
        return Pridruživanje(ime_varijable, vrijednost)
    
    def deklaracija(p):
        tip = p >> {T.INT, T.NAT} #kad budemo imali vise tipova, onda cemo imati p > {T.INT, T.FORMULA...}
        ime = p >> T.IME
        p >> T.JEDNAKO
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
            return elementarni #valjda tu nece bit problema kod T.IME jer to ce kasnije bit naziv za neku varijablu koja ne mora biti aritmetickog tipa
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

class Program(AST):
    naredbe: 'barem jedna naredba'

    def izvrši(program):
        try:
            for naredba in program.naredbe: naredba.izvrši()
        except PrekidBreak: raise SemantičkaGreška('Nedozvoljen break izvan petlje!')
        except PrekidContinue: raise SemantičkaGreška('Nedozvoljen continue izvan petlje!')

class For_Petlja(AST):
    varijabla: 'IME'
    početak: 'izraz'
    operator: '(<|>)' #mogli bi bit još podržani <= ili >=, ali nije da time dobivamo na ekspresivnosti jezika; eventualno dodati !=
    granica: 'izraz'
    promjena: 'izraz?'
    predznak: '(+|-)'
    blok: 'naredba*'

    def izvrši(petlja):
        kv = petlja.varijabla
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

class Blok(AST):
    naredbe: 'naredba*'
    
    def izvrši(blok):
        for naredba in blok.naredbe:
            naredba.izvrši()

class Ispis(AST):
    varijable: 'IME*'

    def izvrši(ispis):
        for varijabla in ispis.varijable:
            print(varijabla.vrijednost(), end = ' ') # NAPOMENA: kad se formule nadju kao varijable, treba svakoj formuli dat metodu vrijednost koja poziva metodu za ispisivanje

class Uvjet(AST):
    lijeva: '(IME|BROJ)'
    operator: '(==|<|>)'
    desna: '(IME|BROJ)'

    def ispunjen(uvjet): # NAPOMENA: možda ovo dolje moze ostati i za tip formula (iako je glupo, bolje za njih samo ==, ali lako promijenimo sto zelimo); ponovno: definirati metodu vrijednost za formulu na koji nacin vec zelimo
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
        if pridruživanje.varijabla in rt.mem:
            if pridruživanje.varijabla.sadržaj[0] == '#': # ovo se odnosi na ARITMETICKE VARIJABLE jer kod njih ima problema
                
                if rt.mem[pridruživanje.varijabla][1] ^ T.NAT and pridruživanje.vrij.vrijednost() < 0:
                    greska = GreskaTipova()
                    greska.krivi_tip(pridruživanje.varijabla.sadržaj, Tip.N, Tip.Z)
                else: rt.mem[pridruživanje.varijabla][0] = pridruživanje.vrij.vrijednost()

            else: rt.mem[pridruživanje.varijabla][0] = pridruživanje.vrij.vrijednost() # ako varijabla nije aritmeticka, onda sve moze (nadopuniti po potrebi)
        else: return rt.mem[pridruživanje.varijabla] #jer ovo vraca bas ono upozorenje koje nam treba

class Deklaracija(AST):
    tip: 'neki od podrzanih tipova'
    ime: 'IME'
    vrij: 'varijabla | BROJ'

    def izvrši(deklaracija):                                              
        if deklaracija.tip ^ T.NAT and deklaracija.vrij.vrijednost() < 0: #na ovaj nacin bi sva ostala nepodudaranja u tipovima mogli rjesavati; uoči da se ovo mora rješavat u AST-u, a ne u odgovarajućoj metodi parsera
            tip1 = Tip.N
            tip2 = Tip.Z
            greska = GreskaTipova()
            greska.krivi_tip(deklaracija.ime.sadržaj, tip1, tip2)

        if deklaracija.ime in rt.mem:
            raise deklaracija.ime.redeklaracija()
        else: rt.mem[deklaracija.ime] = [deklaracija.vrij.vrijednost(), deklaracija.tip] #priliikom deklaracije, kljucevi se preslikavaju u listu s dva elementa (par): vrijednost, tip

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

    def ispis(self): 
        return self.veznik + self.ispod.ispis()
    
    #provjeri ovo
    def izvrši(self):
        return self.ispis()

class Negacija(Unarna):
    veznik = '¬'
    
class Diamond(Unarna):
    veznik = '◆'

class Box(Unarna):
    veznik = '■'

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

    #provjeri ovo
    def izvrši(self):
        return self.ispis()

class Disjunkcija(Binarna):
    veznik = '∨'

class Konjunkcija(Binarna):
    veznik = '∧'

class Kondicional(Binarna):
    veznik = '→'

class Bikondicional(Binarna):
    veznik = '↔'

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
    elif f1 ^ T.PVAR:
        return f1.ispis() == f2.ispis()
    elif isinstance(f1, Binarna): return jednaki(f1.lijevo, f2.lijevo) and jednaki(f1.desno, f2.desno)
    else: return jednaki(f1.ispod, f2.ispod)

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
    

# interaktivni unos -> todo: namjestiti da se korisnički input učitava sve dok se ne stavi;
# kada budemo imali unos programa iz datoteke, staviti opciju gdje korisnik bira hoće li unesti program iz datoteke ili će interaktivno pisati naredbe
# donja funkcija bi mogla biti od koristi
import sys
def get_input_with_semicolon(user_input):
    flag = False
    while True:
        char = sys.stdin.read(1)
        user_input += char
        if char == ';':
            flag = True
            break

    return user_input, flag


rt.mem = Memorija() #ovo mora bit ovdje, a ne u Program(AST) zbog interaktivnog izvršavanja

prikaz(kod := P('''
    int #a = 3;
    nat #b = 2;
    ispiši << #a << #b;
    #b = #a;
    ispiši << #a << #b;

    for (i = 3*2 - 3; i < #a + 10; i += 2^2) ispiši << i; 
'''), 8)
kod.izvrši()

#while True:
#    user_input = input('> ') # ovo popravit jer se naredba ne moze prostirati kroz više redaka
#    if user_input == 'kraj':
#        break
#    else:
#        naredba = P(user_input)
#        naredba.izvrši()