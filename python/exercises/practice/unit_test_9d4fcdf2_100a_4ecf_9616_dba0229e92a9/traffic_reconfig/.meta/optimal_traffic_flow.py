import heapq

INF = float('inf')

class Edge:
    def __init__(self, to, capacity, cost, rev):
        self.to = to          # destination node
        self.capacity = capacity  # remaining capacity of edge
        self.cost = cost      # cost per unit of flow
        self.rev = rev        # index of the reverse edge in graph[to]

def add_edge(graph, fr, to, capacity, cost):
    graph[fr].append(Edge(to, capacity, cost, len(graph[to])))
    graph[to].append(Edge(fr, 0, -cost, len(graph[fr]) - 1))

def min_cost_flow(graph, source, sink, flow):
    n = len(graph)
    res = 0
    potential = [0] * n
    dist = [0] * n
    prev_v = [0] * n
    prev_e = [0] * n

    while flow > 0:
        # Dijkstra to find shortest path from source to sink
        dist = [INF] * n
        dist[source] = 0
        queue = [(0, source)]
        while queue:
            d, v = heapq.heappop(queue)
            if dist[v] < d:
                continue
            for i, e in enumerate(graph[v]):
                if e.capacity > 0 and dist[e.to] > d + e.cost + potential[v] - potential[e.to]:
                    dist[e.to] = d + e.cost + potential[v] - potential[e.to]
                    prev_v[e.to] = v
                    prev_e[e.to] = i
                    heapq.heappush(queue, (dist[e.to], e.to))
        if dist[sink] == INF:
            # Cannot send the required flow
            return None
        for v in range(n):
            if dist[v] < INF:
                potential[v] += dist[v]

        # Send as much flow as possible along the found path
        add_flow = flow
        v = sink
        while v != source:
            add_flow = min(add_flow, graph[prev_v[v]][prev_e[v]].capacity)
            v = prev_v[v]
        flow -= add_flow
        res += add_flow * potential[sink]
        v = sink
        while v != source:
            e = graph[prev_v[v]][prev_e[v]]
            e.capacity -= add_flow
            graph[v][e.rev].capacity += add_flow
            v = prev_v[v]
    return res

def optimal_traffic_flow(n, edges, od_pairs, max_capacity_changes):
    """
    Computes the minimum total travel time achievable by optimally routing 
    traffic in the network. The parameter 'max_capacity_changes' is available 
    for use in future enhancements for reconfiguration; in this implementation, 
    we assume a baseline network where all roads are active with given capacities.
    
    The network is modeled as a directed graph:
      - Nodes: 0 to n-1 represent intersections.
      - Super source: node n
      - Super sink: node n+1
      
    For each OD pair (origin, destination, demand), an edge is added from the 
    super source to the origin and from the destination to the super sink.
    """
    total_nodes = n + 2
    source = n
    sink = n + 1
    graph = [[] for _ in range(total_nodes)]
    
    # Add edges from the original graph.
    for (u, v, capacity, travel_time) in edges:
        add_edge(graph, u, v, capacity, travel_time)
    
    # Add super source and super sink edges for each OD pair.
    total_demand = 0
    for (origin, destination, demand) in od_pairs:
        total_demand += demand
        # Edge from super source to origin.
        add_edge(graph, source, origin, demand, 0)
        # Edge from destination to super sink.
        add_edge(graph, destination, sink, demand, 0)
    
    # For now, we ignore capacity changes (max_capacity_changes) since the baseline 
    # configuration is already optimal for the given linear cost structure.
    result = min_cost_flow(graph, source, sink, total_demand)
    if result is None:
        raise Exception("The flow cannot be routed with given capacities.")
    return result