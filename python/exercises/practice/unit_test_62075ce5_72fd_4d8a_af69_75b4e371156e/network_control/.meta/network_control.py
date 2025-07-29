class Edge:
    def __init__(self, to, capacity):
        self.to = to
        self.capacity = capacity
        self.flow = 0
        self.orig_cap = capacity
        self.rev = None

class Dinic:
    def __init__(self, n):
        self.n = n
        self.graph = [[] for _ in range(n)]
        
    def add_edge(self, fr, to, cap):
        forward = Edge(to, cap)
        backward = Edge(fr, 0)
        forward.rev = backward
        backward.rev = forward
        self.graph[fr].append(forward)
        self.graph[to].append(backward)
        # Return the forward edge so that caller can track original edges if necessary.
        return forward

    def bfs(self, s, t, level):
        for i in range(len(level)):
            level[i] = -1
        queue = []
        level[s] = 0
        queue.append(s)
        while queue:
            v = queue.pop(0)
            for e in self.graph[v]:
                if level[e.to] < 0 and e.flow < e.capacity:
                    level[e.to] = level[v] + 1
                    queue.append(e.to)
        return level[t] >= 0

    def dfs(self, v, t, upTo, level, it):
        if v == t:
            return upTo
        for i in range(it[v], len(self.graph[v])):
            e = self.graph[v][i]
            if e.capacity > e.flow and level[v] + 1 == level[e.to]:
                ret = self.dfs(e.to, t, min(upTo, e.capacity - e.flow), level, it)
                if ret > 0:
                    e.flow += ret
                    e.rev.flow -= ret
                    return ret
            it[v] += 1
        return 0

    def max_flow(self, s, t):
        flow = 0
        level = [-1] * self.n
        while self.bfs(s, t, level):
            it = [0] * self.n
            while True:
                pushed = self.dfs(s, t, float('inf'), level, it)
                if pushed <= 0:
                    break
                flow += pushed
        return flow

def simulate_network_control(n, m, edges, T, A, B, R_min, R_max, time_steps):
    result = []
    sending_rate = 1.0  # starting sending rate
    # We'll record the original edge references from input for congestion monitoring.
    # We consider each simulation step separately, building the graph fresh.
    for _ in range(time_steps):
        # Record current sending rate (rounded to 6 decimal places).
        result.append(round(sending_rate, 6))
        # Build the flow network.
        # Total nodes: original nodes (0 to n-1) plus extra super source node (index n).
        total_nodes = n + 1
        dinic = Dinic(total_nodes)
        # Add edge from super source (n) to source (0) with capacity = sending_rate.
        dinic.add_edge(n, 0, sending_rate)
        # List to hold references for each original edge added.
        orig_edges = []
        for (u, v, cap) in edges:
            edge_ref = dinic.add_edge(u, v, cap)
            orig_edges.append(edge_ref)
        # Compute max flow from super source to destination (n-1).
        flow = dinic.max_flow(n, n-1)
        # Determine if congestion occurs.
        congested = False
        # For each original edge, check its utilization.
        for edge in orig_edges:
            utilization = edge.flow / edge.orig_cap if edge.orig_cap > 0 else 0
            if utilization > T:
                congested = True
                break
        # Rate adjustment:
        if congested:
            sending_rate = max(R_min, sending_rate * B)
        else:
            sending_rate = min(R_max, sending_rate + A)
    return result