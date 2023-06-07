# Sadržaj

Projekt iz kolegija ***Interpretacija programa*** u kojem će biti implementiran softver za praktičan rad s osnovnim objektima Modalne logike (propozicionalne varijable, modalne formule, Kripkeovi modeli, valuacije...). Potpuna prilagođenost softvera sintaksi Modalne logike omogućit će i proučavanje njezine semantike, a samim time i dobivanje osnovnih teorijskih rezultata što je i sama svrha razvoja ovog softvera. Ipak, prvo je potrebno promotriti njegove karakteristike i mogućnosti.

## 1. Interaktivni način rada
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
* if + else; petlje: while, for; if, while, for sadržavaju uvjet i tijelo koje se nalazi unutar vitičastih zagrada

## 4. Funkcije
* definicija funkcija i funkcijski pozivi. Primjeri funkcija bit će sami algoritmi čiji će izlaz biti važni teorijski rezultati

## 5. Tipovi podataka
### a) propozicionalna varijabla 
* prvi znak naziva: $
* podtip tipa *formula*

### b) formula 
* prvi znak naziva: malo slovo abecede

### c) svijet 
* prvi znak naziva: @ 

### d) model 
* Prvi znak naziva: veliko slovo abecede

### e) konstante (true i false)
* oznake: `T` i `F`

## 6. Operatori

### a) proširivanje valuacije
#### proširivanje skupa istinitih propozicionalnih varijabli na svijetu
* napomena: svijet je s lijeve strane simbola, a s desne prop. varijabla
* simbol: `|=`
* značenje: w1 |= P10 gdje je P10 prop. varijabla koja prije toga "nije bila" u domeni valuacije  
* dualni simbol: `|~` gdje npr. w1 |~ P10 
Alternativno:
* napomena: prop. varijabla je s lijeve strane simbola, a s desne svijet
* simbol: `=|`
* značenje: P10 =| w1 gdje je P10 prop. varijabla koja prije toga "nije bila" u domeni valuacije  
* dualni simbol: `~|` gdje npr. P10 ~| w1 

### b) provjera istinitosti
* simbol: `?`
* pozivanje: formula ? @svijet

### c) negacija
* simbol : `~`

### d) ili
* simbol : `|`

### e) box
* simbol : `[]`

### f) diamond 
* simbol : `<>`

### g) assignment
* simbol : `=`

## 7. Datoteke
* unos iz datoteke i ispis u datoteku
* učitavanje dokaza
* podrška učitavanja modela (nosača, relacija, valuacija) i spremanje u datoteku
* za definiciju *modela* potrebna su dva tipa datoteke: u jednom je zapisana valuacija, a u drugom relacija
* **preporučeno je editirati datoteke za definiranje modela u excelu**

## 8. Komentari
* jednolinijski
------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Uredi ovo ispod

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

### Ostatak
* optimizator: pretvara korisnikove formule u njima ekvivalentne koje koriste operatore `[], ->, ~`


