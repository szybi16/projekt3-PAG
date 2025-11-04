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
maciek = r"C:/Users/Szybi/Documents/Studia/PAG/projekt1-PAG/Dane/"
julka = r""
filip = r"C:/Studia/Sezon_3/Programowania_aplikacji_geoinformacyjnych/Projekt/Dane/"

# Stałe do wczytywania warstwy
layer = maleDane    # tu wybrany zestaw danych
user = maciek       # tu wasz adres danych

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

##### Funkcje temp #####

# Ta funkcja nie działa, i tak powinna iść do wymiany
def save_to_graph(plik_wyjsciowy, vertex_coords, vertex_edges, edges):

    title = "Vertex_ID X Y Neighbours_IDs\n"

    with open(plik_wyjsciowy, 'w', encoding='utf-8') as file:
        file.write(title)

        for id_w, (x, y) in vertex_coords.items():

            neighbor_ids = set()

            for edge_id in vertex_edges[id_w]:
                edge = edges[edge_id]

                neighbor_id = edge["id_to"]
                if neighbor_id != id_w:
                    neighbor_ids.add(neighbor_id)

            sorted_neighbors = sorted(list(neighbor_ids))
            neighbors_list_str = ' '.join(map(str, sorted_neighbors))
            line = f"{id_w}\t{x}\t{y}\t{neighbors_list_str}\n"
            file.write(line)

########################

#### Kod tymczasowy ####

print(f"Liczba wierzchołków: {len(graph.nodes)}")
print(f"Liczba krawędzi: {len(graph.edges)}")
# print(graph)

NX_visualisation(graph)
# Web_visualisation(graph)

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

########################
