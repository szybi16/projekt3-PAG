# Programowanie Aplikacji Geoinformacyjnych -- Projekt 3: Nawigacja

Program służy do wyznaczania optymalnej trasy pomiędzy dwoma punktami wybranymi na mapie na wczytanych danych drogowych.

Wersja z wykorzystaniem Neo4j

## Sposób uruchamiania

Główny plik służący do uruchamiania programu to **`main.py`**, który obsługuje argumenty wejściowe.
Można uruchomić go bez argumentów - przyjmą wartości domyślne.

### **Dostępne argumenty**

| Argument         | Opis                                                                      | Domyślnie                           |
| ---------------- | ------------------------------------------------------------------------- | ----------------------------------- |
| `--layer`        | Nazwa warstwy danych (w założeniu równa nazwie pliku `.shp`)              | `"Drogi_Bydgoszcz"`                 |
| `--port`         | Port localhost, na którym uruchomiona zostanie mapa                       | `4000`                              |
| `--user-path`    | Ścieżka do folderu z danymi `.shp`                                        | folder `"Dane"` w katalogu programu |
| `--tolerance`    | Tolerancja dociągania krawędzi do bliskich wierzchołków grafu (w metrach) | `0.5`                               |
| `--instance-url` | Adres instancji Neo4j                                                     | `bolt://127.0.0.1:7687`             |
| `--db-user`      | Użytkownik bazy danych Neo4j                                              | `neo4j`                             |
| `--db-password`  | Hasło użytkownika bazy danych Neo4j                                       | `12345678`                          |
| `--db-name`      | Nazwa bazy danych                                                         | `roadnetwork`                       |
| `--rebuild`      | Flaga wymuszająca przebudowę grafu od nowa                                | brak (False)                        |


### **Uruchomienie minimalne**

``` bash
python main.py
```

### **Przykładowe uruchomienie z wykorzystaniem wszystkich argumentów**

``` bash
python main.py \
  --layer Drogi_Krakow \
  --port 5000 \
  --user-path ./dane_shp \
  --tolerance 0.8 \
  --instance-url bolt://localhost:7687 \
  --db-user neo4j \
  --db-password secret \
  --db-name roads \
  --rebuild
```
