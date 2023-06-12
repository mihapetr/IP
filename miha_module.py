# interaktinvi rad je implementiran izvan okvira programskog jezika
# šalje parseru blokove koda iza kojih se unese "\n\n"

def main() :

    # ispis uputa
    print(10 * "-" + " MODALNA LOGIKA " + 10 * "-")
    print("Naredbe završavaju znakom ';'.")
    print("Za izvršavanje unesenog bloka dvaput pritisnite Enter.")
    print("Unesite 'bye' ili 'exit' za kraj rada.")
    print("'napravi <ime_datoteke>.mir' izvršava skriptu u toj datoteci.")
    print(60 * "-")

    block = ""
    while True :
        print(">", end =" ") # ispisuje oznaku da smo unutar naše ljuske bez prelaska u novi red
        line = ""
        line = input() # čeka input korisnika

        # IZLAZ IZ PROGRAMA
        if line in {"bye", "exit"} :    # kraj rada
            exit()

        # NAPRAVI SKRIPTU
        elif line[:7] == "napravi":
            block = ""  # resetira do sad uneseno
            s = line.split(' ')
            script = s[1] # drugi element je naziv datoteke

            if not script[-4:] == ".mir" : 
                print("Tip datoteke mora biti .mir!")
                continue

            if not len(s) == 2 :
                print("Previše argumenata! Koristiti: napravi <ime_datoteke>.mir")
                continue

            # print("izvršavam skriptu " + script)
            try : f = open(script, "r")
            except : print("Greška prilikom otvaranja datoteke. Postoji li?")
            else :
                # uspješno otvaranje
                P(f.read()).izvrši() 
                #print("datoteka: " + f.read())
                f.close()
        
        # DVOSTRUKI ENTER
        elif line == "" and not block == "" :  # block sadrži odsječak koda
            #print("blok koda:")   
            #print(block)
            P(block).izvrši() # izvršavamo kod 
            block = ""       # reset

        # KONKATENACIJA NOVE LINIJE U TRENUTNI BLOK KODA
        elif not line == "" :  # linija koda unesena
            block += line + "\n"

        # NEBTINI PRELASCI U NOVI RED
        elif line == "" :
            pass    # ignoriramo bezvezno unošenje novih redova

        # CATCHALL DEBUG
        else :
            print("nepokriven slučaj!") # za debug; ne bi trebalo doći do toga
