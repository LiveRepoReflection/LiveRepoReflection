from collections import deque
import math

class Edge:
    __slots__ = ['to', 'rev', 'cap']
    def __init__(self, to, rev, cap):
        self.to = to
        self.rev = rev
        self.cap = cap

class Dinic:
    def __init__(self, n):
        self.n = n
        self.graph = [[] for _ in range(n)]
    
    def add_edge(self, fr, to, cap):
        forward = Edge(to, len(self.graph[to]), cap)
        backward = Edge(fr, len(self.graph[fr]), 0)
        self.graph[fr].append(forward)
        self.graph[to].append(backward)
    
    def bfs(self, s, t, level):
        for i in range(len(level)):
            level[i] = -1
        queue = deque()
        level[s] = 0
        queue.append(s)
        while queue:
            v = queue.popleft()
            for edge in self.graph[v]:
                if edge.cap > 0 and level[edge.to] < 0:
                    level[edge.to] = level[v] + 1
                    queue.append(edge.to)
        return level[t] != -1

    def dfs(self, v, t, upTo, level, it):
        if v == t:
            return upTo
        for i in range(it[v], len(self.graph[v])):
            it[v] = i
            edge = self.graph[v][i]
            if edge.cap > 0 and level[v] + 1 == level[edge.to]:
                d = self.dfs(edge.to, t, min(upTo, edge.cap), level, it)
                if d > 0:
                    edge.cap -= d
                    self.graph[edge.to][edge.rev].cap += d
                    return d
        return 0

    def max_flow(self, s, t):
        flow = 0
        level = [-1]*self.n
        while self.bfs(s, t, level):
            it = [0]*self.n
            while True:
                pushed = self.dfs(s, t, math.inf, level, it)
                if pushed == 0:
                    break
                flow += pushed
        return flow

def maximize_stream_satisfaction(N, M, edges, p, K, streams):
    # Aggregate demands per source and sink
    demand_source = [0] * N
    demand_sink = [0] * N
    total_demand = 0
    for s, t, d in streams:
        demand_source[s] += d
        demand_sink[t] += d
        total_demand += d

    # Function to build the flow network for a given fraction f and compute max flow.
    def feasible(f):
        # Create graph.
        # Node splitting: For original node i, i_in = i, i_out = i + N.
        # Total nodes: 2*N + 2 (for super source and sink).
        node_count = 2 * N + 2
        super_source = 2 * N
        super_sink = 2 * N + 1
        dinic = Dinic(node_count)

        # Add node capacity edge for each node: from i_in to i_out with capacity p[i].
        for i in range(N):
            dinic.add_edge(i, i + N, p[i])
        
        # Add original edges: from u_out to v_in with capacity c.
        for u, v, cap in edges:
            dinic.add_edge(u + N, v, cap)

        # Connect super source to source nodes (i_in) with capacity = f * total demand from that node.
        for i in range(N):
            if demand_source[i] > 0:
                dinic.add_edge(super_source, i, f * demand_source[i])
        
        # Connect sink nodes (i_out) to super sink with capacity = f * total demand for that node.
        for i in range(N):
            if demand_sink[i] > 0:
                dinic.add_edge(i + N, super_sink, f * demand_sink[i])
        
        # Calculate maximum flow.
        flow = dinic.max_flow(super_source, super_sink)
        return flow >= f * total_demand

    # Binary search for maximum feasible fraction
    lo = 0.0
    hi = 1.0
    # We'll run binary search until the difference is less than 1e-3 (ensuring 2-decimal precision)
    for _ in range(40):
        mid = (lo + hi) / 2.0
        if feasible(mid):
            lo = mid
        else:
            hi = mid
    result_percentage = round(lo * 100, 2)
    return result_percentage

if __name__ == '__main__':
    # Example usage (can be removed or commented out when using unit tests)
    N = 4
    M = 4
    edges = [(0, 1, 5), (1, 3, 5), (0, 2, 5), (2, 3, 5)]
    p = [10, 5, 5, 10]
    K = 2
    streams = [(0, 3, 5), (0, 3, 10)]
    print(maximize_stream_satisfaction(N, M, edges, p, K, streams))