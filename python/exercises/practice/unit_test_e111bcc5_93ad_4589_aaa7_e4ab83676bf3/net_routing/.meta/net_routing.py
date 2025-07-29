import heapq

# Global variables for storing network state
N = 0
graph = {}
node_congestion = []

def initialize_network(n):
    global N, graph, node_congestion
    N = n
    graph = {i: {} for i in range(n)}
    node_congestion = [0] * n

def add_edge(u, v, latency):
    global graph
    # Ensure that u and v are within the current graph
    if u in graph and v in graph:
        graph[u][v] = latency
        graph[v][u] = latency

def remove_edge(u, v):
    global graph
    if u in graph and v in graph[u]:
        del graph[u][v]
    if v in graph and u in graph[v]:
        del graph[v][u]

def update_latency(u, v, new_latency):
    global graph
    if u in graph and v in graph[u]:
        graph[u][v] = new_latency
        graph[v][u] = new_latency

def send_packet(node):
    global node_congestion
    node_congestion[node] += 1

def receive_packet(node):
    global node_congestion
    if node_congestion[node] > 0:
        node_congestion[node] -= 1

def find_optimal_path(start_node, end_node, latency_weight, congestion_weight):
    global graph, node_congestion
    # Number of nodes is determined by the length of the congestion list.
    num_nodes = len(node_congestion)
    # Initialize distances and previous node tracker for path reconstruction.
    dist = [float('inf')] * num_nodes
    prev = [-1] * num_nodes
    # Starting cost includes the congestion at the start node.
    dist[start_node] = node_congestion[start_node] * congestion_weight
    heap = [(dist[start_node], start_node)]
    
    while heap:
        current_cost, u = heapq.heappop(heap)
        if current_cost != dist[u]:
            continue
        if u == end_node:
            break
        # Explore neighbors
        for v, lat in graph[u].items():
            # Edge cost plus congestion cost at node v.
            new_cost = current_cost + (lat * latency_weight) + (node_congestion[v] * congestion_weight)
            if new_cost < dist[v]:
                dist[v] = new_cost
                prev[v] = u
                heapq.heappush(heap, (new_cost, v))
    
    if dist[end_node] == float('inf'):
        return []
    
    # Reconstruct the path from end_node back to start_node.
    path = []
    current = end_node
    while current != -1:
        path.append(current)
        current = prev[current]
    path.reverse()
    return path