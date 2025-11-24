//Czekamy aż załaduje się strona, jeśli się załaduje uruchamiamy to co jest w środku
document.addEventListener('DOMContentLoaded', (event) =>{
    //znalezienie obiektu mapy w Leaflet (folium wykorzystuje Leaflet)
    var map = Object.values(window).find(obj => obj instanceof L.Map);

    if (map) {
        console.log("Mapka otwarta")

        //Tworzenie kontenera na pole do wyboru typu trasy
        const routeOptionsDiv = document.createElement('div');
        routeOptionsDiv.id = 'routeOptions';

        routeOptionsDiv.style.cssText = "position: absolute; top: 10px; right: 10px; z-index: 1000; background: white; padding: 10px; border-radius: 5px; box-shadow: 0 0 5px rgba(0,0,0,0.3);";

        //Kod html dodający możliwości wyboru w polu
        routeOptionsDiv.innerHTML = `
            <label>Wybierz trasę:</label><br>
            <input type="radio" id="fastest" name="routeType" value="fastest" checked>
            <label for="fastest">Najszybsza</label><br>
            
            <input type="radio" id="shortest" name="routeType" value="shortest">
            <label for="shortest">Najkrótsza</label>
        `;

        //Wstawienie kontenerka z polem do pliku html
        document.body.appendChild(routeOptionsDiv);

        //wyszukiwanie i pobieranie wartości dla zaznaczonego obiektu
        let selectedRouteType = document.querySelector('input[name="routeType"]:checked').value;

        function updateRouteType(e) {
             if (e.target.name === 'routeType' && e.target.checked) {
                selectedRouteType = e.target.value;
             }
        }
        //gdy użytkownik zmieni zdanie co do trasy to zapisujemy to
        routeOptionsDiv.addEventListener('change', updateRouteType);

        //Funkcja do wysyłania wiadomości błędowych
        function displayTemporaryMessage(message, mess_time) {
            const messageDiv = document.createElement('div');
            messageDiv.id = 'tempMessage';
            messageDiv.textContent = message;

            //Styl komunikatu
            messageDiv.style.cssText = `
                position: absolute; 
                top: 50%; 
                left: 50%; 
                transform: translate(-50%, -50%); 
                z-index: 2000; 
                background: #ffcccc; 
                color: #cc0000; 
                padding: 15px 30px; 
                border-radius: 8px; 
                box-shadow: 0 0 10px rgba(0,0,0,0.5);
                font-weight: bold;
                pointer-events: none; 
            `;

            document.body.appendChild(messageDiv);

            // Usuwanie komunikatu
            setTimeout(() => {
                if (document.getElementById('tempMessage')) {
                    document.body.removeChild(messageDiv);
                }
            }, mess_time);
        }

        var points = [];
        var currentRoute = null;
        var alternatywqa = null;
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
                if (alternatywqa) {map.removeLayer(alternatywqa);}
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
                        point2: points[1],
                        route_type: selectedRouteType
                    })
                })
                    .then(response => response.json()) //Gdy odbierze odpowiedz konwertuje na typ JSON
                    .then(data => { //Obsługa odebranych danych
                        if(data.start_equal_end === true){
                            displayTemporaryMessage("Punkty są zbyt blisko siebie przez co punkt startowy i końcowy są w tym samym miejscu. Oddal od siebie punkty w celu wyznaczenia trasy", 3000)
                            if (startMarker) {map.removeLayer(startMarker);}
                            if (endMarker) {map.removeLayer(endMarker);}}
                        console.log("Trasa:", data.route);

                        // Dodanie drogi na mapie
                        alternatywqa = L.polyline(data.route2, {color: 'gray'}).addTo(map);
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
                        //Wyświetlenie użytkownikowi tego co poszło nie tak
                        if(error.message.includes('fetch')) {
                            displayTemporaryMessage("Połączenie z serwerem zostało utracone. Uruchom ponownie serwer.", 30000)
                            if (startMarker) {map.removeLayer(startMarker);}
                            if (endMarker) {map.removeLayer(endMarker);}
                        }else{
                            displayTemporaryMessage("Punkt początkowy lub końcowy znajduje się poza dostępnymi danymi drogowymi.", 3000)
                            if (startMarker) {map.removeLayer(startMarker);}
                            if (endMarker) {map.removeLayer(endMarker);}
                        }
                        points = [];
                    });
            }
        });
    } else {
        console.error("Użytkownik się nie poddaje. NIE CHCE ODDAĆ DANYCH");
        displayTemporaryMessage("Mapa nie chce się załadować.", 60000)
    }
});

// Wyłapywanie zamknięcia okna z mapą i nadanie komunikatu
window.addEventListener("beforeunload", function() {
    navigator.sendBeacon("/shutdown"); 
});