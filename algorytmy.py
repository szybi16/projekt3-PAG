# -*- coding: utf-8 -*-
'''
    W tym pliku umieszczamy funkcje będące implementacjami algorytmów wyszukiwania drogi, ew funkcje pomocnicze.
'''

import math
import heapq

from Graph import *

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

def heurystyka(node1: Node, node2: Node):
    return math.sqrt((node2.x - node1.x) ** 2 + (node2.y - node1.y) ** 2) # odległość euklidejska

def aGwiazdka(start: Node, end: Node):
    S = set()                           # odwiedzone
    Q = [(0, start)]                    # kolejka priorytetowa
    h = {}                              # zbiór heurystyk
    d = {}                              # zbiór odległości
    p = {}                              # zbiór poprzedników
    h[start] = heurystyka(start, end)
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
                f_u = new_d + heurystyka(u, end)
                heapq.heappush(Q, (f_u, u))

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












