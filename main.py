# -*- coding: utf-8 -*-
'''
    Plik główny istnieje po to żeby:

    1. uruchamiać funkcje;
    2. przechowywać stałe ustawiane z kodu;
    3. łatwo testować nowe funkcje/biblioteki/rozwiązania.

    Z tego powodu należy utrzymać ten plik stosunkowo krótki i prosty, a także ograniczać ilość tymczasowego kodu i funkcji przed commitem.

        ~ Maciek <3 
'''

import time
import threading
import webbrowser
import argparse
import os
from Graph import *
from View import *
from algorytmy import *
from Pegasus import *

# Zestawy danych
maleDane = "Drogi_Bydgoszcz_Male"
testKierunek = "maleKierunek"
duzeDane = "Drogi_Bydgoszcz"

# Domyślna warstwa
default_layer = duzeDane

def get_args():
    parser = argparse.ArgumentParser(
        description="Opcjonalna konfiguracja argumentów"
    )

    parser.add_argument(
        "--layer",
        type=str,
        default=default_layer,
        help=f"Nazwa warstwy danych (domyślnie: {default_layer})"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port localhost (domyślnie: 5000)"
    )

    parser.add_argument(
        "--user-path",
        type=str,
        default=None,
        help="Ścieżka do danych (domyślnie: folder \"Dane\" w katalogu programu)"
    )

    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.5,
        help=f"Tolerancja eliminacji niespójności (domyślnie: 0.5)"
    )

    return parser.parse_args()

def build_config():
    args = get_args()
    user_path = args.user_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "Dane") 
    HOST = "localhost" 
    shp = os.path.join(user_path, f"{args.layer}.shp")
    url = f"http://{HOST}:{args.port}"

    return {
        "layer": args.layer,
        "host": HOST,
        "port": args.port,
        "shp": shp,
        "url": url,
        "tolerance": args.tolerance 
    }

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

###### Kod główny ######

#Otwieramy przeglądarę i dajemy jej czas aby server zdążył się odpalić
def open_browser(URL: str):
    time.sleep(1)
    webbrowser.open(URL)

if __name__ == '__main__':
    # konfiguracja
    config = build_config()
    # tworzenie grafu
    layer = config["layer"]
    HOST = config["host"]
    PORT = config["port"]
    shp = config["shp"]
    URL = config["url"]
    tolerance = config["tolerance"]

    # tworzenie grafu
    graph = create_graph(shp, layer, tolerance)
    
    # Zapis
    # save_to_graph("grafek.txt", graph)
    
    #utworzenie wątku, który pozwala na to, że app i open_browser działa w tym samym momencie inaczej albo by się otwierało
    #przed włączeniem serwera albo nie uruchomiło by się wcale bo zaczęło by działać app, dopóki się go nie zatrzyma
    threading.Thread(target=open_browser, args=(URL,)).start()
    
    #Dodajemy nasz graf dla aplikacji Flaskowegj
    app.config['GRAPH'] = graph
    
    #Uruchomienie serwera, debug=False pozwala na brak restartu gdy sobie 'grzebiemy' w kodzie
    app.run(host=HOST, port=PORT, debug=False)

#nx_visualisation(graph)
# web_visualisation(graph, path)
