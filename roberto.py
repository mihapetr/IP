from vepar import *

subskript = str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉')
class Prekid(NelokalnaKontrolaToka): """Signal koji šalje naredba break."""

class T(TipoviTokena):
    NEG, KONJ, DISJ, O_OTV, O_ZATV = '~&|()'
    KOND, BIKOND = '->', '<->'
    BOX, DIAMOND = '[]', '<>'

    class PVAR(Token):
        def optim(self): return self
        def ispis(self): return self.sadržaj.translate(subskript)
        def optim1(self): return self
    #gornji tokeni su za formule, a donji za program
    TOČKAZ, V_OTV, V_ZATV = ';{}'
    FOR, IF, ELSE, WHILE, ISPIŠI = 'for', 'if', 'else', 'while', 'ispiši'
    INT = 'int'
    JEDNAKO, JJEDNAKO, PLUS, PLUSP, PLUSJ, MINUS, MINUSM, MINUSJ, PUTA = '=', '==', '+', '++', '+=', '-', '--', '-=', '*'
    MANJE, MMANJE, VEĆE = '<', '<<', '>' 

    class BREAK(Token):
        literal = 'break'
        def izvrši(self): raise Prekid
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
        elif znak == 'P':
            lex.prirodni_broj('')
            yield lex.token(T.PVAR)
        elif znak.isalpha() or znak == '_':
            lex * {str.isalnum, '_'}
            yield lex.literal_ili(T.IME)
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        elif znak == '-':
            if lex >= '>': yield lex.token(T.KOND)
            elif lex >= '-': yield lex.token(T.MINUSM)
            elif lex >= '=': yield lex.token(T.MINUSJ)
            else: yield lex.token(T.MINUS)
        elif znak == '+':
            if lex >= '+': yield lex.token(T.PLUSP)
            elif lex >= '=': yield lex.token(T.PLUSJ)
            else: yield lex.token(T.PLUS)
        elif znak == '=':
            yield lex.token(T.JJEDNAKO if lex >= '=' else T.JEDNAKO)
        elif znak == '#':
            lex - '\n'
            lex.zanemari()
        else: yield lex.literal(T)

### beskontekstna gramatika
# start -> naredbe naredba
# naredbe -> '' | naredbe naredba
# naredba  -> petlja | grananje | ispis TOČKAZ | pridruživanje TOČKAZ | BREAK TOČKAZ
# for_operator -> MANJE | VEĆE ##ovdje nadodati ako zelimo jos nesto u for_operatoru (možda još !=)
# promjena -> PLUSP | MINUSM | PLUSJ BROJ | MINUSJ BROJ
# for -> FOR O_OTV IME# JEDNAKO BROJ TOČKAZ IME# for_operator BROJ TOČKAZ IME# promjena O_ZATV
# petlja -> for naredba | for V_OTV naredbe V_ZATV
# nešto -> IME | BROJ
# if_operator -> JJEDNAKO | MANJE | VEĆE  #ovdje nadodati ako zelimo jos nesto u if_operatoru (možda još !=)
# uvjet -> nešto | nešto if_operator nešto 
# grananje -> IF O_OTV uvjet O_ZATV naredba | IF O_OTV uvjet O_ZATV naredba ELSE naredba
# varijable -> '' | varijable MMANJE nešto
# ispis -> ISPIŠI varijable 
# tip -> INT (ovo je odvojeno iako je pravilo trivijalno jer će biti još tipova s desne strane)
# pridruživanje -> (tip IME JEDNAKO nešto |) IME JEDNAKO nešto

## ovo ispod kasnije će se povezati s gornjim kad se uvedu varijable formula, model itd.
# formula -> PVAR | NEG formula | DIAMOND formula | BOX formula | O_OTV formula binvez formula O_ZATV
# binvez -> KONJ | DISJ | KOND | BIKOND

class P(Parser):
    def start(p):
        naredbe = [p.naredba()]
        while not p > KRAJ: naredbe.append(p.naredba())
        return Program(naredbe)
    
    def naredba(p):
        if p > T.FOR: return p.petlja()
        elif p > T.ISPIŠI: return p.ispis()
        elif p > T.IF: return p.grananje()
        elif br := p >> T.BREAK:
            p >> T.TOČKAZ
            return br
    
    def petlja(p):
        kriva_varijabla = SemantičkaGreška('Sva tri dijela for-petlje moraju imati istu varijablu')
        
        p >> T.FOR, p >> T.O_OTV
        i = p >> T.IME
        p >> T.JEDNAKO
        početak = p >> T.BROJ
        p >> T.TOČKAZ

        if (p >> T.IME) != i: raise kriva_varijabla
        for_operator = p >> {T.MANJE, T.VEĆE} # ovdje se lako doda ako hocemo podrzati jos neke operatore
        granica = p >> T.BROJ
        p >> T.TOČKAZ

        if (p >> T.IME) != i: raise kriva_varijabla
        if minus_ili_plus := p >= {T.PLUSP, T.MINUSM}: promjena = nenavedeno
        elif minus_ili_plus := p >> {T.PLUSJ, T.MINUSJ}: promjena = p >> T.BROJ
        p >> T.O_ZATV

        if p >= T.V_OTV:
            blok = []
            while not p >= T.V_ZATV: blok.append(p.naredba())
        else: blok = [p.naredba()]
        return Petlja(i, početak, for_operator, granica, promjena, minus_ili_plus, blok)
    
    def ispis(p):
        p >> T.ISPIŠI
        varijable = []
        while p >= T.MMANJE: varijable.append(p >> T.IME)
        p >> T.TOČKAZ
        return Ispis(varijable)
    
    #iznad je sve ok, samo u naredba treba implementirat p.pridruživanje()
    def grananje(p):
        p >> T.IF, p >> T.O_OTV
        uvjet = p.uvjet()
        p >> T.O_ZATV
        if_naredba = p.naredba()
        else_naredba = nenavedeno
        if p >= T.ELSE: else_naredba = p.naredba()
        return Grananje(uvjet, if_naredba, else_naredba)
    
    def uvjet(p):
        lijeva_strana = p >> {T.IME, T.BROJ}
        op = p >> {T.JJEDNAKO, T.MANJE, T.VEĆE} #ovdje se dodaju if_operatori ako zelimo prosiriti
        desna_strana = p >> {T.IME, T.BROJ}
        return Uvjet(lijeva_strana, op, desna_strana)

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
        rt.mem = Memorija()
        try:
            for naredba in program.naredbe: naredba.izvrši()
        except Prekid: raise SemantičkaGreška('nedozvoljen break izvan petlje')

class Petlja(AST):
    varijabla: 'IME'
    početak: 'BROJ'
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
                for naredba in petlja.blok: naredba.izvrši()
            except Prekid: break
            prom = petlja.promjena
            if petlja.predznak ^ T.MINUSJ or petlja.predznak ^ T.MINUSM:
                rt.mem[kv] -= prom.vrijednost() if prom else 1
            else: rt.mem[kv] += prom.vrijednost() if prom else 1

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
        else: print('Trebao bih raisati neku vrstu greške da operator nije podržan ali to ne znam')

class Grananje(AST):
    uvjet: 'log'
    onda: 'naredba'
    inače: 'naredba'

    def izvrši(grananje):
        if grananje.uvjet.ispunjen(): grananje.onda.izvrši()
        elif grananje.inače: grananje.inače.izvrši()

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
    nova = nova.optim1() #kreiramo ekvivalentnu formulu koja ima samo negaciju i kondicional od veznika
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
    
### ispod je samo testiranje

prikaz(kôd := P('''
    for ( i = 8 ; i < 13 ; i += 2 ) {
        for(j=0; j<5; j++) {
            ispiši<<i<<j;
            if(i == 10) if (j == 1) break;
        }
        ispiši<<i;
    }
'''), 8)
kôd.izvrši()