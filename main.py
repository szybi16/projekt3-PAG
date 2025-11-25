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
danePredkosc = "Drogi_Predkosc"

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
    
    #utworzenie wątku, który pozwala na to, że app i open_browser działa w tym samym momencie inaczej, albo by się otwierało
    #przed włączeniem serwera albo nie uruchomiło by się wcale bo zaczęło by działać app, dopóki się go nie zatrzyma
    threading.Thread(target=open_browser, args=(URL,)).start()
    
    #Dodajemy nasz graf dla aplikacji Flaskowej
    app.config['GRAPH'] = graph
    
    #Uruchomienie serwera, debug=False pozwala na brak restartu gdy sobie 'grzebiemy' w kodzie
    app.run(host=HOST, port=PORT, debug=False)

