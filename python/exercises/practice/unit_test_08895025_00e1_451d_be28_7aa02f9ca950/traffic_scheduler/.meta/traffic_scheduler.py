import heapq
import math

def optimize_traffic(N, roads, phases):
    # Build road map: for each node, list outgoing roads as (j, travel_time)
    road_map = {i: [] for i in range(N)}
    for u, v, t in roads:
        road_map[u].append((v, t))
    
    # Pre-calculate cycle length for each node. It is assumed that sum of durations equals cycle length.
    cycle = {}
    for i in range(N):
        cycle[i] = sum(duration for (_, _, duration) in phases.get(i, []))
    
    # Function to compute waiting time at intersection 'node' when transitioning from 'prev' to 'next'
    def waiting_time(node, prev, next_node):
        allow = 0
        for incoming, outgoing, duration in phases.get(node, []):
            if prev in incoming and next_node in outgoing:
                allow += duration
        if allow == 0:
            return None  # Movement not allowed at this intersection.
        return (cycle[node] - allow) / 2.0

    # Compute all pairs shortest paths over the stateful graph.
    # State: (current_node, previous_node) where previous_node is the node from which we arrived.
    # For source nodes, previous is None and no waiting time is incurred.
    # We'll compute the minimal cost from source s to every destination d across all valid states.
    # If any destination d (d != s) is unreachable from s, we'll eventually return float('inf').
    
    # overall_sum and count of pairs
    total_cost = 0.0
    reachable_pairs = 0
    
    for s in range(N):
        # distances: key: (node, prev) value: cost
        dist = {}
        # Priority queue holds tuples (cost, node, prev)
        heap = []
        # Starting state: (s, None) with 0 cost.
        dist[(s, None)] = 0.0
        heapq.heappush(heap, (0.0, s, None))
        
        while heap:
            cost, node, prev = heapq.heappop(heap)
            if cost > dist.get((node, prev), float('inf')):
                continue
            # From the current state, try all outgoing edges.
            # For the source state (prev is None), no waiting time is added.
            for next_node, travel_time in road_map.get(node, []):
                # Determine additional waiting time at node if not starting state.
                if prev is None:
                    wait = 0.0
                else:
                    wait_val = waiting_time(node, prev, next_node)
                    if wait_val is None:
                        # Movement not allowed at this intersection for this turning move.
                        continue
                    wait = wait_val
                new_cost = cost + wait + travel_time
                new_state = (next_node, node)
                if new_cost < dist.get(new_state, float('inf')):
                    dist[new_state] = new_cost
                    heapq.heappush(heap, (new_cost, next_node, node))
        
        # After Dijkstra from source s, record minimal cost to every destination d (d != s)
        for d in range(N):
            if d == s:
                continue
            best = float('inf')
            for key, c in dist.items():
                node, _ = key
                if node == d and c < best:
                    best = c
            if best == float('inf'):
                return float('inf')
            total_cost += best
            reachable_pairs += 1
    
    if reachable_pairs == 0:
        return float('inf')
    return total_cost / reachable_pairs