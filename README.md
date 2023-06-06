# IP
Projekt iz interpretacije programa (solver/proof-checker za modalnu logiku)

# Sadržaj

## 1. interaktivni način rada
poslije svake naredbe dolazi znak ;

## 2. Aritmetika

## 3. Petlje 
for i while petlja + if

## 4. Funkcije
definicija funkcija i funkcijski pozivi. Primjer funkcija: ... 

## 5. Tipovi podataka
formula (beskonačan), svijet (beskonačan), relacija (beskonačna), valuacija (beskonačna), KripkeovModel (beskonačan), konstante (true i false), skupFormula (beskonačan)

## 6. Operatori

### negacija
* simbol : ~

### ili
* simbol? : ili, or, ||

### box
* simbol : []
* za kreiranje tipa formula;

### diamond 
* simbol : <>

### forsira
* simbol : ||-, |-
* za definiranje istinitosti neke prop. varijable na svijetu (npr. w ||- P1);
* ? možda želomo analogon tome, odnosno imati operator \<naziv\>
  
### \<naziv\>
* simbol : -|, -||
* upotreba : P1 -| w1, w2, ..., wn 
	* značenje : V(P1) = {w1, w2, ..., wn} 

### unija
* simbol : U
* za dodavanje instance tipa formula u instancu tipa skupFormula (npr. skupFormula S = f1 U f2 gdje smo ranije definirali formula f1 = nesto1, f2 = nesto2)

### ostatak?
Ostatak može biti korištenje ostalih logičkih veznika i korištenje optimizatora koji ih pretvara u negaciju i ili

## 7. Datoteke
Unos iz datoteke i ispis u datoteku.

## 8. Kkomentari
Jednolinijski.
