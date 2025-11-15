//Czekamy aż załaduje się strona, jeśli się załaduje uruchamiamy to co jest w środku
document.addEventListener('DOMContentLoaded', (event) =>{
    //znalezienie obiektu mapy w Leaflet (folium wykorzystuje Leaflet)
    var map = Object.values(window).find(obj => obj instanceof L.Map);

    if (map) {
        console.log("Mapka otwarta")

        var points = [];
        var currentRoute = null;
        var startLine = null;
        var endLine = null;
        var startMarker = null;
        var endMarker = null;

        //Obsługa kliknięcia
        map.on('click', function(e) {
            //Utworzenie punktu na podstawie funkcji Leafletowych
            var latlon = [e.latlng.lat, e.latlng.lng];
            points.push(latlon);

            //utworzenie ikony markera dla początka i końca drogi
            var startIcon = L.AwesomeMarkers.icon({icon: 'flag', prefix: 'fa', markerColor: 'blue'});
            var endIcon = L.AwesomeMarkers.icon({icon: 'flag', prefix: 'fa', markerColor: 'black'});

            //Utworzenie markera startu
            if (points.length === 1){
                //Usunięcie pozostałości (wcześniejszych tras)
                if (startMarker) {map.removeLayer(startMarker);}
                if (endMarker) {map.removeLayer(endMarker);}
                if (currentRoute) {map.removeLayer(currentRoute);}
                if (startLine) {map.removeLayer(startLine);}
                if (endLine) {map.removeLayer(endLine);}
                //Dodanie markera początkowego
                startMarker = L.marker(latlon, {icon: startIcon}).addTo(map);}

            console.log("Punkcik: ", latlon);
            if (points.length === 2) {
                console.log("2 punkty")
                //Utworzenie markera końca
                endMarker = L.marker(latlon, {icon: endIcon}).addTo(map);

                //Gdy mamy 2 punkty wysyłamy dane do funkcji liczącej trasę
                fetch('/calculate', {
                    method: 'POST', //typ POST - wysyłanie danych
                    headers: {'Content-Type': 'application/json'}, // określenie typu JSON
                    //Zmiana obiektu JSON na tekst
                    body: JSON.stringify({
                        point1: points[0],
                        point2: points[1]
                    })
                })
                    .then(response => response.json()) //Gdy odbierze odpowiedz konwertuje na typ JSON
                    .then(data => { //Obsługa odebranych danych
                        console.log("Trasa:", data.route);

                        // Dodanie drogi na mapie
                        currentRoute = L.polyline(data.route, {color: 'red'}).addTo(map);

                        var startToStart = [points[0],data.start_point];
                        var endToEnd = [data.end_point, points[1]];

                        var polylineOptions = {
                            color: 'grey',
                            dashArray: '10, 10'};
                        //Linie pomiędzy markerem a wierzchołkiem
                        startLine = L.polyline(startToStart, polylineOptions).addTo(map);
                        endLine = L.polyline(endToEnd, polylineOptions).addTo(map);
                        //Czyszczenie
                        points = [];
                    })
                    .catch(error => {
                        console.error('Błąd:', error);
                        //Czyszczenie w przypadku błędu
                        points = [];
                    });
            }
        });
    } else {
        console.error("Użytkownik się nie poddaje. NIE CHCE ODDAĆ DANYCH");
    }
});