# -*- coding: utf-8 -*-
'''
    W tym pliku umieszczamy funkcje będące implementacjami algorytmów wyszukiwania drogi, ew. funkcje pomocnicze.
'''
from Graph import *

def aGwiazdka(driver, database, start_id, end_id, route_type="fastest"):
    weight = "time" if route_type == "fastest" else "length"

    query = f"""
    CALL gds.shortestPath.astar.stream(
      'roadGraph',
      {{
        sourceNode: $start,
        targetNode: $end,
        relationshipWeightProperty: '{weight}',
        latitudeProperty: 'lat',
        longitudeProperty: 'lon'
      }}
    )
    YIELD nodeIds, totalCost
    UNWIND nodeIds AS gdsId
    MATCH (n:Node)
    WHERE n.id = gdsId
    RETURN collect(n.id) AS nodePath, totalCost
    """

    with driver.session(database=database) as session:
        rec = session.run(
            query,
            {"start": start_id, "end": end_id}
        ).single()

        if not rec:
            return [], float("inf")

        return rec["nodePath"], rec["totalCost"]

def routes(driver, database, start_id, end_id, route_type="fastest"):
    """
    Zwraca zawsze dwie ścieżki (path1, time1, path2, time2).
    Jeśli dostępna jest tylko jedna – zwraca ją podwójnie.
    """

    weight = "time" if route_type == "fastest" else "length"

    query = f"""
    CALL gds.shortestPath.yens.stream(
      'roadGraph',
      {{
        sourceNode: $start,
        targetNode: $end,
        k: 2,
        relationshipWeightProperty: '{weight}'
      }}
    )
    YIELD index, nodeIds, totalCost
    RETURN index, nodeIds, totalCost
    ORDER BY index
    """

    with driver.session(database=database) as session:
        records = list(session.run(
            query,
            {"start": start_id, "end": end_id}
        ))

        # Brak jakiejkolwiek ścieżki
        if not records:
            return [], float("inf"), [], float("inf")

        paths = []

        for rec in records:
            node_ids = rec["nodeIds"]
            total_cost = rec["totalCost"]

            edges = []
            for u, v in zip(node_ids[:-1], node_ids[1:]):
                r = session.run(
                    """
                    MATCH (n1:Node {id:$u})-[r:ROAD]->(n2:Node {id:$v})
                    RETURN r.geom AS geom,
                           r.length AS length,
                           r.speed AS speed
                    """,
                    {"u": u, "v": v}
                ).single()

                if r:
                    edges.append({
                        "geom": r["geom"],
                        "length": r["length"],
                        "speed": r["speed"]
                    })

            paths.append((edges, total_cost))

        # Jeśli jest tylko jedna ścieżka → duplikujemy
        if len(paths) == 1:
            paths.append(paths[0])

        (path1, time1), (path2, time2) = paths[:2]
        return path1, time1, path2, time2
