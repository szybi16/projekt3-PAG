# Programowanie Aplikacji Geoinformacyjnych -- Projekt 3: Nawigacja

Program służy do wyznaczania optymalnej trasy pomiędzy dwoma punktami wybranymi na mapie na wczytanych danych drogowych.

Wersja z wykorzystaniem Neo4j

## Sposób uruchamiania

Główny plik służący do uruchamiania programu to **`main.py`**, który obsługuje argumenty wejściowe.
Można uruchomić go bez argumentów - przyjmą wartości domyślne.

### **Dostępne argumenty**

`--layer`       :     Nazwa warstwy danych (w założeniu równa nazwie pliku shp bez rozszerzenia domyślnie: "Drogi_Bydgoszcz")
`--port`        :     Port localhost, na którym uruchomiona zostanie mapa (domyślnie: 5000)
`--user-path`   :     Ścieżka do folderu z danymi .shp (domyślnie: folder \"Dane\" w katalogu programu)
`--tolerance`   :     Tolerancja dociągania krawędzi do bliskich wierzchołków grafu (w metrach, domyślnie: 0.5)

### **Uruchomienie minimalne**

``` bash
python main.py
```

### **Przykładowe uruchomienie z wykorzystaniem wszystkich argumentów**

``` bash
python main.py --layer drogi --port 5500 --user-path "C:/Users/Jan/Documents/MojeDane" --tolerance 0.3
```
