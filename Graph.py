# -*- coding: utf-8 -*-
'''
    Mechanizmy tworzenia grafu w neo4j
'''

from neo4j import GraphDatabase
import geopandas as gpd
from shapely.geometry import LineString
import math
from pyproj import Transformer

class GraphCreator:
    def __init__(self, tolerance = 0.5):
        self.node_id = 0             # żeby przypisać współrzędne wierzchołkom
        self.edge_id = 0
        self.index = {}             # index: (x, y) -> wierzchołek
        self.tolerance = tolerance  # tolerancja dociągania wierzchołków -- dodana przez zespół
        self.nodes = []             # lista wierzchołków grafu do dodania
        self.edges = []             # lista krawędzi grafu do dodania
    
    def getNewNodeId(self):
        self.node_id = self.node_id + 1
        return self.node_id        
    
    def getNewEdgeId(self):
        self.edge_id = self.edge_id + 1
        return self.edge_id    

    def nearbyNode(self, p):    # funkcja znajdowania pobliskiego wierzchołka -- dodana przez zespół
        x, y = p
        candidates = []
        for fx in [math.floor, math.ceil]:
            for fy in [math.floor, math.ceil]:
                key = (fx(x / self.tolerance) * self.tolerance, fy(y / self.tolerance) * self.tolerance)
                candidates.append(key)

        return candidates

    @staticmethod
    def _batch_insert(tx, nodes, edges):
        tx.run("""
        UNWIND $nodes AS n
        MERGE (node:Node {id: n.id})
        SET node.x = n.x,
        node.y = n.y,
        node.lon = n.lon,
        node.lat = n.lat,
        node.location = point({
            longitude: n.lon,
            latitude: n.lat
        })
        """, nodes=nodes)

        tx.run("""
        UNWIND $edges AS e
        MATCH (a:Node {id: e.from})
        MATCH (b:Node {id: e.to})
        CREATE (a)-[:ROAD {
            id: e.id,
            road_id: e.road_id,
            direction: e.direction,
            length: e.length,
            speed: e.speed,
            time: e.time,
            geom: e.geom
        }]->(b)
        """, edges=edges)

    def newNode(self, p):                      # funkcja tworzenia nowego wierzchołka w grafie -- znacznie zmieniona przez zespół na potrzebę "dociągania"
        candidates = self.nearbyNode(p)        # dociąganie "na 4 strony świata" 
        for key in candidates:
            if key in self.index:
                return self.index[key]

        snap = candidates[0]
        node_id = self.getNewNodeId()

        
        self.transformer = Transformer.from_crs(
            "EPSG:2180", "EPSG:4326", always_xy=True
        )

        lon, lat = self.transformer.transform(snap[0], snap[1])

        self.nodes.append({
            "id": node_id,
            "x": snap[0],      # nadal do wizualizacji
            "y": snap[1],
            "lon": lon,        # NOWE
            "lat": lat
        })  
        self.index[snap] = node_id                 # dodawanie wierzchołka do index
        return node_id 
        
    def newEdge(self, speed, length, time, p1, p2, geom, directed = False):
        # tworzenie wierzchołków
        n1 = self.newNode(p1)
        n2 = self.newNode(p2)

        # tworzenie krawędzi
        self.edges.append({
            "from": n1,
            "to": n2,
            "id": self.getNewEdgeId(),
            "length": length,
            "speed": speed,
            "time": time,
            "geom": geom
        })
        if not directed:                        # obsługa krawędzi jednokierunkowych -- dodana przez zespół
            self.edges.append({
                "from": n2,
                "to": n1,
                "id": self.getNewEdgeId(),
                "length": length,
                "speed": speed,
                "time": time,
                "geom": geom
            })
            
# funkcja tworząca graf -- zbudowana de facto od zera na potrzebę rozwiązania bazodanowego
def create_graph(driver, database, gdf, tolerance = 0.5):        
    gc = GraphCreator(tolerance)
                            
    for idx, row in gdf.iterrows():
        geom: LineString = row.geometry

        if geom is None or geom.is_empty:
                continue
        
        length = round(geom.length, 2)
        p1 = geom.coords[0]
        p2 = geom.coords[-1]

        points = geom.wkt

        direction = row.get("KIERUNEK", 0)
        speed = row.get("PREDKOSC", 50.0)
        if not speed or speed <= 0: #domyslna predkosc, gdyby ewentualnie brak danych
            speed = 50.0

        time = length / (speed / 3.6)                       # zmiana jednostki prędkości km/h -> m/s

        if direction == 0:
            gc.newEdge(speed, length, time, p1, p2, directed = False, geom=points)
        elif direction == 1:
            gc.newEdge(speed, length, time, p1, p2, directed = True, geom=points)
        elif direction == 2:
            gc.newEdge(speed, length, time, p2, p1, directed = True, geom=points)

    with driver.session(database=database) as session:
        session.execute_write(
            GraphCreator._batch_insert,
            gc.nodes,
            gc.edges
        )

def ensure_constraints(driver, database):
    cypher = """
    CREATE CONSTRAINT node_id_unique IF NOT EXISTS
    FOR (n:Node)
    REQUIRE n.id IS UNIQUE
    """
    with driver.session(database=database) as session:
        session.execute_write(lambda tx: tx.run(cypher))

def ensure_spatial_index(driver, database):
    cypher = """
    CREATE POINT INDEX node_location_index IF NOT EXISTS
    FOR (n:Node)
    ON (n.location)
    """
    with driver.session(database=database) as session:
        session.execute_write(lambda tx: tx.run(cypher))

def project_graph(driver, database):
    query = """
    CALL gds.graph.project.cypher(
      'roadGraph',
      'MATCH (n:Node)
       RETURN n.id AS id, n.lat AS lat, n.lon AS lon',
      'MATCH (source:Node)-[r:ROAD]->(target:Node)
       RETURN source.id AS source,
              target.id AS target,
              r.length AS length,
              r.time AS time'
    )
    """
    with driver.session(database=database) as session:
        session.run(query)

def recreate_db(driver, db):
    with driver.session(database="system") as session:
        session.execute_write(
            lambda tx: tx.run(f"DROP DATABASE {db} IF EXISTS")
        )
        session.execute_write(
            lambda tx: tx.run(f"CREATE DATABASE {db} WAIT")
        )
