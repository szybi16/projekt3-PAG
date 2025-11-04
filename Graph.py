# -*- coding: utf-8 -*-
'''
    Klasy obsługujące obiektowe podejście do grafu, obecnie jest to kod dostarczony przez prowadzącego zmodyfikowany w niewielkim stopniu.

    Prawdopodobnie nie będzie już tu dużo zmian.
'''

import arcpy
import math

class Node:
    def __init__(self, node_id, x, y):
        self.id = node_id   # id
        self.x = x          # współrzędna x
        self.y = y          # współrzędna y
        self.edges = []     # krawędzie wychodzące z wierzchołka
        
    def __repr__(self):
        eids = ",".join([str(e.id) for e, v in self.edges])
        return f"N({self.id},({self.x},{self.y}),[{eids}])"
        
class Edge:
    def __init__(self, edge_id, cost, start, end):
        self.id = edge_id   # id
        self.cost = cost    # waga krawędzi   
        self.start = start  # z wierzchołka
        self.end = end      # do wierzchołka
        
    def __repr__(self):
        sid = self.start.id if self.start is not None else "None"
        eid = self.end.id if self.end is not None else "None"
        return f"E({self.id},{sid},{eid})"
    
class Graph:
    def __init__(self):
        self.edges = {}  # edge_id -> Edge
        self.nodes = {}  # node_id -> Node
        
    def __repr__(self):
        ns = ",".join([str(n) for n in self.nodes.values()]) # all nodes
        es = ",".join([str(e) for e in self.edges.values()]) # all edges
        return f"Graph:\n  Nodes: [{ns}]\n  Edges: [{es}]"

class GraphCreator:
    def __init__(self, tolerance = 0.5):
        self.graph = Graph()        # nowy graf
        self.new_id = 0             # żeby przypisać współrzędne wierzchołkom
        self.index = {}             # index: (x, y) -> Node
        self.tolerance = tolerance  # tolerancja dociągania wierzchołków
        
    def getNewId(self):
        self.new_id = self.new_id + 1
        return self.new_id        
    
    def nearbyNode(self, p):
        x, y = p
        candidates = []
        for fx in [math.floor, math.ceil]:
            for fy in [math.floor, math.ceil]:
                key = (fx(x / self.tolerance) * self.tolerance, fy(y / self.tolerance) * self.tolerance)
                candidates.append(key)

        return candidates

    def newNode(self, p):
        candidates = self.nearbyNode(p)        # dociąganie "na 4 strony świata" 
        for key in candidates:
            if key in self.index:
                return self.index[key]

        p = candidates[0]

        n = Node(self.getNewId(), p[0], p[1])  # tworzenie wierzchołka
        self.graph.nodes[n.id] = n             # dodawanie wierzchołka do kolekcji
        self.index[p] = n                      # dodawanie wierzchołka do index
        return self.index[p]
        
    def newEdge(self, id, length, p1, p2):
        # tworzenie wierzchołków
        n1 = self.newNode(p1)
        n2 = self.newNode(p2)

        # tworzenie krawędzi
        e = Edge(id, length, n1, n2)          
        self.graph.edges[id] = e

        # łączenie krawędzi i wierzchołków
        n1.edges.append((e, n2))
        n2.edges.append((e, n1))
            
def create_graph(workspace, layer, tolerance = 0.5):
    gc = GraphCreator(tolerance)

    # wczytywanie danych
    arcpy.env.workspace = workspace
    cursor = arcpy.SearchCursor(layer)
    for row in cursor:
        length = round(row.Shape.length, 2)
        p1 = (row.Shape.firstPoint.X, row.Shape.firstPoint.Y)
        p2 = (row.Shape.lastPoint.X, row.Shape.lastPoint.Y)
        gc.newEdge(row.FID, length, p1, p2)
        
    return gc.graph
    