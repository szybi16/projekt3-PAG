# -*- coding: utf-8 -*-
'''
    Tu mają się znaleźć ostatecznie funkcje służące rysowaniu dróg na mapie, na razie są tu nasze dwie formy rysowania grafu.
'''

import networkx as nx
import matplotlib.pyplot as plt
import webbrowser
import folium
from pyproj import Transformer

from Graph import *

# Rysunek z NX
def NX_visualisation(g: Graph):
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

# Wyświetlanie w html (weź to okomentuj Filip jakoś)
def Web_visualisation(g: Graph):
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

    lat = (min_lat + max_lat) / 2
    lon = (min_lon + max_lon) / 2

    place_coords_latlon = [lat, lon]
    m = folium.Map(location=place_coords_latlon, zoom_start=15) # Zoom trzeba zautomatyzować

    for e in g.edges.values():
        id1 = e.start.id
        id2 = e.end.id

        lon1, lat1 = vertex_coords_4326[id1]
        lon2, lat2 = vertex_coords_4326[id2]

        folium.PolyLine(
            locations=[[lat1, lon1], [lat2, lon2]],
            color="gray",
            weight=3,
            opacity=0.7
        ).add_to(m)

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

    m.save("mapka.html")
    webbrowser.open_new_tab("mapka.html")