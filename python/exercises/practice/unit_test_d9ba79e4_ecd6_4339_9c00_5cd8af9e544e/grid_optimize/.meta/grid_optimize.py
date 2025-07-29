import heapq
import math

INF = float('inf')

class MinCostFlow:
    def __init__(self, N):
        self.N = N
        self.graph = [[] for _ in range(N)]
    
    def add_edge(self, fr, to, cap, cost):
        self.graph[fr].append([to, cap, cost, len(self.graph[to])])
        self.graph[to].append([fr, 0, -cost, len(self.graph[fr]) - 1])
    
    def min_cost_flow(self, s, t, f, max_latency, physical_nodes):
        # f: required flow
        # We'll use a modified shortest path search with hop constraint.
        # We store state: (node, hops_used) where hops_used counts physical edge traversals.
        total_cost = 0
        N = self.N

        while f > 0:
            # dist[node][hops] = cost, for hops from 0..max_latency.
            dist = [[INF]*(max_latency+1) for _ in range(N)]
            in_state = [[False]*(max_latency+1) for _ in range(N)]
            prev = [[None]*(max_latency+1) for _ in range(N)]
            # starting state: (s, 0) with cost 0.
            dist[s][0] = 0
            # Priority queue holds tuples: (d, node, hops)
            pq = [(0, s, 0)]
            while pq:
                d, u, hops = heapq.heappop(pq)
                if dist[u][hops] != d:
                    continue
                in_state[u][hops] = True
                # If u is the sink, we can continue as we want the best cost among all hops.
                for i, edge in enumerate(self.graph[u]):
                    v, cap, cost, rev = edge
                    if cap <= 0:
                        continue
                    # Determine new hop count based on edge properties.
                    # If the edge is from s or to t, do not increment hop.
                    new_hops = None
                    if u == s:
                        # Edge from super source: physical edge constraint not counted.
                        new_hops = 0
                    elif v == t:
                        # Edge to super sink: no additional hop.
                        new_hops = hops
                    else:
                        # Both u and v are physical nodes.
                        if u in physical_nodes and v in physical_nodes:
                            if hops < max_latency:
                                new_hops = hops + 1
                        else:
                            new_hops = hops
                    if new_hops is None or new_hops > max_latency:
                        continue
                    nd = d + cost
                    if nd < dist[v][new_hops]:
                        dist[v][new_hops] = nd
                        prev[v][new_hops] = (u, hops, i)  # store predecessor state and edge index
                        heapq.heappush(pq, (nd, v, new_hops))
            
            # Find the best cost state at sink t with any hops <= max_latency.
            best_cost = INF
            best_hops = -1
            for h in range(max_latency+1):
                if dist[t][h] < best_cost:
                    best_cost = dist[t][h]
                    best_hops = h
            if best_cost == INF:
                return -1
            # Determine the maximum flow that can be pushed along the found path.
            d = f
            v = t
            h = best_hops
            path = []
            while v != s:
                u, prev_hops, edge_index = prev[v][h]
                path.append((u, v, edge_index))
                # Update h: if this edge was physical (v != t and u != s), then h = prev_hops, else h stays same.
                if u != s and v != t:
                    h = prev_hops
                else:
                    h = prev_hops  # even if not incremented, restore state
                v = u
            # Reverse to get path from s to t.
            path.reverse()
            # Determine the bottleneck capacity along the path.
            for u, v, ei in path:
                d = min(d, self.graph[u][ei][1])
            f -= d
            total_cost += d * best_cost
            # Update residual capacities along the path.
            for u, v, ei in path:
                self.graph[u][ei][1] -= d
                rev = self.graph[u][ei][3]
                self.graph[v][rev][1] += d
        return total_cost

def optimize_grid(n: int, connections: list, demand: list, max_latency: int) -> int:
    total_positive = sum(x for x in demand if x > 0)
    total_negative = sum(-x for x in demand if x < 0)
    # if no flow is needed, cost is 0.
    if total_positive == 0 and total_negative == 0:
        return 0
    # Construct graph nodes:
    # Physical nodes are 0 to n-1.
    # Let super source be node n and super sink be node n+1.
    S = n
    T = n+1
    V = n + 2
    mcf = MinCostFlow(V)
    
    physical_nodes = set(range(n))  # for hop count purposes

    # Add edges from super source to surplus nodes.
    for i in range(n):
        if demand[i] < 0:
            mcf.add_edge(S, i, -demand[i], 0)
    # Add edges from deficit nodes to super sink.
    for i in range(n):
        if demand[i] > 0:
            mcf.add_edge(i, T, demand[i], 0)
    
    # Add physical edges (bidirectional) for each connection.
    for (u, v, cap, cost) in connections:
        mcf.add_edge(u, v, cap, cost)
        mcf.add_edge(v, u, cap, cost)
    
    # Total flow required: total positive demand (or total surplus)
    required_flow = total_positive
    result = mcf.min_cost_flow(S, T, required_flow, max_latency, physical_nodes)
    return result