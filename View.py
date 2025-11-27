# -*- coding: utf-8 -*-
'''
    Dawniej ten plik służył tworzeniu wizualizacji, stąd jego nazwa.
    Wraz z rozwojem projektu stał się miejscem gdzie zebrane są funkcje geometryczne, znajdowania lokalizacji, długości i składania geometrii
'''
import numpy as np
from pyproj import Transformer
from Graph import *
from math import hypot

#Liczenie odległości pomiędzy wierzchołkami
def distance_to_point(start_node, end_node):
    x_start, y_start = start_node[0], start_node[1]
    x_end, y_end = end_node[0], end_node[1]
    distance = hypot(x_end - x_start, y_end - y_start)
    return distance

#Obliczanie najbliższego wierzchołka do punktu
def calculate_nearest_point(x_coords, y_coords, g: Graph):
    #Zmiana współrzędnych na układ 2180
    transformer_to_meters = Transformer.from_crs("EPSG:4326", "EPSG:2180", always_xy=True)
    x_coords, y_coords = transformer_to_meters.transform(x_coords, y_coords)
    #Ustalenei odległości bounding boxa
    radius = 200
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

#Składanie z powrotem geometrii ścieżki
def rebuild_route(start, path):
    transformer = Transformer.from_crs("EPSG:2180", "EPSG:4326", always_xy=True)

    full_route = []
    
    # Potrzebujemy robić kontrolę kierunków geometrii, więc będziemy zapisywać współrzędne końca poprzedniego fragmentu.
    prev_x = start.x
    prev_y = start.y

    # Przechodzenie przez każdą ścieżkę w celu pozyskania współrzędnych punktów i zamiany ich na układ Leafletowy
    for edge in path:
        points = edge.true_geom 

        # Kontrola kierunku geometrii i ew. odwracanie
        first = points[0]
        last = points[-1]
        dist_first = hypot(first[0] - prev_x, first[1] - prev_y)
        dist_last = hypot(last[0] - prev_x, last[1] - prev_y)
        if dist_last < dist_first:
            points = list(reversed(points))

        # Dołączamy współrzędne do całej ścieżki
        for x, y in points:
            lon, lat = transformer.transform(x, y)
            
            full_route.append([lat, lon])

        prev_x, prev_y = points[-1]

    return full_route
