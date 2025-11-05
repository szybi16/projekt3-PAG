# -*- coding: utf-8 -*-
'''
    Plik główny istnieje po to żeby:

    1. uruchamiać funkcje;
    2. przechowywać stałe ustawiane z kodu;
    3. łatwo testować nowe funkcje/biblioteki/rozwiązania.

    Z tego powodu należy utrzymać ten plik stosunkowo krótki i prosty, a także ograniczać ilość tymczasowego kodu i funkcji przed commitem.

        ~ Maciek <3 
'''

#### Stałe w kodzie ####

# Zestawy danych
duzeDane = "Drogi_Bydgoszcz"
maleDane = "Drogi_Bydgoszcz_Male"
testKierunek = "maleKierunek"

# Personalne adresy plików (trzeba to jakoś lepiej rozwiązać)
maciek_home = r"C:/Users/Szybi/Documents/Studia/PAG/projekt1-PAG/Dane/"
maciek_stud = r"C:/Users/Maciek/Documents/Studia/PAG/projekt1-PAG/Dane/"
julka = r""
filip = r"C:/Studia/Sezon_3/Programowania_aplikacji_geoinformacyjnych/Projekt/Dane/"

# Stałe do wczytywania warstwy
layer = maleDane    # tu wybrany zestaw danych
user = maciek_stud       # tu wasz adres danych

shp = user + layer + ".shp" # tak powstaje adres pliku .shp, to nie stała, ale zostawiam tutaj, bo jest używane w tym samym miejscu co layer

# Tolerancja dociągania do wierzchołków
tolerance = 0.5

########################

import time

from Graph import *
from View import *
from algorytmy import *

###### Kod główny ######

graph = create_graph(shp, layer, tolerance)

########################

#### Kod tymczasowy ####

print(f"Liczba wierzchołków: {len(graph.nodes)}")
print(f"Liczba krawędzi: {len(graph.edges)}")
# print(graph)

NX_visualisation(graph)
# Web_visualisation(graph, path)

########################

# Wierzchołki początku i końca
start = graph.nodes[73]
end = graph.nodes[120]

#### Test Dijkstry ####

# t_start_dijkstra = time.time()
# path, distance = dijkstra(start, end)
# t_end_dijkstra = time.time()
# dijk_time = t_end_dijkstra - t_start_dijkstra
# print("\nDijkstra")
# print("Najkrotsza trasa od", start.id, "do", end.id, ":")
# print("sciezka:", [n.id for n in path])
# print("Dlugosc trasy:", distance, "metrow")
# print(f"Czas działania algorytmu: {dijk_time:.15f} sekundy\n")

########################

####### Test A* ########

t_start_gwiazdka = time.time()
path, distance = aGwiazdka(start, end)
t_end_gwiazdka = time.time()
gw_time = t_end_gwiazdka - t_start_gwiazdka
print("\nA*")
print("Najkrotsza trasa od", start.id, "do", end.id, ":")
print("sciezka:", [n.id for n in path])
print("Dlugosc trasy:", distance, "metrow")
print(f"Czas działania algorytmu: {gw_time:.15f} sekundy\n")

####### Zapis ##########

save_to_graph("grafek.txt", graph)
