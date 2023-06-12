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
* podržani aritmetički operatori: `+, -, *, ^`
* tipovi: `int` (cijeli brojevi), `nat` (prirodni brojevi, uključujući i 0)
* početni znak: `#`

## 3. Petlje 
* `if, else` : svaki oblik podržan
* petlje: `for`, 'while' (#todo)

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
* početak: `\\`

## 9. Dodatno (1)
* provjere istinitosti formule na određenom modelu i svijetu unutar njega (tzv. istinitost na točkovnom modelu) 
* simbol: **??**
* način korištenja: **???**

------------------------------------------------------------------------------------------------------------------------------------------------------------------
U nastavku izlažemo nekoliko naprednih mogućnosti (ispitivanje svojstava gradivnih cjelina Modalne logike - istinitost i valjanost formule, proof-checker, karakteristike relacije dostiživosti) softvera dobivenih uz pomoć gore opisanih funkcionalnosti. 

### 1. Istinitost formule na (konačnom) modelu
* **algoritam**: koristiti mogućnost provjere istinitosti na točkovnom modelu za svaki svijet unutar konkretnog modela za kojeg se ispituje istinitost formule

### 2. Valjanost formule na (konačnim) modelima
* **algoritam**: iterativno ili glavni test (istražiti)

### 3. Karakteristike relacije dostiživosti
* *specifična formula* : modalna formula čija valjanost na okviru ovisi o karakteristikama relacije dostiživosti
* **algoritam**: ispitivanje valjanosti *specifične formule* 

### 4. Proof-checker
* provjera sheme aksioma za formulu: usporedba AST-ova koji predstavljaju formule
* modus ponens:
	* provjera svih mogućih parova iznad dotične formule zadovoljavaju li m.p.
		* prolazak kroz sve formule i provjera je li kondicional i je li desno dijete izvedena formula
	* **na najnižoj razini su samo KONDICIONAL i NEGACIJA**	
	* uzima se u obzir da optimizator pretvara svaku formulu u ekvivalentnu s gornjim veznicima
* **algoritam**: ispravnost dokaza provjeravamo donjim redoslijedom
	1. A1 : A -> (B -> A)
	2. A3: (~B -> ~A) -> (A -> B)
	3. K: [](A -> B) -> ([]A -> []B)
	4. A2: (A -> (B -> C)) -> ((A -> B) -> (A -> C))
	5. Nužnost
	6. Modus ponens 

## NAPOMENE
* Istinitost i valjanost se provode nad konačnim modelima, ali to svejedno ne dovodi do gubljenja općenitosti u pogledu definiranja modela jer Modalna logika ima *finite model property*, odnosno svojstvo konačnosti modela
* Ovdje još objasniti zašto možemo u dokazima koristiti samo sheme aksioma RS umjesto tautologija u modalnom jeziku
	
	


------------------------------------------------------------------------------------------------------------------------------------------------------------------
Ovaj dio će nakon završetka projekta bit obrisan (eventualno možemo ostaviti dijelove u kojima objašnjavamo kako je što ostvareno u memoriji te objašnjenje kako korištenje modela funkcionira)
# Organizacija
* *main.py* je glavni source code u kojem će biti aplikacija
* svatko ima svoj modul na kojem radi

## 1.) Korištenje modela
```
koristi <ime_modela> { @w1, @w2, ..., @wn };
```
* memorija['using'] = <ime_modela>
## 2.) Definiranje valuacija, relacija, okvira, modela
* sve se obavlja uz pomoć učitavanja iz datoteke
* proširujemo dolje definiranim operatorima 

## 3.) Organizacija tipova podataka u memoriji
* svijet (klasa): skup sljedbenika (ime skupa: sljedbenici) , skup propozicionalnih varijabli (ime skupa: činjenice); test (self, formula)
* model (klasa): skup svjetova (ime skupa: nosač)

### Ostatak (ovdje idu usvojeni prijedlozi)
* optimizator: pretvara korisnikove formule u njima ekvivalentne koje koriste operatore `[], ->, ~`

### Prijedlozi
* mogli bismo napraviti "operator" castanja tipa propozicionalna varijabla u tip formula (slično je napravljeno u onom primjeru BASIC.py gdje Čačić objašnjava)
* optimizator za aritmeticke izraze (ovo je mozda nepotrebno, samo riskiramo neku pogresku, a nije da nam se program na njima bazira)
* while petlja -> vjerojatno onda AST Petlja preimenovat u FOR i onda zaseban AST za while imena WHILE
* omogucit vise logickih uvjeta u if-u
* omogucit ispisivanje korisničkog stringa, npr. ispiši << "Sve je dobro prošlo!";

### Problemi
* ~~**Problem (1)**~~ : uveden je token 'formula', odnosno novi tip podatka. Deklaracija je ok, nece bit nikakvih problema, no problem je pridruzivanje s pravilom pridruživanje -> IME JEDNAKO izraz. Nakon uvodjenja tipa formule, ono se treba updateati u pridruživanje -> IME JEDNAKO (izraz | formula), ali hoćemo li u parseru pozvati p.izraz() ili p.formula() ovisi o tome kakvog je tipa IME pa taj problem moramo riješiti (dakle moše se dogoditi nešto poput: formula f = (P0->P1); int a = 3; f = -1; a = f;)
	* prijedlog za rješavanje: napraviti funkciju koja vraća tip od IME (T.INT, T.NAT, T.FORMULA...) i u ovisnosti o tome jesu li kompatibilni tipovi s lijeve i desne strane izvršit pridruživanje. Teoretski bi se to dalo zaključiti iz sadržaja, no opet ako imamo: int a = 3; te onda nekad kasnije a = 5, kako iz sadržaja od 'a' znati je li to int ili nat jer može biti oboje
	* <u>**RIJEŠENO**</u>: iz T.IME možemo razlikovati tip jer formule počinju malim slovom, modeli velikim pa sam stavio da imena varijabli tipa `int, nat` moraju započinjati znakom `#`. Nemogućnost kontrole kompatibilnosti u pridruživanju je riješen tako da se u memoriji za svaki token (koji predstavlja ime varijable) osim njegove vrijednosti pamti i njegov tip (uređeni par koji je zapravo lista s dva elementa: prvi je vrijednost, a drugi tip)

------------------------------------------------------------------------------------------------------------------------------------------------------------------
## roberto.py
* modalne formule, lijepo ispisivanje, optimizator *optim1* koji formulu pretvara u njoj ekvivalentnu koja sadrži samo kondicional i negaciju. Također, implementiran je i optimizator *optim* koji briše redundantne negacije (bilo bi dobro testirati radi li sve ispravno) (8.6.2023.)
* funkcija jednaki(f1, f2) koja prima dva AST-a (formule) i uspoređuje ih. Vraća True ako su jednaki, a False ako nisu (9.6.2023.)
* funkcionalnost: for petlja, if + else naredba, deklaracije varijabli (trenutni tip = int), praćenje je li varijabla deklarirana, javljanje greške ako se varijabla redeklarira ili joj se pridružuje varijabla koja nije do tad deklarirana ili pridružujemo vrijednost varijabli koju do tad nismo deklarirali (osim u for-u), continue, break, aritmetički izrazi (operacije: +, * i ^), ispisivanje varijabli (ispiši<<varijabla|aritmetički izraz), pridruživanje aritmetičkog izraza već deklariranoj aritmetičkoj varijabli (9.6.2023.)
* dodana funkcija za proof-checker: shemaA1 (nju ce kao korisnik upisati pri svom radu, nece biti u jeziku, ali neka stoji), dodan novi tip 'nat' (prirodni brojevi uključujući i 0), dodana kontrola kompatibilnosti tipova (int i nat) za DEKLARACIJU (10.6.2023.)
* riješen Problem (1), promijenjeno ime AST-a "Petlja" u "For_Petlja" i ime metode parsera .petlja() u .for_petlja() (11.6.2023.)
* uveden novi tip varijable `formula` te su riješene sve moguće nekompatibilnosti koje mogu nastati prilikom deklaracije, pridruživanja i unutar uvjeta for petlje između tipova `int`, `nat` i `formula`. Također, dodana je mogućnost ispisa formule te novi uvjet unutar if-a (if (f == g) ... gdje f i g predstavljaju varijable tipa formula). Pripremljen je dio gramatike koji zahtjeva nove metode parsera i AST-ove, a sve to se jednostavno ubacuje jer je neovisno o svemu dosad napravljenom (12.6.2023.)

## kosijenac.py
* svjetovi, relacija doztizivosti, valuacija, model
* model naziva `M` sa svjetovima @svijet1, @svijet2, @svijet3 i prop. varijablama $pada_kisa, $ulice_su_mokre i $prolazi_cisterna deklarira se kao `koristi M { @svijet1, @svijet2, @svijet3; $pada_kisa, $ulice_su_mokre, $prolazi_cisterna }`
* AST `Provjera` koji nastaje iz naredbe oblika `formula ? @svijet` i testira istinitost formule na svijetu
* Implementirani simboli `|=`, `=|`, `|~` i `~|` kao AST-ovi `Forsira`, `Vrijedi`, `Neforsira` i `Nevrijedi`, redom.
* Impl. aliasi za simbole `||-`, `-||`, `||~` i `~||`, redom
* Unos iz datoteke se obavlja kao `M << "relacijska_dat.mir" << 'val_datoteka.mir'` (obvezna je uporaba navodnika oko naziva datoteke, mogu biti jednostruki ili dvostruki ali se moraju poklapati)
* U relacijskoj datoteci mora prvo pisati "rel" (bitno je da su to prva 3 slova, smije pisati i npr. "relacija"), analogno za valuacijsku datoteku gdje mora pisati "val".
* U valuacijskoj su datoteci svijetovi u stupcu slijeva a prop. varijable u prvom retku, dok su u relacijskoj svjetovi s "lijeve" strane relacije u stupcu slijeva. Oznaka za istinitost relacije odnosno forsiranja smije biti u raznim oblicima: bilo koji string kojem je prvi znak 'T', '1', 'Y', 'I', 'D' ili 'O' se interpretira kao istina, a za 'F', '0', 'N', 'L', 'N' i 'X' je neistina (znakovi ne ovise o velikim i malim slovima).
* TODO: testirati klasu `Provjera`
