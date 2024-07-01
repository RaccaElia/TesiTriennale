from mip import *
import random as rnd
from generatoreIstanzeSDST import generaProcess, generaSetup
from time import time

mod = Model("TS1")

#PARAMETRI
n = 40               #numero di job
m = 20               #numero di macchine

p = generaProcess(n, m)             #P[j][r]

s = generaSetup(n, m)               #S[j][i][r]

#VARIABILI

Zij = [[mod.add_var(var_type=mip.BINARY, name=f"Z{i+1}{j+1}") for j in range(n)] for i in range(n)]   #1 se job i sta in posizione j nella sequenza
Wijk = [[[mod.add_var(var_type=mip.BINARY, name=f"W{i+1}{j+1}{k+1}") for k in range(n)] for j in range(n)] for i in range(n)]  #1 se il job i, nella posizione j, seguito da k
Xrj = [[mod.add_var(var_type=mip.CONTINUOUS, name=f"X{r+1}{j+1}") for j in range(n)] for r in range(m)]  #tempo di attesa della macchina r prima che il job in sequenza j venga processato
Yrj = [[mod.add_var(var_type=mip.CONTINUOUS, name=f"Y{r+1}{j+1}") for j in range(n)] for r in range(m)]  #tempo di attesa del job in posizione j prima di finire sulla macchina r
Cj = [mod.add_var(var_type=mip.CONTINUOUS, name=f"C{j+1}") for j in range(n)]  #tempo di completamento del job j
#Cmax = mod.add_var(var_type=INTEGER, name="Cmax")

#VINCOLI

#in posizione j c'è solo un job
for i in range(n):
    mod += xsum(Zij[i][j] for j in range(n)) == 1       

#il job i copre una sola posizione j
for j in range(n):
    mod += xsum(Zij[i][j] for i in range(n)) == 1       

#ogni job ha un solo successore
for i in range(n):
    for j in range(n):
        mod += xsum(Wijk[i][j][k] for k in range(n)) == Zij[i][j]       

#ogni job ha un solo predecessore
for i in range(n):
    for j in range(1,n):
        mod += xsum(Wijk[k][j-1][i] for k in range(n)) == Zij[i][j]     

#il predecessore del primo job è l'ultimo
for i in range(n):
    mod += xsum(Wijk[k][n-1][i] for k in range(n)) == Zij[i][0]           

#vincolo della relazione che lega job e macchine adiacenti
for r in range(m-1):
    for j in range(n-1):
        mod += xsum(xsum((s[k][i][r] - s[k][i][r+1])*Wijk[i][j][k] for k in range(n)) for i in range(n)) + (xsum(p[i][r]*Zij[i][j+1] for i in range(n)) - xsum(p[i][r+1]*Zij[i][j] for i in range(n))) + (Xrj[r][j+1] - Xrj[r+1][j+1]) + (Yrj[r][j+1] - Yrj[r][j]) == 0

#vincolo sull'idle time della macchina r prima del processamento del primo job
for r in range(m-1):
    mod += xsum(p[i][r]*Zij[i][0] for i in range(n)) + Xrj[r][0] + Yrj[r][0] == Xrj[r+1][0]

#vincolo sul completamento dei job
for j in range(n):
    mod += xsum(xsum(p[i][m-1]*Zij[i][q] for i in range(n)) for q in range(j+1)) + xsum(xsum(xsum(s[k][i][m-1]*Wijk[i][q-1][k] for k in range(n)) for i in range(n)) for q in range(1, j+1)) + xsum(Xrj[m-1][q] for q in range(j+1)) == Cj[j]

#vincolo sul makespan
#mod += xsum(p[i][m-1] for i in range(n)) + xsum(xsum(xsum(s[k][i][m-1]*Wijk[i][q-1][k] for k in range(n)) for i in range(n)) for q in range(1, n)) + xsum(Xrj[m-1][q] for q in range(n)) == Cmax

#FUNZIONE OBIETTIVO
mod.objective = xsum(Cj[j] for j in range(n))
#mod.objective = minimize(Cmax)

start_time = time()
status = mod.optimize(max_seconds=300)
end_time = time()

#RISULTATI
if status == OptimizationStatus.OPTIMAL:
    print(f'optimal solution cost {mod.objective_value} found')
elif status == OptimizationStatus.FEASIBLE:
    print(f'solution cost {mod.objective_value} found, best possible: {mod.objective_bound}')
elif status == OptimizationStatus.NO_SOLUTION_FOUND:
    print(f'no feasible solution found, lower bound is: {mod.objective_bound}')

print("p = [", end="")
for i in range(n):
    if i == n-1:
        print(f"{p[i]}]")
    else:
        print(f"{p[i]}, ", end="")
#print(f"process time: {p}")

print("s = [", end="")
for i in range(n):
    if i == n-1:
        print(f"{s[i]}]")
    else:
        print(f"{s[i]},")
#print(f"setup time: {s}")

print(f"La soluzione è stata trovata in {end_time-start_time} secondi da TS1")

print("La soluzione è: ", end="")
for j in range(n):
    for i in range(n):
        if Zij[i][j].x > 0.98:
            if j == n-1:
                print(i+1)
            else:
                print(f"{i+1} - ", end="")
            #print(f"il job {i+1} sta nella posizione {j+1}")
#for j in range(n):
    #for r in range(m):
        #print(f"tempo di attesa della macchina {r+1} prima che il job {j+1} venga processato: {Xrj[r][j].x}")
#for j in range(n):
    #print(f"Completion time del job in posizione {j+1} = {Cj[j].x}")
print(f"Mean flow time = {mod.objective_value/n}")
print((f"best objective {mod.objective_value}, best bound {mod.objective_bound}, gap {mod.gap*100}%\n"))

#STAMPA SU FILE

fileIstanze = open("PerformanceEuristica.txt", "a")
fileIstanze.write("p = [")
for i in range(n):
    if i == n-1:
        fileIstanze.write(f"{p[i]}]\n")
    else:
        fileIstanze.write(f"{p[i]}, ")
fileIstanze.write("s = [")
for i in range(n):
    if i == n-1:
        fileIstanze.write(f"{s[i]}]\n")
    else:
        fileIstanze.write(f"{s[i]},\n")
fileIstanze.write("soluzione: ")
for j in range(n):
    for i in range(n):
        if Zij[i][j].x > 0.98:
            if j == n-1:
                fileIstanze.write(f"{i+1}\n")
            else:
                fileIstanze.write(f"{i+1}-")
fileIstanze.write(f"TS1: {mod.objective_value/n}")
fileIstanze.write(f"best objective {mod.objective_value}, best bound {mod.objective_bound}\n")
fileIstanze.write(f"tempo: {end_time-start_time} secondi (TS1)\n")
fileIstanze.close()