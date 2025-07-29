import math
from collections import deque

class MinCostFlow:
    def __init__(self, n):
        self.n = n
        self.graph = [[] for _ in range(n)]
    
    def add_edge(self, fr, to, cap, cost):
        forward = [to, cap, cost, len(self.graph[to])]
        backward = [fr, 0, -cost, len(self.graph[fr])]
        self.graph[fr].append(forward)
        self.graph[to].append(backward)
    
    def flow(self, s, t, f):
        n = self.n
        prevv = [0] * n
        preve = [0] * n
        INF = 10**9
        res = 0
        h = [0] * n  # potential
        
        while f > 0:
            dist = [INF] * n
            dist[s] = 0
            inqueue = [False] * n
            queue = deque()
            queue.append(s)
            while queue:
                v = queue.popleft()
                inqueue[v] = False
                for i, (to, cap, cost, rev) in enumerate(self.graph[v]):
                    if cap > 0 and dist[to] > dist[v] + cost + h[v] - h[to]:
                        dist[to] = dist[v] + cost + h[v] - h[to]
                        prevv[to] = v
                        preve[to] = i
                        if not inqueue[to]:
                            queue.append(to)
                            inqueue[to] = True
            if dist[t] == INF:
                return None  # cannot flow full f
            for v in range(n):
                h[v] += dist[v]
            d = f
            v = t
            while v != s:
                d = min(d, self.graph[prevv[v]][preve[v]][1])
                v = prevv[v]
            f -= d
            res += d * h[t]
            v = t
            while v != s:
                edge = self.graph[prevv[v]][preve[v]]
                edge[1] -= d
                self.graph[v][edge[3]][1] += d
                v = prevv[v]
        return res

def find_optimal_flow(n, capacities, rates, edges, node_information_request):
    # Pre-check: For nodes with consumption, if demand exceeds capacity, then infeasible.
    for i in range(n):
        if rates[i] < 0 and (-rates[i] > capacities[i]):
            return {}

    # Build min cost flow network
    # We'll create nodes: super source = n, super sink = n+1, total nodes = n+2
    total_nodes = n + 2
    source = n
    sink = n + 1
    mcf = MinCostFlow(total_nodes)
    
    # total production required
    total_production = 0
    # For each node, if production exists, add an edge from source to node.
    # If consumption exists, add an edge from node to sink.
    for i in range(n):
        if rates[i] > 0:
            mcf.add_edge(source, i, rates[i], 0)
            total_production += rates[i]
        elif rates[i] < 0:
            mcf.add_edge(i, sink, -rates[i], 0)
    
    # For each original edge, add edge with high capacity bound.
    # We'll record positions to retrieve flows later.
    original_edge_refs = []
    # Using a large capacity value to simulate infinity for the edge.
    large_cap = total_production  
    for (u, v, cost) in edges:
        # Get additional information from a node if needed (simulate decentralized request)
        # But here, we assume that node_information_request works and data is consistent.
        # Use capacity from production sum as maximum possible flow.
        mcf.add_edge(u, v, large_cap, cost)
        # Record the edge's current state: reference is (u, index in mcf.graph[u], tuple key)
        index = len(mcf.graph[u]) - 1
        # Store a tuple (u, v, cost, index) to extract flow later.
        original_edge_refs.append((u, v, cost, index))
    
    # Compute min cost flow from source to sink
    min_cost = mcf.flow(source, sink, total_production)
    if min_cost is None:
        return {}
    
    # Build the flow dict from the original edges.
    flow_dict = {}
    for (u, v, cost, index) in original_edge_refs:
        # The edge at mcf.graph[u][index] originally had capacity = large_cap.
        # The flow is (original capacity - remaining capacity).
        edge_flow = large_cap - mcf.graph[u][index][1]
        flow_dict[(u, v, cost)] = edge_flow
    return flow_dict