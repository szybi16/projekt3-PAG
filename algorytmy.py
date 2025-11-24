# -*- coding: utf-8 -*-
'''
    W tym pliku umieszczamy funkcje będące implementacjami algorytmów wyszukiwania drogi, ew. funkcje pomocnicze.
'''

import math
import heapq

from Graph import Node, Graph, Edge

#### Algorytm Dijkstra -- nie używany i nieaktualny
def dijkstra(start: Node, end: Node):
    S = set()                           # odwiedzone
    Q = [(0, start)]                    # kolejka priorytetowa
    d = {}                              # zbiór odległości
    p = {}                              # zbiór poprzedników
    d[start] = 0
    p[start] = None

    while Q:
        _, v = heapq.heappop(Q)         # obsługa kolejki, v - wierzchołek 

        if v in S:                      # zabezpieczenie przed wejściem na odwiedzony wierzchołek
            continue
        S.add(v)

        if v == end:                    # zakończenie poszukiwań
            break

        for e, u in v.edges:            # sąsiad u, po drugiej stronie krawędzi e
            length = e.cost

            if u in S:                  # zabezpieczenie przed wejściem na odwiedzony wierzchołek
                continue

            new_d = d[v] + length
            if not u in d or new_d < d[u]:
                d[u] = new_d
                p[u] = v
                heapq.heappush(Q, (d[u], u))

    # Rekonstrukcja ścieżki
    path = []
    v = end
    while v is not None:
        path.append(v)
        v = p[v]
    path.reverse()

    if not end in d:                    # obsługa braku ścieżki  
        return None, math.inf
    return path, d[end]

def heurystyka(node1: Node, node2: Node, graph: Graph, route_type: str):

    dx = node2.x - node1.x
    dy = node2.y - node1.y
    distance_m = math.sqrt(dx**2 + dy**2)

    max_speed_kmh = getattr(graph, "max_speed_kmh", 120)
    v_max = max_speed_kmh/ 3.6
    if route_type == "fastest":
        return distance_m / v_max
    elif route_type == "shortest":
        return distance_m

def cost(e: Edge, route_type: str) :
    if route_type == "fastest":
        v = e.speed / 3.6
        time = e.length / v
        return time
    elif route_type == "shortest":
        return e.length

def aGwiazdka(start: Node, end: Node, graph: Graph, route_type: str):
    S = set()                           # odwiedzone
    Q = [(0, start)]                    # kolejka priorytetowa
    h = {}                              # zbiór heurystyk
    d = {}                              # zbiór odległości
    p = {}                              # zbiór poprzedników
    p_edge = {}                         # zbiór poprzednich krawędzi
    h[start] = heurystyka(start, end, graph, route_type)
    d[start] = 0
    p[start] = None
    p_edge[start] = None
    while Q:
        _, v = heapq.heappop(Q)         # obsługa kolejki, v - wierzchołek 

        if v in S:                      # zabezpieczenie przed wejściem na odwiedzony wierzchołek
            continue
        S.add(v)

        if v == end:                    # zakończenie poszukiwań
            break

        for e, u in v.edges:            # sąsiad u, po drugiej stronie krawędzi e
            route_cost = cost(e, route_type)
            if u in S:                  # zabezpieczenie przed wejściem na odwiedzony wierzchołek
                continue

            new_d = d[v] + route_cost
            if not u in d or new_d < d[u]:
                d[u] = new_d
                p[u] = v
                p_edge[u] = e
                f_u = new_d + heurystyka(u, end, graph, route_type)
                heapq.heappush(Q, (f_u, u))

    # Rekonstrukcja ścieżki
    path = []              
    v = end
    while v is not None:
        if(p_edge[v]):
            path.append(p_edge[v])
        v = p[v]
    path.reverse()

    if not end in d:                    # obsługa braku ścieżki  
        return None, math.inf
    return path, d[end]












