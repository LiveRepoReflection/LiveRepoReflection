import heapq
from collections import defaultdict

def route_deliveries(graph, packages):
    """
    Given a directed graph and a list of packages that need to be delivered,
    this function returns the maximum number of packages that can be delivered 
    on time. Each package is represented as a tuple (origin, destination, deadline).

    The graph is represented as a dictionary where each key is a node and each value
    is a list of tuples (neighbor, cost) representing an edge from the node to the neighbor
    with the associated travel cost.

    The function groups packages by their origin and computes the shortest paths from 
    each origin using Dijkstra's algorithm. For each package, if the shortest path total 
    cost from its origin to destination is within the deadline, it is considered deliverable.
    """
    # Group packages by origin for efficient processing
    packages_by_origin = defaultdict(list)
    for origin, destination, deadline in packages:
        packages_by_origin[origin].append((destination, deadline))

    deliverable_count = 0

    # Process each unique origin
    for origin, pkg_list in packages_by_origin.items():
        # Compute shortest path distances from this origin using Dijkstra's algorithm
        dist = {}
        heap = [(0, origin)]
        while heap:
            current_cost, node = heapq.heappop(heap)
            if node in dist:
                continue
            dist[node] = current_cost
            for neighbor, weight in graph.get(node, []):
                if neighbor not in dist:
                    heapq.heappush(heap, (current_cost + weight, neighbor))
        
        # Check each package with the current origin
        for destination, deadline in pkg_list:
            # For packages where origin equals destination, the cost is 0.
            if destination in dist and dist[destination] <= deadline:
                deliverable_count += 1

    return deliverable_count