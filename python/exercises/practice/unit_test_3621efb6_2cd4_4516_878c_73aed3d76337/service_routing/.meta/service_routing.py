import heapq

def min_total_cost(N, capacities, graph, M, messages):
    # Build adjacency list from graph
    adj = {i: [] for i in range(N)}
    for u, v, cost in graph:
        adj[u].append((v, cost))
        
    total_cost = 0

    # Process messages in order
    for src, dst, size in messages:
        # Check if source and destination have enough capacity to handle the message size
        if capacities[src] < size or capacities[dst] < size:
            return -1
        
        # If src == dst, no edges are used; still need to deduct capacity from src.
        if src == dst:
            capacities[src] -= size
            continue

        # Dijkstra's algorithm with tie-breaker: (cost, hops)
        # Each entry in the heap: (accumulated_cost, hops, current_node, path_list)
        heap = [(0, 0, src, [src])]
        
        # We use a dictionary to track the best (cost, hops) seen for a node 
        best = {src: (0, 0)}
        
        found_path = None
        
        while heap:
            cost, hops, node, path = heapq.heappop(heap)
            
            # If we reached destination, use this path.
            if node == dst:
                found_path = path
                total_cost += cost
                break
            
            # Explore neighbors. Ensure that the neighbor's capacity is >= size when arrival.
            for neighbor, edge_cost in adj.get(node, []):
                # Check capacity constraint at neighbor
                if capacities[neighbor] < size:
                    continue
                
                new_cost = cost + edge_cost
                new_hops = hops + 1
                
                # Check if we have found a better cost or equal cost with fewer hops before
                if neighbor not in best or new_cost < best[neighbor][0] or (new_cost == best[neighbor][0] and new_hops < best[neighbor][1]):
                    best[neighbor] = (new_cost, new_hops)
                    heapq.heappush(heap, (new_cost, new_hops, neighbor, path + [neighbor]))
                    
        # If no valid path found, return -1
        if found_path is None:
            return -1
        
        # Deduct message size from each service in the found path
        for service in found_path:
            capacities[service] -= size
            
    return total_cost

if __name__ == "__main__":
    # Sample execution can be done here if required.
    pass