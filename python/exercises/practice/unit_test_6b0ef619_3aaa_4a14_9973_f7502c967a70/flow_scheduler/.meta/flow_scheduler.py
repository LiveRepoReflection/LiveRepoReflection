import math
import heapq

class Edge:
    __slots__ = ['to', 'cap', 'cost', 'rev']
    def __init__(self, to, cap, cost, rev):
        self.to = to
        self.cap = cap
        self.cost = cost
        self.rev = rev

def add_edge(graph, frm, to, cap, cost):
    graph[frm].append(Edge(to, cap, cost, len(graph[to])))
    graph[to].append(Edge(frm, 0, -cost, len(graph[frm]) - 1))

def min_cost_flow(num_warehouses, edges, commodities):
    # Create graph with an extra super source (s) and super sink (t)
    n = num_warehouses + 2
    s = num_warehouses     # Super source index
    t = num_warehouses + 1 # Super sink index
    graph = [[] for _ in range(n)]
    
    # For each commodity, add edge from super source to its source and from its destination to super sink.
    total_demand = 0
    for src, dest, demand in commodities:
        total_demand += demand
        add_edge(graph, s, src, demand, 0)
        add_edge(graph, dest, t, demand, 0)
    
    # Add all original edges.
    for u, v, cap, cost in edges:
        add_edge(graph, u, v, cap, cost)
    
    INF = 10**9
    result = 0
    flow = total_demand
    potential = [0] * n  # For reduced cost
    dist = [0] * n
    prev_v = [0] * n
    prev_e = [0] * n

    # Successive shortest path algorithm using Dijkstra’s algorithm with Johnson's potentials.
    while flow > 0:
        dist = [INF] * n
        dist[s] = 0
        queue = []
        heapq.heappush(queue, (0, s))
        while queue:
            d, v = heapq.heappop(queue)
            if dist[v] < d:
                continue
            for i, e in enumerate(graph[v]):
                if e.cap > 0 and dist[e.to] > d + e.cost + potential[v] - potential[e.to]:
                    dist[e.to] = d + e.cost + potential[v] - potential[e.to]
                    prev_v[e.to] = v
                    prev_e[e.to] = i
                    heapq.heappush(queue, (dist[e.to], e.to))
        if dist[t] == INF:
            return -1.0
        for v in range(n):
            if dist[v] < INF:
                potential[v] += dist[v]
        add_flow = flow
        v = t
        while v != s:
            e = graph[prev_v[v]][prev_e[v]]
            if add_flow > e.cap:
                add_flow = e.cap
            v = prev_v[v]
        flow -= add_flow
        result += add_flow * potential[t]
        v = t
        while v != s:
            e = graph[prev_v[v]][prev_e[v]]
            e.cap -= add_flow
            graph[v][e.rev].cap += add_flow
            v = prev_v[v]
    return float(result)