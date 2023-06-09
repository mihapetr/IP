from vepar import *

subskript = str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉')

class T(TipoviTokena):
    NEG, KONJ, DISJ, O_OTV, O_ZATV = '~&|()'
    KOND, BIKOND = '->', '<->'
    BOX, DIAMOND = '[]', '<>'
    #inertni tokeni iznad su dovoljni za formule, ovi ispod su već za jezik
    TOČKAZ = ';'
    class PVAR(Token):
        def optim(self): return self
        def ispis(self): return self.sadržaj.translate(subskript)
        def optim1(self): return self
@lexer
def ml(lex):
    for znak in lex:
        if znak.isspace() : lex.zanemari()
        elif znak == '[':
            lex >> ']'
            yield lex.token(T.BOX)
        elif znak == '<':
            if lex >= '>' : yield lex.token(T.DIAMOND)
            else:
                lex >> '-', lex >> '>'
                yield lex.token(T.BIKOND)
        elif znak == 'P':
            lex.prirodni_broj('')
            yield lex.token(T.PVAR)
        elif znak == '-':
            lex >> '>'
            yield lex.token(T.KOND)
        elif znak == '#':
            lex - '\n'
            lex.zanemari()
        else: yield lex.literal(T)

### beskontekstna gramatika
# formula -> PVAR | NEG formula | DIAMOND formula | BOX formula | O_OTV formula binvez formula O_ZATV
# binvez -> KONJ | DISJ | KOND | BIKOND

class P(Parser):
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
    
ulaz = '(<>~~P0&([]P1<-><>P5))'
prikaz(F := P(ulaz))
print(F.ispis())
prikaz(F := optimiziraj(F))
print(F.ispis())