from vepar import *
import csv
import copy

subskript = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


class PrekidBreak(NelokalnaKontrolaToka):
    """Signal koji šalje naredba break."""


class PrekidContinue(NelokalnaKontrolaToka):
    """Signal koji šalje naredba continue."""


class T(TipoviTokena):
    # Tokeni za modalne formule
    NEG, KONJ, DISJ, O_OTV, O_ZATV = "~&|()"
    KOND, BIKOND = "->", "<->"
    BOX, DIAMOND = "[]", "<>"

    class PVAR(Token):
        def optim(self):
            return self

        def ispis(self):
            return self.sadržaj.translate(subskript)

        def optim1(self):
            return self

        def vrijednost(self, w):
            return self in w.činjenice

        def pozovi(self):
            return self

    class TRUE(Token):
        literal = "T"

        def vrijednost(self, w):
            return True

        def ispis(self):
            return self.literal

        def pozovi(self):
            return self

    class FALSE(Token):
        literal = "F"

        def vrijednost(self, w):
            return False

        def ispis(self):
            return self.literal

        def pozovi(self):
            return self

    # Tokeni za svijetove i modele
    FORSIRA, NEFORSIRA, VRIJEDI, NEVRIJEDI = "|=", "|~", "=|", "~|"

    class SVIJET(Token):
        sljedbenici: "set(T.SVIJET)"
        činjenice: "set(T.PVAR)"

        def vrijednost(self):
            return self.sadržaj

        def ispis(self):
            za_ispis = self.sadržaj + ": {"
            for sljedbenik in self.sljedbenici:
                za_ispis += " " + sljedbenik.sadržaj
            za_ispis += "; "
            for pvar in self.činjenice:
                za_ispis += pvar.sadržaj + " "
            za_ispis += "} "
            return za_ispis.translate(subskript)

    class MODEL(Token):
        pvars: "set(T.PVAR)"
        nosač: "set(T.SVIJET)"

        def vrijednost(self):
            return self.sadržaj

        def ispis(self):
            za_ispis = self.sadržaj + ": {"
            for svijet in self.nosač:
                za_ispis += " " + svijet.sadržaj
            za_ispis += "; "
            for pvar in self.pvars:
                za_ispis += pvar.sadržaj + " "
            za_ispis += "} "
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
        def vrijednost(self):
            return str(self.sadržaj[1:-1])

    # Tokeni za jezik
    TOČKAZ, ZAREZ, V_OTV, V_ZATV, UPITNIK = ";,{}?"
    FOR, IF, ELSE, WHILE, FOREACH, NR, FUN = (
        "for",
        "if",
        "else",
        "while",
        "foreach",
        "nr",
        "fun",
    )
    ISPIŠI, UNESI, KORISTI, VRATI, SPREMI = (
        "ispiši",
        "unesi",
        "koristi",
        "vrati",
        "spremi",
    )
    INT, NAT, FORMULA = "int", "nat", "formula"
    JEDNAKO, PLUS, MINUS, PUTA, NA, OSTATAK = "=+-*^%"
    JJEDNAKO, PLUSP, PLUSJ, MINUSM, MINUSJ = "==", "++", "+=", "--", "-="
    MANJE, MMANJE, VEĆE = "<", "<<", ">"

    class BROJ(Token):
        def vrijednost(self):
            return int(self.sadržaj)

        def ispis(self):
            return self.sadržaj

    class IME(Token):
        def vrijednost(self):
            return rt.mem[self][0] if fun == "__main__" else rt.lm[fun][self][0]

        def tip_varijable(self):
            return rt.mem[self][1] if fun == "__main__" else rt.lm[fun][self][1]

        def ispis(self):
            if len(rt.mem[self]) == 1:
                return rt.mem[self][0]
            elif self.tip_varijable() ^ {T.INT, T.NAT}:
                return self.vrijednost()
            elif self.tip_varijable() ^ T.FORMULA:
                return self.vrijednost().ispis()
            elif len(rt.mem[self]) == 2:
                return rt.mem[self][0].ispis()
            elif len(rt.mem[self]) == 3:
                return rt.mem[self][0]
            else:
                raise SemantičkaGreška("Traženje nepoznatog sadržaja!")

    class IMEF(IME):
        def ispis(self):
            return self.sadržaj

    class CONTINUE(Token):
        literal = "continue"

        def izvrši(self):
            raise PrekidContinue

    class BREAK(Token):
        literal = "break"

        def izvrši(self):
            raise PrekidBreak


# donje dvije klase sluze samo za lijepo ispisivanje poruke prilikom nekompatibilnih tipova
class Tip(enum.Enum):
    N = "NAT"
    Z = "INT"


class GreskaTipova:
    def krivi_tip(self, ime, tip1, tip2):
        raise SemantičkaGreška(
            f"IME '{ime}': tipovi ne odgovaraju: {tip1.name} vs. {tip2.name}"
        )


@lexer
def ml(lex):
    for znak in lex:
        if znak.isspace():
            lex.zanemari()
        elif znak == "[":
            lex >> "]"
            yield lex.token(T.BOX)
        elif znak == "<":
            if lex >= ">":
                yield lex.token(T.DIAMOND)
            elif lex >= "<":
                yield lex.token(T.MMANJE)
            elif lex >= "-":
                lex >> ">"
                yield lex.token(T.BIKOND)
            else:
                yield lex.token(T.MANJE)
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        elif znak == "-":
            if lex >= ">":
                yield lex.token(T.KOND)
            elif lex >= "-":
                yield lex.token(T.MINUSM)
            elif lex >= "=":
                yield lex.token(T.MINUSJ)
            elif lex >= "|":
                lex >> "|"
                yield lex.token(T.VRIJEDI)
            else:
                yield lex.token(T.MINUS)
        elif znak == "+":
            if lex >= "+":
                yield lex.token(T.PLUSP)
            elif lex >= "=":
                yield lex.token(T.PLUSJ)
            else:
                yield lex.token(T.PLUS)
        elif znak == "~":
            if lex >= "|":
                yield lex.token(T.NEVRIJEDI if lex >= "|" else T.NEVRIJEDI)
            else:
                yield lex.token(T.NEG)
        elif znak == "=":
            if lex >= "|":
                yield lex.token(T.VRIJEDI)
            else:
                yield lex.token(T.JJEDNAKO if lex >= "=" else T.JEDNAKO)
        elif znak == "|":
            if lex >= "=":
                yield lex.token(T.FORSIRA)
            elif lex >= "~":
                yield lex.token(T.NEFORSIRA)
            elif lex >= "|":
                if lex >= "-":
                    yield lex.token(T.FORSIRA)
                elif lex >= "~":
                    yield lex.token(T.NEFORSIRA)
            else:
                yield lex.token(T.DISJ)
        elif znak == "/":
            lex >> "/"
            lex - "\n"
            lex.zanemari()
        elif znak == "#":
            lex >> str.isalpha
            lex * {str.isalnum, "_"}
            yield lex.token(T.IME)
        elif znak == "$":
            lex + {str.isalnum, "_"}
            yield lex.token(T.PVAR)
        elif znak == "@":
            lex + {str.isalnum, "_"}
            yield lex.token(T.SVIJET)
        elif znak == "_":
            lex + {str.isalnum, "_"}
            yield lex.token(T.IMEF)
        elif znak.isupper():
            lex * {str.isalnum, "_"}
            yield lex.literal_ili(T.MODEL)
        elif znak == '"' or znak == "'":
            lex + (lambda char: char != znak and char != ".")
            lex >> "."
            lex >> "m"
            lex >> "i"
            lex >> "r"
            lex >> znak
            yield lex.token(T.IMED)
        elif znak.isalnum():
            lex * {str.isalnum, "_"}
            yield lex.literal_ili(T.IME)
        else:
            yield lex.literal(T)


### BKG ###
# start -> naredbe naredba
# naredbe -> '' | naredbe naredba | naredbe funkcija
# naredba -> petlja | grananje | ispis TOČKAZ | pridruživanje TOČKAZ | deklaracija TOČKAZ | BREAK TOČKAZ | CONTINUE TOČKAZ
# funkcija -> FUN IMEF O_OTV parametri? O_ZATV blok
# parametri -> tip IME | parametri ZAREZ tip IME
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
# ispis_varijabla -> IME (aritmetičko) | BROJ | NR
# varijable -> '' | varijable MMANJE ispis_varijabla
# ispis -> ISPIŠI varijable
# tip -> INT | NAT | FORMULA (ovo je odvojeno iako je pravilo trivijalno jer će biti još tipova s desne strane; vjerojatno ću još od aritmetičkih dodati nat i to će biti dovoljno)
# pridruživanje -> IME (aritmetičkog tipa) JEDNAKO izraz
# deklaracija -> tip IME JEDNAKO izraz
# formula -> PVAR | TRUE | FALSE | NEG formula | DIAMOND formula | BOX formula | O_OTV formula binvez formula O_ZATV
# binvez -> KONJ | DISJ | KOND | BIKOND

# formula -> IME (formule)
# formula -> IMEF O_OTV vrijednosti? O_ZATV
# vrijednosti -> IME
# pridruživanje -> IME (formule) JEDNAKO IME (formule)
# deklaracija -> FORMULA IME JEDNAKO formula
# ispis_varijabla -> IME (formula)
# uvjet -> IME (formule) JJEDNAKO IME (formule)

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

# naredba -> FOREACH (SVIJET | PVAR) blok
# naredba -> SPREMI MODEL TOČKAZ
# poziv_funkcije -> IMEF O_OTV IME* O_ZATV
# pridruživanje -> IME (formule) JEDNAKO poziv_funkcije TOČKAZ
# naredba -> poziv_funkcije TOČKAZ
# naredba -> vrati TOČKAZ
# vrati -> VRATI (TRUE | FALSE) TOČKAZ


class P(Parser):
    def start(p):
        naredbe = [p.naredba()]
        while not p > KRAJ:
            naredbe.append(p.naredba())
        return Program(naredbe)

    def naredba(p):
        if p > T.FOR:
            return p.for_petlja()
        if p > T.FOREACH:
            return p.foreach_petlja()
        if p > T.ISPIŠI:
            return p.ispis()
        if p > T.IF:
            return p.grananje()
        if p > {T.INT, T.NAT, T.FORMULA}:
            return p.deklaracija()
        if ime := p >= T.IME:
            if p >= T.JEDNAKO:
                return p.pridruživanje(ime)
            if p >= T.UPITNIK:
                return p.provjera(ime)
        if p > T.SVIJET:
            return p.forsira()
        if p > T.PVAR:
            return p.vrijedi()
        if p > T.KORISTI:
            return p.koristi()
        if p > T.SPREMI:
            return p.spremi()
        if p > T.UNESI:
            return p.unos()
        if p > T.VRATI:
            return p.vrati_konstantu()
        if p > T.FUN:
            return p.deklaracija_funkcije()
        if p > T.IMEF:
            return p.poziv_funkcije()
        if br := p >= T.BREAK:
            p >> T.TOČKAZ
            return br
        if cont := p >= T.CONTINUE:
            p >> T.TOČKAZ
            return cont
        return p.formula()

    def deklaracija_funkcije(p):
        p >> T.FUN
        ime_funkcije = p >> T.IMEF
        p >> T.O_OTV
        parametri = []
        if param_tip := p >= {T.INT, T.NAT, T.FORMULA}:
            param_ime = p >> T.IME
            parametri.append([param_ime, param_tip])
        while p >= T.ZAREZ:
            param_tip = p >> {T.INT, T.NAT, T.FORMULA}
            param_ime = p >> T.IME
            parametri.append([param_ime, param_tip])
        p >> T.O_ZATV

        return Deklaracija_funkcije(ime_funkcije, parametri, p.blok())

    def poziv_funkcije(p):
        ime = p >> T.IMEF
        p >> T.O_OTV
        argumenti = []
        if arg := p >= T.IME:
            argumenti.append(arg)
        while arg := p >= T.ZAREZ:
            argumenti.append(p >> T.IME)
        p >> T.O_ZATV
        p >> T.TOČKAZ
        return Poziv_funkcije(ime, argumenti)

    def vrati_konstantu(p):
        p >> T.VRATI
        konst = p >> {T.FALSE, T.TRUE}
        p >> T.TOČKAZ
        return Vrati_konstantu(konst)

    def spremi(p):
        p >> T.SPREMI
        model = p >> T.MODEL
        p >> T.TOČKAZ
        return Spremi(model)

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
        while p >= T.MMANJE:
            datoteke.append(p >> T.IMED)
        p >> T.TOČKAZ
        return Unos(datoteke)

    def funkcija(p):
        ime_funkcije = p >> T.IMEF
        p >> T.O_OTV
        parametri = []
        if param_tip := p >= {T.INT, T.NAT, T.FORMULA}:
            param_ime = p >> T.IME
            parametri.append([param_ime, param_tip])
        while p >= T.ZAREZ:
            parametri.append([p >> {T.INT, T.NAT, T.FORMULA}, p >> T.IME])
        p >> T.O_ZATV
        return Funkcija(ime_funkcije, parametri, p.blok())

    def provjera(p, ime):
        w = p >> T.SVIJET
        p >> T.TOČKAZ
        return Provjera(w, ime)

    def for_petlja(p):
        kriva_varijabla = SemantičkaGreška(
            "Sva tri dijela for-petlje moraju imati istu varijablu"
        )

        p >> T.FOR, p >> T.O_OTV
        i = p >> T.IME
        p >> T.JEDNAKO
        početak = p.izraz()  ## u AST for_petlja pazimo ako se vrati ime formule
        p >> T.TOČKAZ

        if (p >> T.IME) != i:
            raise kriva_varijabla
        for_operator = p >> {
            T.MANJE,
            T.VEĆE,
        }  # ovdje se lako doda ako hocemo podrzati jos neke operatore
        granica = p.izraz()  ## u AST for_petlja pazimo ako se vrati ime formule
        p >> T.TOČKAZ

        if (p >> T.IME) != i:
            raise kriva_varijabla
        if minus_ili_plus := p >= {T.PLUSP, T.MINUSM}:
            promjena = nenavedeno
        elif minus_ili_plus := p >> {T.PLUSJ, T.MINUSJ}:
            promjena = p.izraz()  ## u AST for_petlja pazimo ako se vrati ime formule
        p >> T.O_ZATV

        blok = p.blok()
        return For_Petlja(
            i, početak, for_operator, granica, promjena, minus_ili_plus, blok
        )

    # blok može biti ili jedna naredba ili {naredbe*} !!!
    def blok(p):
        naredbe = []
        if p >= T.V_OTV:
            while not p >= T.V_ZATV:
                naredbe.append(p.naredba())
        else:
            naredbe.append(p.naredba())

        return Blok(naredbe)

    def ispis(p):
        p >> T.ISPIŠI
        varijable = []
        while p >= T.MMANJE:
            varijable.append(p >> {T.IME, T.BROJ, T.SVIJET, T.MODEL, T.NR})
        p >> T.TOČKAZ
        return Ispis(varijable)

    def grananje(p):
        p >> T.IF, p >> T.O_OTV
        uvjet = p.uvjet()
        p >> T.O_ZATV
        if_blok = p.blok()
        else_blok = nenavedeno
        if p >= T.ELSE:
            else_blok = p.blok()
        return Grananje(uvjet, if_blok, else_blok)

    def uvjet(p):
        lijeva_strana = p >> {T.IME, T.BROJ}
        op = p >> {T.JJEDNAKO, T.MANJE, T.VEĆE, T.UPITNIK}
        desna_strana = p >> {T.IME, T.BROJ, T.SVIJET}
        return Uvjet(lijeva_strana, op, desna_strana)

    def pridruživanje(p, ime_varijable):
        if ime_varijable.sadržaj[0] == "#":  ## ako pridružujemo aritmetičkom izrazu
            vrijednost = p.izraz()
        elif ime_varijable.sadržaj[0].islower() and p > T.IMEF:
            vrijednost = p.poziv_funkcije()
            return Pridruživanje(ime_varijable, vrijednost)
        elif ime_varijable.sadržaj[0].islower():  ## ako pridružujemo formuli
            vrijednost = p.formula()
        else:
            raise SintaksnaGreška(
                f"Pridruživanje nije podržano za varijablu {ime_varijable.sadržaj}"
            )
        p >> T.TOČKAZ
        return Pridruživanje(ime_varijable, vrijednost)

    def deklaracija(p):
        tip = p >> {
            T.INT,
            T.NAT,
            T.FORMULA,
        }  # kad budemo imali vise tipova, onda cemo imati p > {T.INT, T.FORMULA...}
        ime = p >> T.IME
        p >> T.JEDNAKO
        if tip ^ {T.INT, T.NAT}:  ## ako deklariramo aritmetički izraz
            vrij = p.izraz()
        elif tip ^ T.FORMULA:  ## ako deklariramo varijablu
            vrij = p.formula()
        else:
            raise SintaksnaGreška(f"Za tip {tip} nije podržana deklaracija!")
        p >> T.TOČKAZ
        return Deklaracija(tip, ime, vrij)

    def izraz(p):
        t = p.član()
        while op := p >= {T.PLUS, T.MINUS}:
            t = Op(op, t, p.član())
        return t

    def član(p):
        t = p.faktor()
        while op := p >= {T.PUTA, T.OSTATAK}:
            t = Op(op, t, p.faktor())
        return t

    def faktor(p):
        if op := p >= T.MINUS:
            return Op(op, nenavedeno, p.faktor())
        baza = p.baza()
        if p >= T.NA:
            return Potencija(baza, p.faktor())
        else:
            return baza

    def baza(p):
        if elementarni := p >= {T.BROJ, T.IME}:
            return elementarni
        elif p >> T.O_OTV:
            u_zagradi = p.izraz()
            p >> T.O_ZATV
            return u_zagradi

    def formula(p):
        if varijabla := p >= {T.PVAR, T.IME}:
            return varijabla
        elif konstanta := p >= {T.TRUE, T.FALSE}:
            return konstanta
        elif p > {T.BOX, T.DIAMOND, T.NEG}:
            klasa, ispod = p.unvez(), p.formula()
            return klasa(ispod)
        elif p >= T.O_OTV:
            l, klasa, d = p.formula(), p.binvez(), p.formula()
            p >> T.O_ZATV
            return klasa(l, d)
        raise SintaksnaGreška("Nepoznata naredba")

    def unvez(p):
        if p >= T.NEG:
            return Negacija
        elif p >= T.DIAMOND:
            return Diamond
        elif p >= T.BOX:
            return Box
        else:
            raise p.greška()

    def binvez(p):
        if p >= T.KONJ:
            return Konjunkcija
        elif p >= T.DISJ:
            return Disjunkcija
        elif p >= T.KOND:
            return Kondicional
        elif p >= T.BIKOND:
            return Bikondicional
        else:
            raise p.greška()

    def forsira(p):
        w = p >> T.SVIJET
        simb = p >> {T.FORSIRA, T.NEFORSIRA}
        lista_pvar = []
        if p >= T.V_OTV:
            lista_pvar.append(p >> T.PVAR)
            while p >= T.ZAREZ:
                lista_pvar.append(p >> T.PVAR)
            p >> T.V_ZATV
        else:
            lista_pvar.append(p >> T.PVAR)
        p >> T.TOČKAZ
        return Forsira(w, lista_pvar, simb)

    def vrijedi(p):
        pvar = p >> T.PVAR
        simb = p >> {T.VRIJEDI, T.NEVRIJEDI}
        lista_svijet = []
        if p >= T.V_OTV:
            lista_svijet.append(p >> T.SVIJET)
            while p >= T.ZAREZ:
                lista_svijet.append(p >> T.SVIJET)
            p >> T.V_ZATV
        else:
            lista_svijet.append(p >> T.SVIJET)
        p >> T.TOČKAZ
        return Vrijedi(pvar, lista_svijet, simb)


class Program(AST):
    naredbe: "barem jedna naredba"

    def izvrši(program):
        try:
            for naredba in program.naredbe:
                naredba.izvrši()
        except PrekidBreak:
            raise SemantičkaGreška("Nedozvoljen break izvan petlje!")
        except PrekidContinue:
            raise SemantičkaGreška("Nedozvoljen continue izvan petlje!")


class Spremi(AST):
    ime: "MODEL"

    def izvrši(spremi):
        if "using" not in rt.mem:
            raise SemantičkaGreška("Niste još deklarirali model!")
        elif spremi.ime.sadržaj != rt.mem["using"].sadržaj:
            raise SemantičkaGreška(
                f"Model {spremi.ime.sadržaj} ne postoji! Trenutno deklarirani model je {rt.mem['using'].sadržaj}."
            )

        rel_filename = "rel_dat" + spremi.ime.sadržaj + ".mir"
        val_filename = "val_dat" + spremi.ime.sadržaj + ".mir"

        with open(rel_filename, "w") as file:
            row = "rel"
            for svijet in rt.mem["using"].nosač:
                f_svijet = svijet.sadržaj
                f_svijet = f_svijet.replace("@", " ")
                row += f_svijet
            file.write(row + "\n")

            row = ""
            for svijet in rt.mem["using"].nosač:
                f_svijet = svijet.sadržaj
                f_svijet = f_svijet.replace("@", "")
                row = f_svijet
                for svijet1 in rt.mem["using"].nosač:
                    if svijet1 in svijet.sljedbenici:
                        row += " 1"
                    else:
                        row += " 0"
                file.write(row + "\n")
                row = ""

        with open(val_filename, "w") as file:
            row = "valuacija"
            for cinjenica in rt.mem["using"].pvars:
                f_cinjenica = cinjenica.sadržaj
                f_cinjenica = f_cinjenica.replace("$", " ")
                row += f_cinjenica
            file.write(row + "\n")

            row = ""
            for svijet in rt.mem["using"].nosač:
                f_svijet = svijet.sadržaj
                f_svijet = f_svijet.replace("@", "")
                row = f_svijet
                for cinjenica in rt.mem["using"].pvars:
                    if cinjenica in svijet.činjenice:
                        row += " 1"
                    else:
                        row += " 0"
                file.write(row + "\n")
                row = ""

        print(
            f"Podaci o relaciji i valuaciji modela {spremi.ime.sadržaj} su spremljeni u datoteke {rel_filename} i {val_filename}."
        )


class Koristi(AST):
    model: T.MODEL

    def izvrši(self):
        rt.mem["using"] = self.model


class Unos(AST):
    datoteke: "list(T.IMED)"

    def izvrši(self):
        for dat in self.datoteke:
            with open(dat.vrijednost(), newline="") as csv_dat:
                reader = csv.reader(csv_dat, delimiter=" ")
                prvi_red = next(reader)
                tip = prvi_red[0][:3]
                if tip == "rel":
                    svjetovi = []
                elif tip == "val":
                    pvars = []
                else:
                    raise IOError('Neispravan tip datoteke: mora biti "rel" ili "val".')
                    return -1
                if tip == "rel":
                    for i in range(1, len(prvi_red)):
                        if novi := rt.mem["using"].nađi_svijet("@" + prvi_red[i]):
                            if novi in svjetovi:
                                raise IOError("Svijet se navodi dvaput.")
                            else:
                                svjetovi.append(novi)
                        else:
                            raise IOError("Svijet nije deklariran.")
                else:
                    for i in range(1, len(prvi_red)):
                        if nova := rt.mem["using"].nađi_pvar("$" + prvi_red[i]):
                            if nova in pvars:
                                raise IOError(
                                    "Propozicionalna varijabla navodi se dvaput."
                                )
                            else:
                                pvars.append(nova)
                        else:
                            raise IOError("Propozicionalna varijabla nije deklarirana.")
                for redak in reader:
                    lijevi = rt.mem["using"].nađi_svijet("@" + redak[0])
                    for i in range(1, len(redak)):
                        if str.upper(redak[i][0]) in ["T", "1", "Y", "I", "D", "O"]:
                            if tip == "rel":
                                lijevi.sljedbenici.add(svjetovi[i - 1])
                            else:
                                lijevi.činjenice.add(pvars[i - 1])
                        elif str.upper(redak[i][0]) in ["F", "0", "N", "L", "N", "X"]:
                            if tip == "rel":
                                lijevi.sljedbenici.discard(svjetovi[i - 1])
                            else:
                                lijevi.činjenice.discard(pvars[i - 1])
                        else:
                            raise IOError("Neispravna oznaka istinitosti u tablici.")


class Vrati_konstantu(AST):
    konstanta: "FALSE|TRUE"

    def izvrši(self):
        rt.lm["return"] = self.konstanta


class Deklaracija_funkcije(AST):
    ime: "T.IMEF"
    parametri: "[IME, TIP]*"
    blok: "naredba*"

    def izvrši(dekl_fje):
        rt.fje[dekl_fje.ime] = Funkcija(dekl_fje.ime, dekl_fje.parametri, dekl_fje.blok)


class Poziv_funkcije(AST):
    ime: "IMEF"
    argumenti: "IME*"

    def izvrši(fja):
        parametri = rt.fje[fja.ime].parametri

        if len(fja.argumenti) != len(parametri):
            raise GreškaIzvođenja(
                f"{fja.ime} mora primiti {len(parametri)} parametara!"
            )

        kopija_memorije = rt.mem
        lokalna_memorija = Memorija()

        i = 0
        j = 0
        for parametar in parametri:
            j = 0
            for argument in fja.argumenti:
                if i == j:
                    if parametar[1] == Token(T.FORMULA):
                        if (
                            argument.sadržaj[0] == "#"
                            or not argument.sadržaj[0].islower()
                        ):
                            raise GreškaIzvođenja(
                                f"{fja.ime} nije dobila kompatibilne parametre!"
                            )
                    elif parametar[1] == Token(T.INT) or parametar[1] == Token(T.NAT):
                        if not argument.sadržaj[0] == "#":
                            raise GreškaIzvođenja(
                                f"{fja.ime} nije dobila kompatibilne parametre!"
                            )

                    lokalna_memorija[parametar[0]] = rt.mem[argument]
                    lokalna_memorija[parametar[0]] = copy.deepcopy(
                        lokalna_memorija[parametar[0]]
                    )

                    if lokalna_memorija[parametar[0]][1] == Token(
                        T.INT
                    ) or lokalna_memorija[parametar[0]][1] == Token(T.NAT):
                        lokalna_memorija[parametar[0]].append(".")
                    break
                j += 1
            i += 1

        rt.mem = lokalna_memorija

        rt.fje[fja.ime].izvrši(fja.argumenti)

        del rt.mem
        rt.mem = kopija_memorije


class Funkcija(AST):
    ime: "T.IMEF"
    parametri: "[IME, TIP]*"
    blok: "naredba*"

    def izvrši(self, argumenti):
        if len(argumenti) != len(self.parametri):
            raise GreškaIzvođenja(
                f"{self.ime} mora primiti {len(self.parametri)} parametara!"
            )

        self.blok.izvrši()


class Foreach_petlja(AST):
    ime: "(SVIJET | PVAR)"
    blok: "naredba+"

    def izvrši(self):
        if "using" not in rt.mem:
            raise SemantičkaGreška("Potrebno je prvo deklarirati model!")

        for element in (
            rt.mem["using"].nosač if self.ime ^ T.SVIJET else rt.mem["using"].pvars
        ):
            try:
                if self.ime ^ T.SVIJET:
                    self.ime.sljedbenici = element.sljedbenici
                    self.ime.činjenice = element.činjenice
                    rt.mem["temp"] = self.ime
                elif self.ime ^ T.PVAR:
                    rt.mem["temp"] = element
                else:
                    raise SemantičkaGreška(
                        "Nepodržan tip podatka unutar foreach petlje!"
                    )
                self.blok.izvrši()
            except PrekidBreak:
                break
            except PrekidContinue:
                continue

        del rt.mem["temp"]


class For_Petlja(AST):
    varijabla: "IME"
    početak: "izraz"
    operator: "(<|>)"
    granica: "izraz"
    promjena: "izraz?"
    predznak: "(+|-)"
    blok: "naredba*"

    def izvrši(petlja):
        neadekvatna_desna_strana = SemantičkaGreška(
            "Greška: nad formulama nisu definirane aritmetičke operacije!"
        )
        kv = petlja.varijabla

        # donja tri uvjeta provjeravaju da se s desne strane ne nađe formula
        if petlja.početak ^ T.IME and petlja.početak.sadržaj[0] != "#":
            raise neadekvatna_desna_strana
        elif petlja.granica ^ T.IME and petlja.granica.sadržaj[0] != "#":
            raise neadekvatna_desna_strana
        elif petlja.promjena ^ T.IME and petlja.promjena.sadržaj[0] != "#":
            raise neadekvatna_desna_strana

        memo = rt.mem if fun == "__main__" else rt.lm[fun]
        memo[kv] = [petlja.početak.vrijednost()]
        while (
            memo[kv][0] < petlja.granica.vrijednost()
            if petlja.operator ^ T.MANJE
            else memo[kv][0] > petlja.granica.vrijednost()
        ):
            try:
                petlja.blok.izvrši()
            except PrekidBreak:
                break
            except PrekidContinue:
                prom = petlja.promjena
                if petlja.predznak ^ T.MINUSJ or petlja.predznak ^ T.MINUSM:
                    memo[kv][0] -= prom.vrijednost() if prom else 1
                else:
                    memo[kv][0] += prom.vrijednost() if prom else 1
                continue
            prom = petlja.promjena
            if petlja.predznak ^ T.MINUSJ or petlja.predznak ^ T.MINUSM:
                memo[kv][0] -= prom.vrijednost() if prom else 1
            else:
                memo[kv][0] += prom.vrijednost() if prom else 1
        del memo[kv]


class Blok(AST):
    naredbe: "naredba*"

    def izvrši(blok):
        for naredba in blok.naredbe:
            naredba.izvrši()


class Ispis(AST):
    varijable: "IME*"

    def izvrši(ispis):
        for varijabla in ispis.varijable:
            if varijabla ^ {T.INT, T.NAT, T.FORMULA, T.BROJ, T.IME}:
                if "temp" in rt.mem:
                    print(rt.mem["temp"].ispis())
                else:
                    print(varijabla.ispis(), end=" ")
            elif varijabla ^ {T.SVIJET}:
                if svijet := rt.mem["using"].nađi_svijet(varijabla.sadržaj):
                    print(svijet.ispis())
                elif "temp" in rt.mem:
                    print(rt.mem["temp"].ispis())
                else:
                    raise SemantičkaGreška(
                        f"Svijet {varijabla.sadržaj} nije deklariran."
                    )
            elif varijabla ^ {T.MODEL}:
                if rt.mem["using"].sadržaj == varijabla.sadržaj:
                    print(rt.mem["using"].ispis())
                else:
                    raise SemantičkaGreška(
                        f"Model {varijabla.sadržaj} nije trenutno u uporabi."
                    )
            elif varijabla ^ T.NR:
                print()
            else:
                raise SemantičkaGreška("Neočekivana varijabla za ispis!")


class Uvjet(AST):
    lijeva: "(IME|BROJ)"
    operator: "(==|<|>|?)"
    desna: "(IME|BROJ)"

    def ispunjen(uvjet):
        if uvjet.lijeva ^ T.IME and uvjet.lijeva.sadržaj[0].islower():
            if uvjet.operator ^ T.JJEDNAKO:
                if uvjet.desna ^ T.IME and not uvjet.desna.sadržaj[0].islower():
                    raise SemantičkaGreška(
                        "Uspoređivanje formule s nekompatibilnim tipom!"
                    )
                else:
                    return uvjet.lijeva.ispis() == uvjet.desna.ispis()
            elif uvjet.operator ^ T.UPITNIK:
                if not uvjet.desna ^ T.SVIJET:
                    raise SemantičkaGreška("Provjera formule na nekompatibilnom tipu!")
                else:
                    return Provjera(uvjet.desna, uvjet.lijeva).vrijednost()
            else:
                raise SemantičkaGreška("Nepodržan operator na tipu formula!")

        # ovo ispod bez problema prolazi za aritmetičke vrijednosti s lijeve i desne strane
        if uvjet.operator ^ T.JJEDNAKO:
            return uvjet.lijeva.vrijednost() == uvjet.desna.vrijednost()
        elif uvjet.operator ^ T.VEĆE:
            return uvjet.lijeva.vrijednost() > uvjet.desna.vrijednost()
        elif uvjet.operator ^ T.MANJE:
            return uvjet.lijeva.vrijednost() < uvjet.desna.vrijednost()
        else:
            raise SintaksnaGreška("Nepodržan if-uvjet!")


class Grananje(AST):
    uvjet: "log"
    onda: "naredba"
    inače: "naredba"

    def izvrši(grananje):
        if grananje.uvjet.ispunjen():
            grananje.onda.izvrši()
        elif grananje.inače:
            grananje.inače.izvrši()


class Pridruživanje(AST):
    varijabla: "IME"
    vrij: "(varijabla | BROJ | poziv funkcije)"

    def izvrši(pridruživanje):
        memo = rt.mem if fun == "__main__" else rt.lm[fun]
        if isinstance(pridruživanje.vrij, Poziv_funkcije):
            pridruživanje.vrij.izvrši()
            memo[pridruživanje.varijabla][0] = rt.lm["return"]
            return
        if pridruživanje.varijabla in memo:
            if (
                pridruživanje.varijabla.sadržaj[0] == "#"
            ):  # ovo se odnosi na pridruživanje aritmetičkim varijablama (int, nat)
                if pridruživanje.vrij ^ T.IME and pridruživanje.vrij.sadržaj[0] != "#":
                    raise SemantičkaGreška(
                        "Greška: nepravilno pridruživanje aritmetičkoj varijabli!"
                    )
                elif (
                    memo[pridruživanje.varijabla][1] ^ T.NAT
                    and pridruživanje.vrij.vrijednost() < 0
                ):
                    greska = GreskaTipova()
                    greska.krivi_tip(pridruživanje.varijabla.sadržaj, Tip.N, Tip.Z)
                else:
                    memo[pridruživanje.varijabla][0] = pridruživanje.vrij.vrijednost()
            elif pridruživanje.varijabla.sadržaj[
                0
            ].islower():  # ovo se odnosi na pridruživanje formulama
                if (
                    pridruživanje.vrij ^ T.IME
                    and not pridruživanje.vrij.sadržaj[0].islower()
                ):
                    raise SemantičkaGreška(
                        "Greška: nepravilno pridruživanje varijabli formula!"
                    )
                else:
                    memo[pridruživanje.varijabla][0] = pridruživanje.vrij.pozovi()
        else:
            return memo[
                pridruživanje.varijabla
            ]  # jer ovo vraca bas ono upozorenje koje nam treba


class Deklaracija(AST):
    tip: "neki od podrzanih tipova"
    ime: "IME"
    vrij: "varijabla | BROJ"

    # prilikom deklaracije, kljucevi se preslikavaju u listu s dva elementa (par): vrijednost, tip
    def izvrši(deklaracija):
        memo = rt.mem if fun == "__main__" else rt.lm[fun]
        if deklaracija.ime in memo:  ## ako se dogodila redeklaracija
            raise deklaracija.ime.redeklaracija()
        elif deklaracija.tip ^ {T.NAT, T.INT}:  ## ako deklariramo aritmeticki tip
            if deklaracija.tip ^ T.NAT and deklaracija.vrij.vrijednost() < 0:
                tip1 = Tip.N
                tip2 = Tip.Z
                greska = GreskaTipova()
                greska.krivi_tip(deklaracija.ime.sadržaj, tip1, tip2)
            elif not deklaracija.ime.sadržaj[0] == "#":
                raise SemantičkaGreška("Neispravan naziv varijable aritmetičkog tipa!")
            elif deklaracija.vrij ^ T.IME and not deklaracija.vrij.sadržaj[0] == "#":
                raise SemantičkaGreška(
                    f"Nepodudaranje tipova prilikom deklaracije aritmetičke varijable {deklaracija.ime.sadržaj}!"
                )
            else:
                memo[deklaracija.ime] = [deklaracija.vrij.vrijednost(), deklaracija.tip]
        elif deklaracija.tip ^ T.FORMULA:  ## ako deklariramo formulu
            if deklaracija.vrij ^ T.IME and not deklaracija.vrij.sadržaj[0].islower():
                raise SemantičkaGreška(
                    f"Nepodudaranje tipova prilikom deklaracije formule {deklaracija.ime.sadržaj}!"
                )
            elif (
                not deklaracija.ime.sadržaj.islower()
                or deklaracija.ime.sadržaj[0] == "#"
            ):
                raise SemantičkaGreška("Neispravan naziv varijable tipa formula!")
            else:
                memo[deklaracija.ime] = [deklaracija.vrij.pozovi(), deklaracija.tip]
        else:
            raise SemantičkaGreška(
                "Nepodržani tip varijable!"
            )  # ne bi smjelo do ovoga doći jer za to imamo provjeru u odg. metodi


class Op(AST):
    op: "T"
    lijevo: "izraz?"
    desno: "izraz"

    def vrijednost(self):
        if self.lijevo is nenavedeno:
            l = 0
        else:
            l = self.lijevo.vrijednost()
        o, d = self.op, self.desno.vrijednost()
        if o ^ T.PLUS:
            return l + d
        elif o ^ T.MINUS:
            return l - d
        elif o ^ T.PUTA:
            return l * d
        elif o ^ T.OSTATAK:
            return l % d


class Potencija(AST):
    baza: "elementarni | izraz"
    eksponent: "faktor"

    def vrijednost(self):
        if self.eksponent.vrijednost() < 0:
            raise SemantičkaGreška(
                f"Nepodržano potenciranje s negativnim eksponentom {self.eksponent.vrijednost()}!"
            )
        return self.baza.vrijednost() ** self.eksponent.vrijednost()


class Unarna(AST):
    ispod: "formula"

    def optim(self):
        klasa = type(self)
        ispod_opt = self.ispod.optim()
        if ispod_opt ^ Negacija and self ^ Negacija:
            return ispod_opt.ispod
        else:
            return klasa(ispod_opt)

    def optim1(self):
        klasa = type(self)
        if isinstance(self, Diamond):
            ispod_opt = self.ispod.optim1()
            nova_klasa = Negacija(ispod_opt)
            nova_klasa = Box(nova_klasa)
            return Negacija(nova_klasa)
        else:
            return self

    def __eq__(self, o):
        return jednaki(self.ispod, o.ispod)

    def ispis(self):
        return self.veznik + self.ispod.ispis()

    # provjeri ovo
    def izvrši(self):
        return self.ispis()

    def pozovi(self):
        return self


class Negacija(Unarna):
    veznik = "¬"

    def vrijednost(self, w):
        return not self.ispod.vrijednost(w)


class Diamond(Unarna):
    veznik = "◆"

    def vrijednost(self, w):
        for sljedbenik in w.sljedbenici:
            if self.ispod.vrijednost(sljedbenik):
                return True
        return False


class Box(Unarna):
    veznik = "■"

    def vrijednost(self, w):
        for sljedbenik in w.sljedbenici:
            if not self.ispod.vrijednost(sljedbenik):
                return False
        return True


class Binarna(AST):
    lijevo: "formula"
    desno: "formula"

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
        else:
            return self

    def __eq__(self, o):
        return jednaki(self.lijevo, o.lijevo) and jednaki(self.desno, o.desno)

    def ispis(self):
        return "(" + self.lijevo.ispis() + self.veznik + self.desno.ispis() + ")"

    # provjeri ovo
    def izvrši(self):
        return self.ispis()

    def pozovi(self):
        return self


class Disjunkcija(Binarna):
    veznik = "∨"

    def vrijednost(self, w):
        return self.lijevo.vrijednost(w) or self.desno.vrijednost(w)


class Konjunkcija(Binarna):
    veznik = "∧"

    def vrijednost(self, w):
        return self.lijevo.vrijednost(w) and self.desno.vrijednost(w)


class Kondicional(Binarna):
    veznik = "→"

    def vrijednost(self, w):
        return self.lijevo.vrijednost(w) <= self.desno.vrijednost(w)


class Bikondicional(Binarna):
    veznik = "↔"

    def vrijednost(self, w):
        return self.lijevo.vrijednost(w) == self.desno.vrijednost(w)


class Provjera(AST):
    svijet: T.SVIJET
    ime: "ime formule"

    def izvrši(self):
        if svijet := rt.mem["using"].nađi_svijet(self.svijet.sadržaj):
            t = " ⊩ " if self.ime.vrijednost().vrijednost(svijet) else " ⊮ "
            print(svijet.sadržaj + t + self.ime.vrijednost().ispis())
        else:
            raise SemantičkaGreška(f"Svijet {self.svijet.sadržaj} nije deklariran.")

    def vrijednost(self):
        if svijet := rt.mem["using"].nađi_svijet(self.svijet.sadržaj):
            return self.ime.vrijednost().vrijednost(svijet)
        else:
            raise SemantičkaGreška(f"Svijet {self.svijet.sadržaj} nije deklariran.")


class Forsira(AST):
    svijet: T.SVIJET
    pvars: "list(T.PVAR)"
    simbol: "T.FORSIRA | T.NEFORSIRA"

    def izvrši(self):
        if svijet := rt.mem["using"].nađi_svijet(self.svijet.sadržaj):
            for pvar in self.pvars:
                if self.simbol ^ T.FORSIRA:
                    svijet.činjenice.add(pvar)
                elif self.simbol ^ T.NEFORSIRA:
                    svijet.činjenice.discard(pvar)
        else:
            raise SemantičkaGreška(f"Svijet {self.svijet.sadržaj} nije deklariran.")


class Vrijedi(AST):
    pvar: T.PVAR
    svjetovi: "list(T.SVIJET)"
    simbol: "T.VRIJEDI | T.NEVRIJEDI"

    def izvrši(self):
        for s in self.svjetovi:
            if svijet := rt.mem["using"].nađi_svijet(s.sadržaj):
                if self.simbol ^ T.VRIJEDI:
                    svijet.činjenice.add(self.pvar)
                elif self.simbol ^ T.NEVRIJEDI:
                    svijet.činjenice.discard(self.pvar)
            else:
                raise SemantičkaGreška(f"Svijet {self.svijet.sadržaj} nije deklariran.")


def optimiziraj(formula):
    """Pretvara formulu (AST) u formulu koja od veznika ima samo kondicional i negaciju; prije te pretvorbe su još uklonjene dvostruke negacije"""

    nova = (
        formula.optim()
    )  # prije optimizacije da dobijemo samo negaciju i kondicional uklanjamo redundantne negacije
    nova = (
        nova.optim1()
    )  # kreiramo ekvivalentnu formulu koja ima samo negaciju, kondicional i box od veznika
    return (
        nova.optim()
    )  # nakon dobivanja ekvivalentne formule opet se mogu javiti redundantne negacije pa ih zato još jednom mičemo


def jednaki(f1, f2):
    klasa1 = type(f1)
    klasa2 = type(f2)

    if klasa1 != klasa2:
        return False
    return f1 == f2


# provjerava je li formula f shema aksioma A1
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
fun = "__main__"
rt.lm = Memorija()
rt.fje = Memorija(redefinicija=False)

### ISPOD JE SVE ZA REALIZACIJU KORISNIČKOG UNOSA ###


# u interaktivnom nacinu rada omoguciti unos programa koji je natipkan u
# nekoj .txt datoteci. Ako je program napisan u program.txt, onda se
# poziva s unos_programa("program.txt")
def unos_programa(ime_txt_dat):
    with open(ime_txt_dat, "r") as file:
        lines = file.readlines()
    naredbe = ""
    for line in lines:
        naredbe += line

    P(naredbe).izvrši()


######################### interaktivni način rada ###############################


def main():
    # ispis uputa
    print(10 * "-" + " MODALNA LOGIKA " + 10 * "-")
    print("Naredbe završavaju znakom ';'.")
    print("Za izvršavanje unesenog bloka dvaput pritisnite Enter.")
    print("Unesite 'bye' ili 'exit' za kraj rada.")
    print("'napravi <ime_datoteke>.mir' izvršava skriptu u toj datoteci.")
    print(60 * "-")

    block = ""
    while True:
        print(
            ">", end=" "
        )  # ispisuje oznaku da smo unutar naše ljuske bez prelaska u novi red
        line = ""
        line = input()  # čeka input korisnika

        # IZLAZ IZ PROGRAMA
        if line in {"bye", "exit"}:  # kraj rada
            exit()

        # NAPRAVI SKRIPTU
        elif line[:7] == "napravi":
            block = ""  # resetira do sad uneseno
            s = line.split(" ")
            script = s[1]  # drugi element je naziv datoteke

            if not script[-4:] == ".mir":
                print("Tip datoteke mora biti .mir!")
                continue

            if not len(s) == 2:
                print("Previše argumenata! Koristiti: napravi <ime_datoteke>.mir")
                continue

            # print("izvršavam skriptu " + script)
            try:
                f = open(script, "r")
            except:
                print("Greška prilikom otvaranja datoteke. Postoji li?")
            else:
                # uspješno otvaranje
                # print(">", end=" ")
                try:
                    P(f.read()).izvrši()
                except Exception as e:
                    print(e)
                # print("datoteka: " + f.read())
                f.close()
                print("")

        # DVOSTRUKI ENTER
        elif line == "" and not block == "":  # block sadrži odsječak koda
            # print("blok koda:")
            # print(block)
            try:
                P(block).izvrši()  # izvršavamo kod
            except Exception as e:
                print(e)
            block = ""  # reset
            print("")

        # KONKATENACIJA NOVE LINIJE U TRENUTNI BLOK KODA
        elif not line == "":  # linija koda unesena
            block += line + "\n"

        # NEBTINI PRELASCI U NOVI RED
        elif line == "":
            pass  # ignoriramo bezvezno unošenje novih redova


unos_programa("program5.txt")
