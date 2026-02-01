//Czekamy aż załaduje się strona
document.addEventListener('DOMContentLoaded', (event) =>{
    //znalezienie obiektu mapy w Leaflet
    var map = Object.values(window).find(obj => obj instanceof L.Map);

    if (map) {
        console.log("Mapka otwarta");

        //Tworzenie kontenera na pole do wyboru typu trasy
        const routeOptionsDiv = document.createElement('div');
        routeOptionsDiv.id = 'routeOptions';
        routeOptionsDiv.style.cssText = "position: absolute; top: 10px; right: 10px; z-index: 1000; background: white; padding: 10px; border: 1px solid #ccc; border-radius: 5px;"; // Dodałem ramkę dla estetyki

        routeOptionsDiv.innerHTML = `
            <label>Wybierz trasę:</label><br>
            <input type="radio" id="fastest" name="routeType" value="fastest" checked>
            <label for="fastest">Najszybsza</label><br>
            
            <input type="radio" id="shortest" name="routeType" value="shortest">
            <label for="shortest">Najkrótsza</label>
        `;

        // --- POPRAWKA 1: Dodanie elementu do strony ---
        document.body.appendChild(routeOptionsDiv);

        //wyszukiwanie i pobieranie wartości dla zaznaczonego obiektu
        // Teraz to zadziała, bo element już istnieje w DOM
        let selectedRouteType = document.querySelector('input[name="routeType"]').value;

        function updateRouteType(e) {
             if (e.target.name === 'routeType' && e.target.checked) {
                selectedRouteType = e.target.value;
             }
        }
        routeOptionsDiv.addEventListener('change', updateRouteType);

        //Funkcja do wysyłania wiadomości błędowych
        function displayTemporaryMessage(message, mess_time) {
            const messageDiv = document.createElement('div');
            messageDiv.id = 'tempMessage';
            messageDiv.textContent = message;

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

            setTimeout(() => {
                const existingMsg = document.getElementById('tempMessage');
                if (existingMsg) {
                    document.body.removeChild(existingMsg);
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
        var alternatywqaLabel = null;

        //Obsługa kliknięcia
        map.on('click', function(e) {
            var latlon = [e.latlng.lat, e.latlng.lng];
            points.push(latlon);

            var startIcon = L.AwesomeMarkers.icon({icon: 'flag', prefix: 'fa', markerColor: 'blue'});
            var endIcon = L.AwesomeMarkers.icon({icon: 'flag', prefix: 'fa', markerColor: 'black'});

            if (points.length === 1){
                //Czyszczenie mapy przed nową trasą
                if (startMarker) {map.removeLayer(startMarker);}
                if (endMarker) {map.removeLayer(endMarker);}
                if (currentRoute) {map.removeLayer(currentRoute);}
                if (alternatywqa) {map.removeLayer(alternatywqa);}
                if (startLine) {map.removeLayer(startLine);}
                if (endLine) {map.removeLayer(endLine);}
                if (alternatywqaLabel) {map.removeLayer(alternatywqaLabel);}

                startMarker = L.marker(latlon, {icon: startIcon}).addTo(map);
            }

            console.log("Punkcik: ", latlon);

            if (points.length === 2) {
                console.log("2 punkty - wysyłanie");
                endMarker = L.marker(latlon, {icon: endIcon}).addTo(map);

                fetch('/calculate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        point1: points[0],
                        point2: points[1],
                        route_type: selectedRouteType
                    })
                })
                .then(response => response.json())
                .then(data => {
                    // --- POPRAWKA 2: Rozdzielenie obsługi błędu od sukcesu ---
                    if(data.start_equal_end === true){
                        displayTemporaryMessage("Punkty są zbyt blisko siebie. Oddal od siebie punkty.", 3000);
                        if (startMarker) {map.removeLayer(startMarker);}
                        if (endMarker) {map.removeLayer(endMarker);}
                        points = []; // Reset punktów przy błędzie
                    } else {
                        // Sytuacja poprawna - rysujemy trasę
                        console.log("Trasa:", data.route);

                        if (data.route) {
                             currentRoute = L.polyline(data.route, {color: 'red'}).addTo(map);
                        }

                        // Linie łączące punkty z trasą (jeśli API zwraca te dane)
                        if (data.start_point && data.end_point) {
                            var startToStart = [points[0], data.start_point];
                            var endToEnd = [data.end_point, points[1]];

                            var polylineOptions = {
                                color: 'grey',
                                dashArray: '10, 10'
                            };
                            startLine = L.polyline(startToStart, polylineOptions).addTo(map);
                            endLine = L.polyline(endToEnd, polylineOptions).addTo(map);
                        }

                        // Czyścimy tablicę punktów, aby można było zacząć nową trasę od 1 kliknięcia
                        points = [];
                    }
                })
                .catch(error => {
                    console.error('Błąd:', error);
                    if(error.message && error.message.includes('fetch')) {
                         displayTemporaryMessage("Błąd połączenia z serwerem.", 5000);
                    } else {
                         displayTemporaryMessage("Błąd wyznaczania trasy.", 3000);
                    }
                    // Reset w razie błędu
                    points = [];
                });
            }
        });
    } else {
        console.error("Nie znaleziono mapy");
    }
});

window.addEventListener("beforeunload", function() {
    navigator.sendBeacon("/shutdown"); 
});