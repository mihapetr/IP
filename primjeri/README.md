# općenito
* editirati u excelu ili nekom srodnom programu radi lakše vizualizacije

# relacije
* datoteka koja sadrži *valuaciju* ima na kordinati 0,0 (nulti redak, nulti stupac) napisano "valuacija"
* prvi stupac i redak su liste svih propozicionalnih varijabli
* relacija se interpretira tablično
    * primjer:
```
# python kod:
# recimo da se u R kao dvodimenzionalnu listu importira relacija.csv

R[0][0] == "relacija" # provjera tipa datoteke
s2 = R[2][0] # neki svijet $2
s4 = R[0][4] # neki svijet $4

if R[2][4] == "R" :
    # s2 R s4
    pass
else :
    # s2 nije u relaciji R s s4
```


# valuacije
* datoteka koja sadrži *valuaciju* ima na kordinati 0,0 (nulti redak, nulti stupac) napisano "valuacija"


# modeli i okviri
* za definiciju *okvira* je dovoljna datoteka s relacijom jer su elementi *nosača* implicitno zadani kroz tablicu
* za definiciju *modela* su potrebna oba tipa datoteke
    * ali moraju biti **kompatibilni**, osnosno lista svijetova u datoteci s valuacijom mora biti identična kao
    u datoteci s relacijom

