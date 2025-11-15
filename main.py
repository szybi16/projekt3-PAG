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
julka = r"C:/GI sem 5/PAG_GITHUB_REZPOYTORIUM/projekt1-PAG/Dane/"
filip = r"C:/Studia/Sezon_3/Programowania_aplikacji_geoinformacyjnych/Projekt/Dane/"

# Stałe do wczytywania warstwy
layer = duzeDane    # tu wybrany zestaw danych
user = filip     # tu wasz adres danych

shp = user + layer + ".shp" # tak powstaje adres pliku .shp, to nie stała, ale zostawiam tutaj, bo jest używane w tym samym miejscu co layer

# Tolerancja dociągania do wierzchołków
tolerance = 0.5

########################

import time
import threading
import webbrowser
from Graph import *
from View import *
from algorytmy import *
from Pegasus import *

#Zmienne globalne dla serwera, jak ktoś chce inny port to można sobie to zmienić ale raczej na 5000 nic innego z niego nie korzysta
PORT = 5000
HOST = "localhost"
URL = f"http://{HOST}:{PORT}"

###### Kod główny ######

graph = create_graph(shp, layer, tolerance)

########################

#### Kod tymczasowy ####

#print(f"Liczba wierzchołków: {len(graph.nodes)}")
#print(f"Liczba krawędzi: {len(graph.edges)}")
# print(graph)

########################
"""
# Wierzchołki początku i końca
start = graph.nodes[73]
end = graph.nodes[120]

#### Test Dijkstry ####

 t_start_dijkstra = time.time()
 path, distance = dijkstra(start, end)
 t_end_dijkstra = time.time()
 dijk_time = t_end_dijkstra - t_start_dijkstra 
 print("\nDijkstra")
 print("Najkrotsza trasa od", start.id, "do", end.id, ":")
 print("sciezka:", [n.id for n in path])
 print("Dlugosc trasy:", distance, "metrow")
 print(f"Czas działania algorytmu: {dijk_time:.15f} sekundy\n")

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
"""
####### Zapis ##########

save_to_graph("grafek.txt", graph)

###### Wyświetlania ####

#Otwieramy przeglądarę i dajemy jej czas aby server zdążył się odpalić
def open_browser():
    time.sleep(1)
    webbrowser.open(URL)

if __name__ == '__main__':
    #utworzenie wątku, który pozwala na to, że app i open_browser działa w tym samym momencie inaczej albo by się otwierało
    #przed włączeniem serwera albo nie uruchomiło by się wcale bo zaczęło by działać app, dopóki się go nie zatrzyma
    threading.Thread(target=open_browser).start()
    #Dodajemy nasz graf dla aplikacji Flaskowegj
    app.config['GRAPH'] = graph
    #Uruchomienie serwera, debug=False pozwala na brak restartu gdy sobie 'grzebiemy' w kodzie
    app.run(host=HOST, port=PORT, debug=False)

#nx_visualisation(graph)
# web_visualisation(graph, path)