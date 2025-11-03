import arcpy
import math
import heapq
import matplotlib.pyplot as plt
import networkx as nx
import time
import webbrowser
import folium
from pyproj import Transformer
#roads = r"BDOT\dodatkowe\duzo_drog.shp"
# roads = r"BDOT\kujawsko_pomorskie_m_Torun\fragment_roads.shp"

duzeDane = "\Dane\Drogi_Bydgoszcz.shp"
maleDane = "\Dane\Drogi_Bydgoszcz_Male.shp"
testKierunek = "\Dane\maleKierunek.shp"
m = r""
j = r""
f = r"C:\Studia\Sezon_3\Programowania_aplikacji_geoinformacyjnych\Projekt"

roads = f + maleDane

vertices = {}
vertex_coords = {}
vertex_edges = {}
edges = []
vertex_counter = 0
edge_counter = 0
tolerance = 0.5


def find_nearby_vertex(x, y, tolerance):
    candidates = []
    for fx in [math.floor, math.ceil]:
        for fy in [math.floor, math.ceil]:
            key = (fx(x / tolerance) * tolerance, fy(y / tolerance) * tolerance)
            candidates.append(key)

    return candidates


def get_or_create_vertex(x, y):
    global vertex_counter
    candidates = find_nearby_vertex(x, y, tolerance)
    for key in candidates:
        if key in vertices:
            return vertices[key]

    vertex_id = vertex_counter
    vertices[candidates[0]] = vertex_id
    vertex_coords[vertex_id] = candidates[0]
    vertex_edges[vertex_id] = []
    vertex_counter += 1
    return vertices[candidates[0]]


with arcpy.da.SearchCursor(roads, ["OID@", "SHAPE@"]) as cursor:
    for row in cursor:
        jezdnia_id = row[0]
        geom = row[1]
        start = geom.firstPoint
        end = geom.lastPoint

        id_from = get_or_create_vertex(start.X, start.Y)
        id_to = get_or_create_vertex(end.X, end.Y)

        length = geom.length

        edge = {
            "id": edge_counter,
            "id_from": id_from,
            "id_to": id_to,
            "id_jezdni": jezdnia_id,
            "length": length
        }
        edges.append(edge)
        vertex_edges[id_from].append(edge_counter)

        edge_rev = {
            "id": edge_counter + 1,
            "id_from": id_to,
            "id_to": id_from,
            "id_jezdni": jezdnia_id,
            "length": length
        }

        edges.append(edge_rev)
        vertex_edges[id_to].append(edge_counter + 1)

        edge_counter += 2


def dijkstra(start, end, vertex_edges, edges):
    S = set()
    # Q = [(0, start)]
    Q = {start}
    d = {v: math.inf for v in vertex_edges.keys()}
    p = {v: None for v in vertex_edges.keys()}
    d[start] = 0

    while Q:
        #_, v = heapq.heappop(Q)
        v = min(Q, key=lambda x: d[x])
        Q.remove(v)

        if v in S:
            continue
        S.add(v)

        if v == end:
            break

        for edge_id in vertex_edges[v]:
            e = edges[edge_id]
            if e["id_from"] == v:
                u = e["id_to"]
            else:
                u = e["id_from"]

            length = e["length"]

            if u in S:
                continue

            new_d = d[v] + length
            if new_d < d[u]:
                d[u] = new_d
                p[u] = v
                #heapq.heappush(Q, (d[u], u))
                Q.add(u)

    path = []
    v = end
    while v is not None:
        path.append(v)
        v = p[v]
    path.reverse()

    if d[end] == math.inf:
        return None, math.inf
    return path, d[end]


def heurystyka(point1_id, point2_id, vertex_coords):
    x1, y1 = vertex_coords[point1_id]
    x2, y2 = vertex_coords[point2_id]

    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    # return 0


def aGwiazdka(start, end, vertex_edges, edges, vertex_coords):
    S = set()
    #Q = [(0 + heurystyka(start, end, vertex_coords), start)] 
    Q = {start}
    h = {}
    h[start] = heurystyka(start, end, vertex_coords)
    d = {v: math.inf for v in vertex_edges.keys()}
    p = {v: None for v in vertex_edges.keys()}
    d[start] = 0

    while Q:
        #_, v = heapq.heappop(Q) 
        v = min(Q, key=lambda x: d[x] + h[x])
        Q.remove(v)

        if v in S:
            continue
        S.add(v)

        if v == end:
            break

        for edge_id in vertex_edges[v]:
            e = edges[edge_id]
            if e["id_from"] == v:
                u = e["id_to"]
            else:
                u = e["id_from"]

            length = e["length"]

            if u in S:
                continue

            new_d = d[v] + length
            if new_d < d[u]:
                d[u] = new_d
                p[u] = v
                # f_u = new_d + heurystyka(u, end, vertex_coords)
                # heapq.heappush(Q, (f_u, u))
                h[u] = heurystyka(u, end, vertex_coords)
                Q.add(u)

    path = []
    v = end
    while v is not None:
        path.append(v)
        v = p[v]
    path.reverse()

    if d[end] == math.inf:
        return None, math.inf
    return path, d[end]

def save_to_graph(plik_wyjsciowy, vertex_coords, vertex_edges, edges):

    title = "Vertex_ID X Y Neighbours_IDs\n"

    with open(plik_wyjsciowy, 'w', encoding='utf-8') as file:
        file.write(title)

        for id_w, (x, y) in vertex_coords.items():

            neighbor_ids = set()

            for edge_id in vertex_edges[id_w]:
                edge = edges[edge_id]

                neighbor_id = edge["id_to"]
                if neighbor_id != id_w:
                    neighbor_ids.add(neighbor_id)

            sorted_neighbors = sorted(list(neighbor_ids))
            neighbors_list_str = ' '.join(map(str, sorted_neighbors))
            line = f"{id_w}\t{x}\t{y}\t{neighbors_list_str}\n"
            file.write(line)

    # DO SPRAWDZENIA SOBIE ---------------------------------------


print(f"Liczba wierzchołków: {len(vertices)}")
print(f"Liczba krawędzi: {len(edges)}")
# print("\n Wierzchołki ")
# for id_w, (x, y) in vertex_coords.items():
#     out_edges = vertex_edges[id_w]
#     print(f"ID: {id_w}, X: {x}, Y: {y}, edge_out: {out_edges}")

start = 250
end = 516

#-------------------------------------------------------------------------------------------------------------

t_start_dijkstra = time.time()
path, distance = dijkstra(start, end, vertex_edges, edges)
t_end_dijkstra = time.time()
dijk_time = t_end_dijkstra - t_start_dijkstra
print("Dijkstra")
print("Najkrotsza trasa od", start, "do", end, ":")
print("sciezka:", path)
print("Dlugosc trasy:", distance, "metrow")
print(f"Czas działania algorytmu: {dijk_time:.15f} sekundy\n\n")

#-------------------------------------------------------------------------------------------------------------

t_start_gwiazdka = time.time()
path, distance = aGwiazdka(start, end, vertex_edges, edges, vertex_coords)
t_end_gwiazdka = time.time()
gw_time = t_end_gwiazdka - t_start_gwiazdka
print("A*")
print("Najkrotsza trasa od", start, "do", end, ":")
print("sciezka:", path)
print("Dlugosc trasy:", distance, "metrow")
print(f"Czas działania algorytmu: {gw_time:.15f} sekundy\n\n")

#-------------------------------------------------------------------------------------------------------------


# Tymczasowy rysunek

G = nx.Graph()
for e in edges:
    f, t, l = e["id_from"], e["id_to"], e["length"]
    G.add_edge(f, t, weight=l)

pos = {vid: (x, y) for vid, (x, y) in vertex_coords.items()}

plt.figure(figsize=(10, 8))
nx.draw(G, pos, node_size=40, node_color="red", edge_color="gray", with_labels=True, font_size=8)

plt.show()

#Wyswietlanie w oddzielnej stronie
transformer = Transformer.from_crs("EPSG:2180", "EPSG:4326", always_xy=True)

vertex_coords_4326 = {
    vertex_id: transformer.transform(x, y)
    for vertex_id, (x, y) in vertex_coords.items()
}

min_lat = min(v[1] for v in vertex_coords_4326.values())
max_lat = max(v[1] for v in vertex_coords_4326.values())
min_lon = min(v[0] for v in vertex_coords_4326.values())
max_lon = max(v[0] for v in vertex_coords_4326.values())

lat = (min_lat + max_lat) / 2
lon = (min_lon + max_lon) / 2

place_coords_latlon = [lat, lon]
m = folium.Map(location=place_coords_latlon, zoom_start=15)

for e in edges:
    id1 = e["id_from"]
    id2 = e["id_to"]

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
