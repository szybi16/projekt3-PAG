# -*- coding: utf-8 -*-
'''
    Plik główny istnieje po to żeby:

    1. Przyjmować argumenty;
    2. Uruchamiać funkcje;
    3. Przechowywać stałe ustawiane z kodu;
    (4. łatwo testować nowe funkcje/biblioteki/rozwiązania.)

    Z tego powodu należy utrzymać ten plik stosunkowo krótki i prosty, a także ograniczać ilość tymczasowego kodu i funkcji przed commitem.

        ~ Maciek <3 
'''

import time
import threading
import webbrowser
import argparse
import os
import atexit
from Graph import *
from View import *
from algorytmy import *
from Pegasus import *

# Zestawy danych
maleDane = "Drogi_Bydgoszcz_Male"
testKierunek = "maleKierunek"
duzeDane = "Drogi_Bydgoszcz"
danePredkosc = "Drogi_Predkosc"

# Domyślne dane
default_road_data = duzeDane

def get_args():
    parser = argparse.ArgumentParser(
        description="Opcjonalna konfiguracja argumentów"
    )

    parser.add_argument(
        "--road_data",
        type=str,
        default=default_road_data,
        help=f"Nazwa zbioru danych drogowych (domyślnie: {default_road_data})"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=4000,
        help="Port localhost (domyślnie: 4000)"
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
        default=5.0,
        help="Tolerancja eliminacji niespójności (domyślnie: 5)"
    )

    # 🔹 Neo4j / DB
    parser.add_argument(
        "--instance-url",
        type=str,
        default="bolt://127.0.0.1:7687",
        help="Adres instancji Neo4j (domyślnie: bolt://127.0.0.1:7687)"
    )

    parser.add_argument(
        "--db-user",
        type=str,
        default="neo4j",
        help="Użytkownik bazy danych (domyślnie: neo4j)"
    )

    parser.add_argument(
        "--db-password",
        type=str,
        default="12345678",
        help="Hasło do bazy danych"
    )

    parser.add_argument(
        "--db-name",
        type=str,
        default="roadnetwork",
        help="Nazwa bazy danych (domyślnie: roadnetwork)"
    )

    # 🔹 Flaga
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Wymuś przebudowę danych (domyślnie: False)"
    )

    return parser.parse_args()

def build_config():
    args = get_args()

    user_path = args.user_path or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "Dane"
    )

    HOST = "localhost"
    shp = os.path.join(user_path, f"{args.road_data}.shp")
    url = f"http://{HOST}:{args.port}"

    return {
        "road_data": args.road_data,
        "host": HOST,
        "port": args.port,
        "shp": shp,
        "url": url,
        "tolerance": args.tolerance,
        "instance_url": args.instance_url,
        "user": args.db_user,
        "password": args.db_password,
        "db": args.db_name,
        "rebuild": args.rebuild
    }

###### Kod główny ######

#Otwieramy przeglądarę i dajemy jej czas aby server zdążył się odpalić
def open_browser(URL: str):
    time.sleep(1)
    webbrowser.open(URL)


@atexit.register
def close_driver():
    driver.close()

if __name__ == '__main__':
    # konfiguracja
    config = build_config()

    road_data = config["road_data"]
    HOST = config["host"]
    PORT = config["port"]
    shp = config["shp"]
    URL = config["url"]
    tolerance = config["tolerance"]

    INSTANCE_URL = config["instance_url"]
    USER = config["user"]
    PASSWORD = config["password"]
    db = config["db"]
    rebuild = config["rebuild"]

    driver = GraphDatabase.driver(
        INSTANCE_URL,
        auth=(USER, PASSWORD)
    )
    if rebuild:
        recreate_db(driver, db)
        ensure_constraints(driver, db)

        gdf = gpd.read_file(shp)

        # tworzenie grafu
        create_graph(driver, db, gdf)
        time.sleep(0.5) #na wszelki wypadek, żeby dać czas się bazie uruchomić
        ensure_spatial_index(driver, db)

        # projekcja grafu aby działały algorytmy
        project_graph(driver, db)
    else :
        ensure_spatial_index(driver, db)
    #utworzenie wątku, który pozwala na to, że app i open_browser działa w tym samym momencie inaczej, albo by się otwierało
    #przed włączeniem serwera albo nie uruchomiło by się wcale bo zaczęło by działać app, dopóki się go nie zatrzyma
    threading.Thread(target=open_browser, args=(URL,)).start()
    
    #Dodajemy bazę danych dla aplikacji Flaskowej
    app.config['DRIVER'] = driver
    app.config['DB'] = db
    
    #Uruchomienie serwera, debug=False pozwala na brak restartu gdy sobie 'grzebiemy' w kodzie
    app.run(host=HOST, port=PORT, debug=False)

