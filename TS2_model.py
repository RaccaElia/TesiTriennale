from mip import *
import random as rnd
from generatoreIstanzeSDST import generaProcess, generaSetup
from time import time

mod = Model("TS2")

#PARAMETRI
n = 30               #numero di job
m = 20               #numero di macchine

p = generaProcess(n, m)             #P[j][r]

s = generaSetup(n, m)               #S[j][i][r]

#VARIABILI

Zij = [[mod.add_var(var_type=mip.BINARY, name=f"Z{i+1}{j+1}") for j in range(n)] for i in range(n)]   #1 se job i sta in posizione j nella sequenza
Wijk = [[[mod.add_var(var_type=mip.BINARY, name=f"W{i+1}{j+1}{k+1}") for k in range(n)] for j in range(n)] for i in range(n)]  #1 se il job i, nella posizione j, seguito da k
Crj = [[mod.add_var(var_type=mip.INTEGER, name=f"C{j+1}{r+1}") for j in range(n)] for r in range(m)] #tempo di completamento del job j
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

#relazione tra job adiacenti sulla stessa macchina
for r in range(m):
    for j in range(n-1):
        mod += Crj[r][j] + xsum(xsum(s[k][i][r]*Wijk[i][j][k] for k in range(n)) for i in range(n)) + xsum(p[i][r]*Zij[i][j+1] for i in range(n)) <= Crj[r][j+1]

#relazione tra completamenti su 2 macchine dello stesso job
for r in range(m-1):
    for j in range(n):
        mod += Crj[r][j] + xsum(p[i][r+1]*Zij[i][j] for i in range(n)) <= Crj[r+1][j]

#vincolo su completamento del primo job
for r in range(m):
    mod += xsum(p[i][r]*Zij[i][0] for i in range(n)) <= Crj[r][0]

#FUNZIONE OBIETTIVO
mod.objective = xsum(Crj[m-1][j] for j in range(n))
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

print(f"La soluzione è stata trovata in {end_time-start_time} secondi")

#print(f"process time: {p}")
#print(f"setup time: {s}")

for j in range(n):
    for i in range(n):
        #print(f"Z{i}{j} = {Zij[i][j].x}")
        if Zij[i][j].x > 0.98:
            print(f"il job {i+1} sta nella posizione {j+1}")
for j in range(n):
        print(f"Completion time job {j+1} = {Crj[m-1][j].x}")
#print(f"Completion time = {Cmax.x}")
print(f"TS2: {mod.objective_value/n}")
print((f"best objective {mod.objective_value}, best bound {mod.objective_bound}, gap {mod.gap*100}% (TS2)\n"))