import heapq

class Edge:
    def __init__(self, to, rev, capacity, cost, init_capacity, original):
        self.to = to
        self.rev = rev
        self.capacity = capacity
        self.cost = cost
        self.init_capacity = init_capacity
        self.original = original

class MinCostMaxFlow:
    def __init__(self, N):
        self.N = N
        self.graph = [[] for _ in range(N)]
    
    def add_edge(self, fr, to, capacity, cost, original):
        forward = Edge(to, len(self.graph[to]), capacity, cost, capacity, original)
        backward = Edge(fr, len(self.graph[fr]), 0, -cost, 0, False)
        self.graph[fr].append(forward)
        self.graph[to].append(backward)
    
    def flow(self, s, t, max_flow):
        N = self.N
        prevv = [0] * N
        preve = [0] * N
        INF = 10**9
        res = 0
        h = [0] * N  # potential
        dist = [0] * N
        flow = 0
        while flow < max_flow:
            dist = [INF] * N
            dist[s] = 0
            queue = [(0, s)]
            while queue:
                d, v = heapq.heappop(queue)
                if dist[v] < d:
                    continue
                for i, e in enumerate(self.graph[v]):
                    if e.capacity > 0 and dist[e.to] > d + e.cost + h[v] - h[e.to]:
                        dist[e.to] = d + e.cost + h[v] - h[e.to]
                        prevv[e.to] = v
                        preve[e.to] = i
                        heapq.heappush(queue, (dist[e.to], e.to))
            if dist[t] == INF:
                break
            for v in range(N):
                h[v] += dist[v] if dist[v] < INF else 0
            d = max_flow - flow
            v = t
            while v != s:
                d = min(d, self.graph[prevv[v]][preve[v]].capacity)
                v = prevv[v]
            flow += d
            res += d * h[t]
            v = t
            while v != s:
                e = self.graph[prevv[v]][preve[v]]
                e.capacity -= d
                self.graph[v][e.rev].capacity += d
                v = prevv[v]
        return flow, res

def optimal_traffic_flow(N, edges, sources, destinations):
    total_supply = sum(demand for _, demand in sources)
    total_demand = sum(cap for _, cap in destinations)
    if total_supply != total_demand:
        raise ValueError("Total supply and demand do not match")
    total_nodes = N + 2
    S = N
    T = N + 1
    mcmf = MinCostMaxFlow(total_nodes)
    # Add original edges from the city graph.
    # Keep track of these edges to extract flows later.
    original_edge_info = []
    for u, v, capacity, congestion in edges:
        mcmf.add_edge(u, v, capacity, congestion, True)
        original_edge_info.append((u, v))
    # Connect super source to sources.
    for node, demand in sources:
        mcmf.add_edge(S, node, demand, 0, False)
    # Connect destinations to super sink.
    for node, cap in destinations:
        mcmf.add_edge(node, T, cap, 0, False)
    max_flow, min_cost = mcmf.flow(S, T, total_supply)
    if max_flow != total_supply:
        raise ValueError("Could not route all demand from sources to destinations")
    # Extract flows on original edges.
    flow_dict = {}
    for u in range(N):
        for e in mcmf.graph[u]:
            if e.original:
                used_flow = e.init_capacity - e.capacity
                key = (u, e.to)
                if key in flow_dict:
                    flow_dict[key] += used_flow
                else:
                    flow_dict[key] = used_flow
    return flow_dict