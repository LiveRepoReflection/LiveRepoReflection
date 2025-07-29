import heapq

def optimal_packet_route(network, source, destination, packet_size):
    if source == destination:
        return [source]

    # Initialize the distance for all nodes as infinity, except the source.
    dist = {node: float('inf') for node in network}
    dist[source] = 0

    # Dictionary to track the previous node in the optimal path.
    prev = {}

    # Priority queue for Dijkstra's algorithm: (current_cost, current_node)
    heap = [(0, source)]

    while heap:
        current_cost, node = heapq.heappop(heap)

        if current_cost > dist[node]:
            continue

        if node == destination:
            break

        # Check each neighbor of the current node.
        for neighbor, edge in network[node].items():
            bandwidth = edge.get('bandwidth', 0)
            if bandwidth == 0:
                # Skip broken link (bandwidth zero)
                continue

            base_cost = edge.get('cost', 0)
            # Calculate utilization ratio: packet_size (in MB) converted to megabits by multiplying by 8.
            utilization = (packet_size * 8) / bandwidth

            penalty = 0
            if utilization > 0.8:
                penalty = base_cost * (utilization - 0.8) * 5

            effective_cost = base_cost + penalty
            new_cost = current_cost + effective_cost

            if new_cost < dist.get(neighbor, float('inf')):
                dist[neighbor] = new_cost
                prev[neighbor] = node
                heapq.heappush(heap, (new_cost, neighbor))

    # If destination is unreachable, return an empty list.
    if destination not in dist or dist[destination] == float('inf'):
        return []

    # Reconstruct the path from destination back to source.
    path = []
    current = destination
    while current != source:
        path.append(current)
        current = prev.get(current)
        if current is None:
            return []
    path.append(source)
    return path[::-1]