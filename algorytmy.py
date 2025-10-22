import arcpy
import math
import matplotlib.pyplot as plt
import networkx as nx
import time

roads = r"C:\Studia\Sezon_3\Programowania_aplikacji_geoinformacyjnych\Projekt\Drogi3.shp"

vertices = {}
vertex_coords = {}
vertex_edges = {}
edges = []
vertex_counter = 0
edge_counter = 0
tolerance = 1


def round_point(x, y, tolerance):
    return (round(x / tolerance) * tolerance, round(y / tolerance) * tolerance)


def get_or_create_vertex(x, y):
    global vertex_counter
    key = round_point(x, y, tolerance)
    if key not in vertices:
        vertex_id = vertex_counter
        vertices[key] = vertex_id
        vertex_coords[vertex_id] = key
        vertex_edges[vertex_id] = []
        vertex_counter += 1
    return vertices[key]


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
    Q = {start}
    d = {v: math.inf for v in vertex_edges.keys()}
    p = {v: None for v in vertex_edges.keys()}
    d[start] = 0

    while Q:
        v = min(Q, key=lambda x: d[x])
        Q.remove(v)

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
                Q.add(u)

        S.add(v)

    path = []
    v = end
    while v is not None:
        path.insert(0, v)
        v = p[v]

    return path, d[end]


def heurystyka(point1_id, point2_id, vertex_coords):
    x1, y1 = vertex_coords[point1_id]
    x2, y2 = vertex_coords[point2_id]

    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def aGwiazdka(start, end, vertex_edges, edges, vertex_coords):
    g = {v: math.inf for v in vertex_edges.keys()}
    f = {v: math.inf for v in vertex_edges.keys()}
    p = {v: None for v in vertex_edges.keys()}

    g[start] = 0
    f[start] = heurystyka(start, end, vertex_coords)

    Q = {start}

    while Q:
        v = min(Q, key=lambda x: f[x])
        Q.remove(v)

        if v == end:
            break

        for edge_id in vertex_edges[v]:
            e = edges[edge_id]
            u = e["id_to"]

            length = e["length"]

            tentative_g = g[v] + length

            if tentative_g < g[u]:
                p[u] = v
                g[u] = tentative_g
                h = heurystyka(u, end, vertex_coords)
                f[u] = g[u] + h

                if u not in Q:
                    Q.add(u)

    path = []
    v = end
    while v is not None:
        path.insert(0, v)
        v = p.get(v)

    final_distance = g[end] if g[end] != math.inf else None

    return path, final_distance

    # DO SPRAWDZENIA SOBIE ---------------------------------------


# print(f"Liczba wierzchołków: {len(vertices)}")
# print(f"Liczba krawędzi: {len(edges)}")
# print("\n Wierzchołki ")
# for id_w, (x, y) in vertex_coords.items():
# out_edges = vertex_edges[id_w]
# print(f"ID: {id_w}, X: {x}, Y: {y}, edge_out: {out_edges}")

start = 8
end = 98

t_start_dijkstra = time.time()
path, distance = dijkstra(start, end, vertex_edges, edges)
t_end_dijkstra = time.time()
dijk_time = t_end_dijkstra - t_start_dijkstra
print("Dijkstra")
print("Najkrotsza trasa od", start, "do", end, ":")
print("sciezka:", path)
print("Dlugosc trasy:", distance, "metrow")
print(f"Czas działania algorytmu: {dijk_time:.15f} sekundy\n\n")

# -------------------------------------------------------------------------------------------------------------


t_start_gwiazdka = time.time()
path, distance = aGwiazdka(start, end, vertex_edges, edges, vertex_coords)
t_end_gwiazdka = time.time()
gw_time = t_end_gwiazdka - t_start_gwiazdka
print("A*")
print("Najkrotsza trasa od", start, "do", end, ":")
print("sciezka:", path)
print("Dlugosc trasy:", distance, "metrow")
print(f"Czas działania algorytmu: {gw_time:.15f} sekundy\n\n")

G = nx.Graph()
for e in edges:
    f, t, l = e["id_from"], e["id_to"], e["length"]
    G.add_edge(f, t, weight=l)

pos = {vid: (x, y) for vid, (x, y) in vertex_coords.items()}

plt.figure(figsize=(10, 8))
nx.draw(G, pos, node_size=40, node_color="red", edge_color="gray", with_labels=True, font_size=8)
plt.title("graf drog BDOT")
plt.show()
