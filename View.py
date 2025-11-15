# -*- coding: utf-8 -*-
'''
    Tu mają się znaleźć ostatecznie funkcje służące rysowaniu dróg na mapie, na razie są tu nasze dwie formy rysowania grafu.
'''

import networkx as nx
import matplotlib.pyplot as plt
import webbrowser
import folium
import numpy as np
from pyproj import Transformer
from Graph import *

# Rysunek z NX
def nx_visualisation(g: Graph):
    G = nx.Graph()
        
    # Wierzchołki
    for node_id, node in g.nodes.items():
        G.add_node(node_id, pos=(node.x, node.y))

    # Krawędzie
    for edge_id, edge in g.edges.items():
        G.add_edge(edge.start.id, edge.end.id, weight=edge.cost)

    # Pozycje dla rysunku
    pos = {node_id: (node.x, node.y) for node_id, node in g.nodes.items()}

    nx.draw(G, pos, node_size=40, node_color="red", edge_color="gray", with_labels=True, font_size=8)
    plt.axis('equal')
    plt.show()

#Liczenie odległości pomiędzy wierzchołkami
def distance_to_point(start_node, end_node):
    x_start, y_start = start_node[0], start_node[1]
    x_end, y_end = end_node[0], end_node[1]
    distance = np.sqrt((x_end - x_start) ** 2 + (y_end - y_start) ** 2)
    return distance

#Obliczanie najbliższego wierzchołka do punktu
def calculate_nearest_point(x_coords, y_coords, g: Graph):
    #Zmiana współrzędnych na układ 2180
    transformer_to_meters = Transformer.from_crs("EPSG:4326", "EPSG:2180", always_xy=True)
    x_coords, y_coords = transformer_to_meters.transform(x_coords, y_coords)
    #Ustalenei odległości bounding boxa
    radius = 100
    nearest_node_id = None
    min_x = x_coords - radius
    max_x = x_coords + radius
    min_y = y_coords - radius
    max_y = y_coords + radius
    #Początkowa najkrótsza odległość - nieskończoność
    min_distance = float("inf")
    #iterowanie przez punkty
    for node_id, node in g.nodes.items():
        x, y = node.x, node.y
        #Sprawdzanie czy punkt znajduje się w bounding boxie
        if min_x <= x <= max_x and min_y <= y <= max_y:
            #obliczanie odległości dla punktu
            current_distance = distance_to_point([x_coords, y_coords], [x, y])
            #Jeśli odległość jest mniejsza niż dla wcześniejszych punktów to nadpisujemy
            if current_distance < min_distance:
                min_distance = current_distance
                nearest_node_id = node_id

    return nearest_node_id, min_distance

#Obliczenie miejsca, w którym mamy dane
def start_location(g: Graph):
    transformer = Transformer.from_crs("EPSG:2180", "EPSG:4326", always_xy=True)

    # Transformacja współrzędnych na WGS 84
    vertex_coords_4326 = {}
    for node_id, node in g.nodes.items():
        lon, lat = transformer.transform(node.x, node.y)
        vertex_coords_4326[node_id] = (lon, lat)

    min_lat = min(v[1] for v in vertex_coords_4326.values())
    max_lat = max(v[1] for v in vertex_coords_4326.values())
    min_lon = min(v[0] for v in vertex_coords_4326.values())
    max_lon = max(v[0] for v in vertex_coords_4326.values())

    # Obliczanie środka dla całego obszaru
    lat = (min_lat + max_lat) / 2
    lon = (min_lon + max_lon) / 2

    place_coords_latlon = [lat, lon]
    #Zwracamy wspórzędne punktu oraz słownik ze współrzędnymi punktów w układzie Mercatora
    return place_coords_latlon, vertex_coords_4326

# Wyświetlanie w html
def web_visualisation(g: Graph, path):
    place_coords_latlon, vertex_coords_4326 = start_location(g)
    #Tworzenie mapy
    m = folium.Map(location=place_coords_latlon, zoom_start=15)
    #Punty dla początka i końca w celu wyświetlenia markerów
    start_id = path[0].id
    end_id = path[-1].id

    lon_start, lat_start = vertex_coords_4326[start_id]
    lon_end, lat_end = vertex_coords_4326[end_id]
    location_start = [lat_start, lon_start]
    location_end = [lat_end, lon_end]
    
    #Rysowanie linii trasy
    for e in g.edges.values():
        id1 = e.start
        id2 = e.end

        lon1, lat1 = vertex_coords_4326[id1.id]
        lon2, lat2 = vertex_coords_4326[id2.id]
        if id1 in path and id2 in path:
            folium.PolyLine(
                locations=[[lat1, lon1], [lat2, lon2]],
                color="red",
                weight=5,
                opacity=1
            ).add_to(m)

    #Rysowanie markerów początka i końca
    folium.Marker(
        location=location_start,
        tooltip="Start",
        icon=folium.Icon(color='black', icon='flag', prefix='fa')
    ).add_to(m)

    folium.Marker(
        location=location_end,
        tooltip="Koniec",
        icon=folium.Icon(color='blue', icon='flag', prefix='fa')
    ).add_to(m)
    """
    for vertex_id, (lon, lat) in vertex_coords_4326.items():
        folium.CircleMarker(
            location=[lat, lon],
            radius=3,
            color="black",
            fill=True,
            fill_color="black",
            fill_opacity=1.0,
            popup=f"ID: {vertex_id}"
        ).add_to(m)
    """
    #Zapis i otwarcie w przeglądarce
    m.save("mapka.html")
    webbrowser.open_new_tab("mapka.html")
