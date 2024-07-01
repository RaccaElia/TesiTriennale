import copy
import random
from time import time
from generatoreIstanzeSDST import generaProcess, generaSetup


class EuristicaSDST:

    def __init__(self):
        self.n = 40
        self.m = 20
        self.p = generaProcess(self.n, self.m)
        self.s = generaSetup(self.n, self.m)

        self._soluzioneBest = None
        self._costoBest = None
        self._differenze = {}
        self._differenzeTuple = []

    def trovaDifferenze(self):
        for i in range(self.n):
            for k in range(self.n):
                if i == k:
                    pass
                else:
                    dif = 0
                    for r in range(self.m - 1):
                        dif += abs((self.p[k][r]+self.s[k][i][r]) - (self.p[i][r+1]+self.s[k][i][r+1]))
                    self._differenze[(i, k)] = dif

    def primaSoluzione(self):
        difReverse = [(parte[1], parte[0]) for parte in self._differenze.items()]
        sortDifRev = sorted(difReverse)
        self._differenzeTuple = [tupla[1] for tupla in sortDifRev]
        self._soluzioneBest = self.calcolaSequenza(self._differenzeTuple)
        self._costoBest = self.costoSequenza(self.calcolaSequenza(self._differenzeTuple))
        return self._differenzeTuple

    def calcolaSequenza(self, listaTup):
        soluz = []
        for tupla in listaTup:
            if tupla[0] not in soluz and tupla[1] not in soluz:
                soluz.append(tupla[0])
                soluz.append(tupla[1])
            elif tupla[0] in soluz and tupla[1] not in soluz:
                soluz.insert(soluz.index(tupla[0])+2, tupla[1])
            elif tupla[0] not in soluz and tupla[1] in soluz:
                soluz.insert(soluz.index(tupla[1])-2, tupla[0])
            else:
                continue
        return soluz

    def ricorsione(self, parziale, stato, start_time):          #il parziale è una lista di tuple
        if time() - start_time > 60:
            return
        seqP = self.calcolaSequenza(parziale)
        if len(seqP) == self.n and self.isBest(seqP):       #dentro la funzione isBest se il costo è migliore lo salvo già
            print(f"soluzione migliore")
            self._soluzioneBest = copy.deepcopy(seqP)
            if len(parziale) > len(self._differenzeTuple)*0.8:
                self._differenzeTuple = copy.deepcopy(parziale)
        else:
            if stato == self.n or parziale == []:
                return
            #non c'è bisogno del else perchè con il return la funzione ferma l'esecuzione alla riga precedente
            parziale.pop(0)
            for tupla in parziale:
                parziale.append(tupla)
                self.ricorsione(parziale, stato+1, start_time)
                if parziale != []:
                    parziale.pop(0)

    def costoSequenza(self, seq):
        compl = [[0]*self.m]*self.n
        costo = 0
        for i in range(self.n):
            if i == 0:
                compl[i][0] = self.p[seq[i]][0]         #C00
                for r in range(1, self.m):              #C0r
                    compl[i][r] = compl[i][r-1] + self.p[seq[i]][r]
            else:
                compl[i][0] = compl[i-1][0] + self.p[seq[i]][0] + self.s[seq[i]][seq[i-1]][0]           #Cj0
                for r in range(1, self.m):                                                              #Cjr
                    compl[i][r] = max(compl[i][r-1], compl[i-1][r]+self.s[seq[i]][seq[i-1]][r])+self.p[seq[i]][r]

            costo += compl[i][self.m-1]
        return costo/self.n

    def isBest(self, seq):
        costoSeq = self.costoSequenza(seq)
        if costoSeq < self._costoBest:
            self._costoBest = costoSeq      #salvo già qui il costo così non devo ricalcolarlo nella funzione ricorsione
            return True
        else:
            return False

    def esploraSpazio(self, listaTuple):
        random.shuffle(listaTuple)
        lun = len(listaTuple)
        i = 0
        while i <= lun*0.2:
            tupla = listaTuple[random.randint(0, lun-1)]
            nuovaTupla = (tupla[1], tupla[0])
            tupla = nuovaTupla
            i += 1
        return listaTuple

    @property
    def differenze(self):
        return self._differenze

if __name__ == '__main__':

    #CREAZIONE ISTANZA
    eur = EuristicaSDST()
    eur.trovaDifferenze()

    #CALCOLO SOLUZIONE DI PARTENZA
    primaSoluz = eur.primaSoluzione()
    print(eur._soluzioneBest)
    print(eur._costoBest)

    #PRIMA RICERCA LOCALE
    parziale = copy.deepcopy(eur._differenzeTuple)
    start_time = time()
    eur.ricorsione(parziale, 0, start_time)
    print(f"finita prima ricorsione")
    print(f"best: {eur._costoBest}")
    end_time = time()

    #ESPLORAZIONE INTORNI VICINI
    while end_time - start_time < 300:
        parziale = copy.deepcopy(eur.esploraSpazio(eur._differenzeTuple))
        eur.ricorsione(parziale, 0, time())
        end_time = time()
        print(f"fine iterazione: {end_time-start_time} secondi")
        print(f"best: {eur._costoBest}")

    #STAMPA RISULTATO MIGLIORE
    print(eur._soluzioneBest)
    print(f"eur: {eur._costoBest}")
    print(f"tempo: {end_time - start_time}")
