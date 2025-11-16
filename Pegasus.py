# -*- coding: utf-8 -*-
"""
Plik zawiera obsługę serverową w stylu aplikacji z biblioteki flask
Nasłuchujemy użytkownika hehe (mimo to że to my)
Tzw. Mózg wszystkiego
"""
import flask
import folium
from flask import Flask
from View import *
from algorytmy import *
from pyproj import Transformer
#Stworzenie instancji aplikacji FLask, która jest serverem
app = Flask(__name__)

#app.route('/') określa, że gdy wejdziemy na naszego localhosta na wybranym porcie to uruchomi index()
@app.route('/')
def index():
    #Dodanie pozyskanego grafu
    graph = flask.current_app.config['GRAPH']
    start_coords, _ = start_location(graph)
    m = folium.Map(location=start_coords, zoom_start=12)
    #Link do pliku javaScript
    js_url = flask.url_for('static', filename='map_click_add.js')
    #Utworzenie tagu HTML dla pliku JavaScript
    script_tag = f'<script src="{js_url}"></script>'
    #Doadajemy go do naszego pliku html z mapki
    m.get_root().html.add_child(folium.Element(script_tag))
    return m._repr_html_()



#Funkcja służąca do obliczania trasy (Akceptuje tylko POST, czyli wysyłanie danych)
@app.route('/calculate',methods=['POST'])
def calculate_route():
    data = flask.request.json
    point1 = data['point1'] # [lat, lon]
    point2 = data['point2'] # [lat, lon]
    route_type = data['route_type']

    graph = flask.current_app.config['GRAPH']
    #Obliczanie najbliższego wierzchołka względem naszego klikniętego punktu
    node_start, dist_to_start = calculate_nearest_point(point1[1],point1[0], graph)
    node_end, dist_to_end = calculate_nearest_point(point2[1],point2[0], graph)

    start = graph.nodes[node_start]
    end = graph.nodes[node_end]

    path, cost, path_edges = aGwiazdka(start, end, graph, route_type)

    # path_edges jest listą krawędzi grafu, więc musimy tylko poskładać z tego geometrię :))
    # Tworzymy z tego listę ponieważ tylko tak Leaflet tak to potrafi obsłużyć :/ It is how it is
    route_coords = rebuild_route(start, path_edges)

    #Zwracamy naszą drogę i punkty początek, koniec jako plik JSONowy
    return flask.jsonify({
        'route': route_coords,
        'start_point': route_coords[0],
        'end_point': route_coords[-1]})