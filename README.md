# IP
Projekt iz interpretacije programa (solver/proof-checker za modalnu logiku)

## Osnovno: istinitost formule na modelu
* nužno: unutar jezika implementirati mogućnost provjere istinitosti formule na određenom modelu i svijetu unutar njega

## Valjanost formule na konačnim modelima
* iterativno?
* istražiti glavni test za konačne modele

## Svojstva relacije
* nužno: valjanost formule na konačnim modelima

## Provjera dokaza
* provjera sheme aksioma za formulu
	* u AST-ovima usporedba stabala

* modus ponens
	* provjera svih mogućih parova iznad dotične formule zadovoljavaju li m.p.
		* prolazak kroz sve formule i provjera je li kondicional i je li desno dijete izvedena formula
	* **na najnižoj razini su samo KONDICIONAL i NEGACIJA**	
	* optimizator pretvara svaku formulu u ekvivalentnu s gornjim veznicima
* redosljed provjere (algoritam) :
	1. A1 : A -> (B -> A)
	2. A3: (~B -> ~A) -> (A -> B)
	3. K: [](A -> B) -> ([]A -> []B)
	4. A2: ...
	5. Nužnost
	6. Modus ponens 
* potrebne funkcije za ostvarenje gornjeg algoritma: usporedi(AST f1, AST f2) {usporedi jesu li dvije formule jednake}, razdvoji(AST f) {korijen stabla}

# Organizacija

* *main.py* je glavni source code u kojem će biti aplikacija
* svatko ima svoj modul na kojem radi

# Problemi

## vezanost *forsiranja* i *modela*
* operatori `|-` i `-|` podrazumijevaju neki *model* za koji se definira valuacija
* moramo nekako naznačiti o kojem *modelu* se radi kod korištenja tih operatora
* jedna opcija je na globalnoj razini koristiti neku naredbu kao npr. 
```
use_model <ime_modela>;
// nakon ove linije se sve naredbe koje zahtjevaju <ime_modela> odnose na taj model
```
* analogno za okvire
```
use_frame <ime_okvira>;
// sve dalje se odnosi na taj okvir
``` 

## definiranje valuacija, relacija, okvira, modela
* sve se obavlja uz pomoć učitavanja iz datoteke
* proširujemo 

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
* prvi znak naziva: $
* naziv oblika `p#` gdje je # neki prirodan broj
* ------------ PRIJEDLOG -----------------
* naziv oblika `( _<riječ> )+ `
	* npr. `_pada_kisa` 
	* kako bismo mogli semantički razmišljati o njima
	* radi se o proširenju jer i dalje imamo mogućnost `_p#`

### formula (beskonačan)
* prvi znak naziva: malo slovo abecede
* bilo koji naziv, ali da je prvo slovo malo i da nije `p` ili `w`
* definicija kao npr. `primjerFormule = p0 -> !(<>p1 -> p2)`
* ------------ PRIJEDLOG ---------------------------
* ako prop. var. počinju s `_`, a svijetovi s `$`, formule mogu imati proizvoljan početak (alfanumerički)
* omogućiti definiranje formula pomoću drugih formula (iz rekurzivne definicije formule)
	* npr. `novaFormula = f1 <veznik> f2`

### svijet (beskonačan)
* prvi znak naziva: @
* naziv oblika `w#` gdje je # neki prirodan broj
* ili da naziv bude samo prirodan broj?
* ------------ PRIJEDLOG ----------------
* naziv oblika `$<riječ> (_<riječ>)+`
	* npr. `$oblacni_svijet`
	* i sada je  jako intuitivno razmišljati o izrazu `$oblacni_svijet |- {_pada_kisa _nema_sunca}` 

### Model (beskonačan)
* Prvi znak naziva: veliko slovo abecede

### konstante (true i false)
* oznake npr. `T` i `F`

## 6. Operatori

### Proširivanje valuacije
#### proširivanje skupa istinitih propozicionalnih varijabli na svijetu
##### svijet je s lijeve strane simbola, a s desne prop. varijabla
* simbol: `|=`
* značenje: w1 |= P10 gdje je P10 prop. varijabla koja prije toga "nije bila" u domeni valuacije  
* dualni simbol: `|~` gdje npr. w1 |~ P10 
##### prop. varijabla s lijeve strane simbola, a s desne svijet
* simbol: `=|`
* značenje: P10 =| w1 gdje je P10 prop. varijabla koja prije toga "nije bila" u domeni valuacije  
* dualni simbol: `~|` gdje npr. P10 ~| w1 


### Negacija
* simbol : `~`

### Ili
* simbol? : `|`

### Box
* simbol : `[]`
* za kreiranje tipa formula;

### Diamond 
* simbol : `<>`

### Forsira i valuacija
* za definiranje istinitosti neke prop. varijable na svijetu: vidi *Proširivanje valuacije*

### Ostatak
* optimizator: pretvara korisnikove formule u njima ekvivalentne koje koriste operatore `[], ->, ~`

## 7. Datoteke
Unos iz datoteke i ispis u datoteku.
* bilo bi korisno imati podršku učitavanja modela (nosača, relacija, valuacija) iz datoteka
* primjeri su dani u direktoriju *primjeri*
* datoteka koja sadrži *valuaciju* ima na kordinati 0,0 (nulti redak, nulti stupac) napisano "valuacija"; analogno za *relaciju*
* za definiciju *okvira* je dovoljna datoteka s relacijom jer su elementi *nosača* implicitno zadani kroz tablicu
* za definiciju *modela* su potrebna oba tipa datoteke
* **preporučeno je editirati datoteke u excelu**
* detalji u direktoriju *primjeri*
### Učitavanje dokaza
* pogledati Provjera dokaza

## 8. Komentari
Jednolinijski.
