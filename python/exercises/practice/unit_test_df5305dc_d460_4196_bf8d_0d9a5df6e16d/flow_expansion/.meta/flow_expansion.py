import heapq

INF = 10**9

class Edge:
    def __init__(self, to, capacity, cost, rev):
        self.to = to
        self.capacity = capacity
        self.cost = cost
        self.rev = rev

class MinCostFlow:
    def __init__(self, N):
        self.N = N
        self.graph = [[] for _ in range(N)]
    
    def add_edge(self, fr, to, capacity, cost):
        forward = Edge(to, capacity, cost, len(self.graph[to]))
        backward = Edge(fr, 0, -cost, len(self.graph[fr]))
        self.graph[fr].append(forward)
        self.graph[to].append(backward)
    
    def flow(self, s, t, f):
        N = self.N
        res = 0
        dist = [0] * N
        potential = [0] * N
        prev_v = [0] * N
        prev_e = [0] * N
        
        while f > 0:
            dist = [INF] * N
            dist[s] = 0
            queue = [(0, s)]
            while queue:
                d, v = heapq.heappop(queue)
                if dist[v] < d:
                    continue
                for i, e in enumerate(self.graph[v]):
                    if e.capacity > 0 and dist[e.to] > d + e.cost + potential[v] - potential[e.to]:
                        dist[e.to] = d + e.cost + potential[v] - potential[e.to]
                        prev_v[e.to] = v
                        prev_e[e.to] = i
                        heapq.heappush(queue, (dist[e.to], e.to))
            if dist[t] == INF:
                return -1
            for v in range(N):
                if dist[v] < INF:
                    potential[v] += dist[v]
            add_flow = f
            v = t
            while v != s:
                add_flow = min(add_flow, self.graph[prev_v[v]][prev_e[v]].capacity)
                v = prev_v[v]
            f -= add_flow
            res += add_flow * potential[t]
            v = t
            while v != s:
                e = self.graph[prev_v[v]][prev_e[v]]
                e.capacity -= add_flow
                self.graph[v][e.rev].capacity += add_flow
                v = prev_v[v]
        return res

def minimum_cost_expansion(n, edges, commodities, cost_func):
    # Create a graph for min cost flow
    # We add two extra nodes: super source (S) and super sink (T)
    S = n
    T = n + 1
    total_nodes = n + 2
    mcf = MinCostFlow(total_nodes)
    
    # Calculate total demanded flow
    total_demand = 0
    for src, dst, demand in commodities:
        total_demand += demand
    
    # For each edge in the original graph, add two edges:
    # 1. Free capacity up to initial_capacity, cost = 0
    # 2. Expandable capacity up to total_demand (or more), cost = cost(u,v)
    for u, v, init_cap in edges:
        # Free edge with cost 0
        mcf.add_edge(u, v, init_cap, 0)
        # Expansion edge: capacity up to total_demand and cost per unit expansion
        mcf.add_edge(u, v, total_demand, cost_func(u, v))
    
    # For each commodity, add an edge from super source S -> commodity source with capacity = demand, cost = 0
    # and add an edge from commodity sink -> super sink T with capacity = demand, cost = 0.
    for src, dst, demand in commodities:
        mcf.add_edge(S, src, demand, 0)
        mcf.add_edge(dst, T, demand, 0)
    
    # Run the min cost flow from S to T to push total_demand units.
    result = mcf.flow(S, T, total_demand)
    return result