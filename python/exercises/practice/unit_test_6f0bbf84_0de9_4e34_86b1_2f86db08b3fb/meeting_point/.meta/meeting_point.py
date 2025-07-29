import heapq

def find_optimal_meeting_point(n, edges, friends):
    # Build graph as an adjacency list
    graph = {i: [] for i in range(n)}
    for u, v, w in edges:
        graph[u].append((v, w))
        graph[v].append((u, w))
    
    # Dijkstra's algorithm to compute shortest distances from a source
    def dijkstra(source):
        dist = [float('inf')] * n
        dist[source] = 0
        heap = [(0, source)]
        while heap:
            d, curr = heapq.heappop(heap)
            if d > dist[curr]:
                continue
            for neighbor, weight in graph[curr]:
                new_dist = d + weight
                if new_dist < dist[neighbor]:
                    dist[neighbor] = new_dist
                    heapq.heappush(heap, (new_dist, neighbor))
        return dist

    # For each friend compute the shortest distances to every node
    # We'll store the distances in a list of lists: distances[i][j] is the distance from friend i to node j.
    friend_dists = []
    for friend in friends:
        friend_dists.append(dijkstra(friend))
    
    # Find the meeting point that minimizes the maximum travel time from any friend.
    # For each node, compute the maximum distance over all friends.
    optimal_node = None
    optimal_max_dist = float('inf')
    
    for node in range(n):
        current_max = 0
        for dist in friend_dists:
            current_max = max(current_max, dist[node])
        # if current_max is less than our current optimal, or equal but smaller node number
        if current_max < optimal_max_dist or (current_max == optimal_max_dist and (optimal_node is None or node < optimal_node)):
            optimal_max_dist = current_max
            optimal_node = node
    
    return optimal_node