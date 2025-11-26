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

def bellcurve(a, b, x):                 # a to 2. miejsce 0 funkcji (koniec interesującej nas części), a b to maksymalna wartość x-1
    m = (b * 16) / (a ** 4)             # współczynnik skalujący
    f1 = (x ** 2) * ((x-a) ** 2)        # kształt funkcji
    f = (f1 * m) + 1
    return f

def cost(e: Edge, route_type: str, prev_route) :
    cost_multiplier = 1
    if prev_route and e in prev_route:  # przeszliśmy po tej krawędzi poprzednim razem
        n = len(prev_route) - 1               # liczba krawędzi w poprzedniej trasie
        i = prev_route.index(e)             # numer krawędzi w poprzedniej trasie
        max_cm = 0.7                        # maksymalne obciążenie dodatkowe trasy
        cost_multiplier = bellcurve(n, max_cm, i)              
    v = e.speed / 3.6
    time = e.length / v
    if route_type == "fastest":
        return time * cost_multiplier, time
    elif route_type == "shortest":
        return e.length * cost_multiplier, time

def aGwiazdka(start: Node, end: Node, graph: Graph, route_type: str, prev_route = None):
    S = set()                           # odwiedzone
    Q = [(0, start)]                    # kolejka priorytetowa
    h = {}                              # zbiór heurystyk
    d = {}                              # zbiór kosztów
    p = {}                              # zbiór poprzedników
    t = {}                              # zbiór czasów przejazdu przez krawędź
    p_edge = {}                         # zbiór poprzednich krawędzi
    h[start] = heurystyka(start, end, graph, route_type)
    d[start] = 0
    t[start] = 0
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
            route_cost, time = cost(e, route_type, prev_route)
            if u in S:                  # zabezpieczenie przed wejściem na odwiedzony wierzchołek
                continue

            new_d = d[v] + route_cost
            if not u in d or new_d < d[u]:
                d[u] = new_d
                t[u] = t[v] + time
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
    return path, t[end]
