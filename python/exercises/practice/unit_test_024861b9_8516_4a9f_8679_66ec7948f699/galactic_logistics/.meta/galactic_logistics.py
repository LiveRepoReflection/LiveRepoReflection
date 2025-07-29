from collections import defaultdict
from heapq import heappush, heappop
import math

def optimize_logistics(N, M, wormholes, planet_data, T_max):
    # Create adjacency list representation of the network
    graph = defaultdict(list)
    for source, dest, time, cost in wormholes:
        graph[source].append((dest, time, cost))

    # Create production and demand dictionaries for easy access
    production = {}
    demand = {}
    for i, data in enumerate(planet_data, 1):
        production[i] = {good: qty for good, qty in data["production"]}
        demand[i] = {good: qty for good, qty in data["demand"]}

    def dijkstra(start, good_id):
        # Returns shortest paths considering both time and cost
        distances = {i: (float('inf'), float('inf')) for i in range(1, N + 1)}  # (time, cost)
        distances[start] = (0, 0)
        pq = [(0, 0, start)]  # (time, cost, node)
        paths = {start: []}

        while pq:
            curr_time, curr_cost, curr = heappop(pq)
            
            if (curr_time, curr_cost) != distances[curr]:
                continue

            for next_node, time, cost in graph[curr]:
                new_time = curr_time + time
                new_cost = curr_cost + cost

                if new_time <= T_max and (new_time, new_cost) < distances[next_node]:
                    distances[next_node] = (new_time, new_cost)
                    paths[next_node] = paths[curr] + [(curr, next_node)]
                    heappush(pq, (new_time, new_cost, next_node))

        return distances, paths

    def find_max_flow(source, sink, path, capacity):
        if source == sink:
            return capacity

        for curr, next_node in path:
            if curr == source:
                remaining = find_max_flow(next_node, sink, path, capacity)
                if remaining > 0:
                    return remaining
        return 0

    total_cost = 0
    for good in range(1, M + 1):
        # For each good, find producers and consumers
        producers = [(i, production[i].get(good, 0)) for i in range(1, N + 1)]
        consumers = [(i, demand[i].get(good, 0)) for i in range(1, N + 1)]
        
        # Filter out zero quantities
        producers = [(i, qty) for i, qty in producers if qty > 0]
        consumers = [(i, qty) for i, qty in consumers if qty > 0]

        # Check if supply meets demand
        total_supply = sum(qty for _, qty in producers)
        total_demand = sum(qty for _, qty in consumers)
        if total_supply < total_demand:
            return -1

        # For each producer-consumer pair, try to satisfy demand
        for prod_id, prod_qty in producers:
            while prod_qty > 0:
                for cons_id, cons_qty in consumers:
                    if cons_qty <= 0:
                        continue

                    # Find shortest path from producer to consumer
                    distances, paths = dijkstra(prod_id, good)
                    
                    if distances[cons_id][0] > T_max:
                        continue

                    if cons_id not in paths:
                        continue

                    # Calculate maximum flow possible through this path
                    ship_qty = min(prod_qty, cons_qty)
                    if ship_qty <= 0:
                        continue

                    # Update quantities and cost
                    prod_qty -= ship_qty
                    consumers[consumers.index((cons_id, cons_qty))] = (cons_id, cons_qty - ship_qty)
                    total_cost += ship_qty * distances[cons_id][1]

                if prod_qty > 0:
                    # If we still have goods to ship but couldn't find valid paths
                    remaining_demand = sum(qty for _, qty in consumers if qty > 0)
                    if remaining_demand > 0:
                        return -1
                    break

        # Check if all demands are satisfied
        if any(qty > 0 for _, qty in consumers):
            return -1

    return total_cost