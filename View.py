# -*- coding: utf-8 -*-
'''
    Dawniej ten plik służył tworzeniu wizualizacji, stąd jego nazwa.
    Wraz z rozwojem projektu stał się miejscem gdzie zebrane są funkcje geometryczne, znajdowania lokalizacji, długości i składania geometrii
'''
from pyproj import Transformer
from Graph import *
from math import hypot
from shapely import wkt

#Obliczanie najbliższego wierzchołka do punktu
def find_nearest_node(driver, database, lon, lat):
    query = """
    MATCH (n:Node)
    RETURN n.id AS id,
           point.distance(
             n.location,
             point({ longitude: $lon, latitude: $lat })
           ) AS dist
    ORDER BY dist
    LIMIT 1
    """

    with driver.session(database=database) as session:
        r = session.run(query, {"lon": lon, "lat": lat}).single()

    return r["id"], r["dist"]

#Obliczenie miejsca, w którym mamy dane
def start_location(driver, database):
    query = """
    MATCH (n:Node)
    RETURN
        min(n.x) AS min_x,
        max(n.x) AS max_x,
        min(n.y) AS min_y,
        max(n.y) AS max_y
    """

    with driver.session(database=database) as session:
        r = session.run(query).single()

    if r is None:
        return None

    # środek w EPSG:2180
    center_x = (r["min_x"] + r["max_x"]) / 2
    center_y = (r["min_y"] + r["max_y"]) / 2

    # transformacja do WGS84
    transformer = Transformer.from_crs(
        "EPSG:2180", "EPSG:4326", always_xy=True
    )
    lon, lat = transformer.transform(center_x, center_y)

    return [lat, lon]

# Składanie z powrotem geometrii ścieżki
def rebuild_route(driver, database, node_path):
    transformer = Transformer.from_crs("EPSG:2180", "EPSG:4326", always_xy=True)

    full_route = []

    with driver.session(database=database) as session:
        # Przechodzenie przez każdą ścieżkę w celu pozyskania współrzędnych punktów i zamiany ich na układ Leafletowy
        for u, v in zip(node_path[:-1], node_path[1:]):
            rec = session.run(
                """
                MATCH (n1:Node {id:$u})-[r:ROAD]->(n2:Node {id:$v})
                RETURN 
                  r.geom AS geom,
                  n1.x AS x1, n1.y AS y1,
                  n2.x AS x2, n2.y AS y2
                LIMIT 1
                """,
                {"u": u, "v": v}
            ).single()

            if not rec:
                continue

            points = list(wkt.loads(rec["geom"]).coords)
            
            # Kontrola kierunku geometrii i ew. odwracanie
            dist_first = hypot(points[0][0] - rec["x1"], points[0][1] - rec["y1"])
            dist_last   = hypot(points[-1][0] - rec["x1"], points[-1][1] - rec["y1"])

            if dist_last < dist_first:
                points.reverse()

            # Dołączamy współrzędne do całej ścieżki
            for x, y in points:
                lon, lat = transformer.transform(x, y)

                full_route.append([lat, lon])

    return full_route
