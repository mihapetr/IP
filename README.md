# Sadržaj

Projekt iz kolegija ***Interpretacija programa*** u kojem će biti implementiran softver za praktičan rad s osnovnim objektima Modalne logike (propozicionalne varijable, modalne formule, Kripkeovi modeli, valuacije...). Potpuna prilagođenost softvera sintaksi Modalne logike omogućit će i proučavanje njezine semantike, a samim time i dobivanje osnovnih teorijskih rezultata koji će biti obrazloženi u nastavku, kao sama svrha razvoja ovog softvera. 
Karakteristike softvera:

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

### formula (beskonačan)
* prvi znak naziva: malo slovo abecede

### svijet (beskonačan)
* prvi znak naziva: @ 

### model (beskonačan)
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

### Provjera istinitosti
* simbol: `?`
* pozivanje: formula ? @svijet

### Negacija
* simbol : `~`

### Ili
* simbol? : `|`

### Box
* simbol : `[]`
* za kreiranje tipa formula;

### Diamond 
* simbol : `<>`

### Assigment
* simbol : `=`

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
### Zapisivanje i učitavanje modela

## 8. Komentari
Jednolinijski.

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

## Korištenje modela
```
koristi <ime_modela>;
```
* memorija['using'] = <ime_modela>
## definiranje valuacija, relacija, okvira, modela
* sve se obavlja uz pomoć učitavanja iz datoteke
* proširujemo dolje definiranim operatorima 

## Organizacija tipova podataka u memoriji
* svijet (klasa): skup sljedbenika (ime skupa: sljedbenici) , skup propozicionalnih varijabli (ime skupa: činjenice); test (self, formula)
* model (klasa): skup svjetova (ime skupa: nosač)

