# IP
Projekt iz interpretacije programa (solver/proof-checker za modalnu logiku)

# Organizacija

* *main.py* je glavni source code u kojem će biti aplikacija
* **je li ok da svatko ima svoj module u koji implementira neki dio zadatka pa sve kombiniramo nakon suglasnosti u *main.py*?**

# Sadržaj

## 1. interaktivni način rada
* poslije svake naredbe dolazi znak `;`
* ako korisnik unese liniju na kraju koje ne stoji `;`, ispisuje se nešto poput `...` kao naznaka za prelazak u novi red
	* primjer stanja konzole: 
```
> <prvi dio naredbe> \n
> ... <drugi dio> \n
> ... <treci dio>; \n
// nakon ovoga je unos gotov
```

## 2. Aritmetika

## 3. Petlje 
for i while petlja + if

## 4. Funkcije
definicija funkcija i funkcijski pozivi. Primjer funkcija: ... 

## 5. Tipovi podataka
### propozicionalna varijabla (beskonačan)
* naziv oblika `p#` gdje je # neki prirodan broj
\\ ------------ PRIJEDLOG -----------------
* naziv oblika `( _<riječ> )+ `
	* npr. `_pada_kisa` 
	* kako bismo mogli semantički razmišljati o njima
	* radi se o proširenju jer i dalje imamo mogućnost `_p#`

### formula (beskonačan)
* bilo koji naziv, ali da je prvo slovo malo i da nije `p` ili `w`
* definicija kao npr. `primjerFormule = p0 -> !(<>p1 -> p2)`
\\ ------------ PRIJEDLOG ---------------------------
* ako prop. var. počinju s `_`, a svijetovi s `$`, formule mogu imati proizvoljan početak (alfanumerički)

### svijet (beskonačan)
* naziv oblika `w#` gdje je # neki prirodan broj
* ili da naziv bude samo prirodan broj?
\\ ------------ PRIJEDLOG ----------------
* naziv oblika `$<riječ> (_<riječ>)+`
	* npr. `$oblaci`
	* i sada je  jako intuitivno razmišljati o izrazu `$oblacni |- {_pada_kisa _nema_sunca}` 

### relacija (beskonačna)
* naziv oblika R# gdje je # prirodan broj
* definirana kao niz naredbi oblika npr. `w2 R1 w3` ili samo `2 R1 3`

### valuacija (beskonačna)
* definirana kao niz naredbi oblika npr. `w2 |- p3` ili `2 |- p3` ili `2 ||- p3`
* alternativno, koristimo agregirani prikaz `w4 |- {p1 p2 p5 p17}` 
* u reverznoj notaciji: `p4 -| {4 2 5 11 0}`

### KripkeovModel (beskonačan)
### konstante (true i false)
* oznake npr. `T` i `F`

### skupFormula (beskonačan)
* bilo koji naziv, ali da je prvo slovo veliko i da nije `T`, `F`, ni `R`

## 6. Operatori

### negacija
* simbol : `~`

### ili
* simbol? : `ili, or, ||`

### box
* simbol : `[]`
* za kreiranje tipa formula;

### diamond 
* simbol : `<>`

### forsira
* simbol? : `||-, |-`
* za definiranje istinitosti neke prop. varijable na svijetu (npr. w ||- P1);
* ? možda želomo analogon tome, odnosno imati operator *valuacija*
  
### valuacija
* simbol? : `-|, -||`
* upotreba : `p4 -| {4 2 5 11 0}` alterantivno `p4 -| {w4 w2 w5 w11 w0}` 
	* značenje : V(P4) = {w4, w2, w5, w11, w0}

### unija
* simbol : U
* za dodavanje instance tipa formula u instancu tipa skupFormula (npr. skupFormula S = f1 U f2 gdje smo ranije definirali formula f1 = nesto1, f2 = nesto2)

### ostatak?
Ostatak može biti korištenje ostalih logičkih veznika i korištenje optimizatora koji ih pretvara u negaciju i ili

## 7. Datoteke
Unos iz datoteke i ispis u datoteku.

## 8. Kkomentari
Jednolinijski.
