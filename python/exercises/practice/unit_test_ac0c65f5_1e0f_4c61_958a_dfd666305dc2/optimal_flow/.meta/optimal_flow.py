class Edge:
    def __init__(self, to, cap, rev):
        self.to = to
        self.cap = cap
        self.rev = rev

class OptimalFlowNetwork:
    def __init__(self, N, S, T, edges, statuses):
        self.N = N
        self.S = S
        self.T = T
        # Copy statuses (node_id -> bool) and initialize capacities (u,v -> capacity)
        self.statuses = statuses.copy()
        self.capacities = {}
        for u, v, cap in edges:
            self.capacities[(u, v)] = cap

    def update_node(self, node, status):
        # Update the online/offline status of the node.
        self.statuses[node] = status

    def update_capacity(self, u, v, capacity):
        # Update or add the capacity for the edge (u, v)
        self.capacities[(u, v)] = capacity

    def query_flow(self):
        # Build the graph based on current statuses and capacities.
        n = self.N
        graph = [[] for _ in range(n + 1)]  # 1-indexed nodes.
        for (u, v), cap in self.capacities.items():
            if self.statuses.get(u, False) and self.statuses.get(v, False):
                if cap > 0:
                    self._add_edge(graph, u, v, cap)
        return self._dinic_max_flow(graph, self.S, self.T, n)

    def _add_edge(self, graph, fr, to, cap):
        # Add forward edge and a reverse edge for residual capacity.
        graph[fr].append(Edge(to, cap, len(graph[to])))
        graph[to].append(Edge(fr, 0, len(graph[fr]) - 1))

    def _bfs(self, graph, s, t, level, n):
        for i in range(n + 1):
            level[i] = -1
        queue = []
        level[s] = 0
        queue.append(s)
        while queue:
            v = queue.pop(0)
            for e in graph[v]:
                if e.cap > 0 and level[e.to] < 0:
                    level[e.to] = level[v] + 1
                    queue.append(e.to)
        return level[t] != -1

    def _dfs(self, graph, v, t, upTo, it, level):
        if v == t:
            return upTo
        for i in range(it[v], len(graph[v])):
            it[v] = i
            e = graph[v][i]
            if e.cap > 0 and level[v] + 1 == level[e.to]:
                d = self._dfs(graph, e.to, t, min(upTo, e.cap), it, level)
                if d > 0:
                    e.cap -= d
                    graph[e.to][e.rev].cap += d
                    return d
        return 0

    def _dinic_max_flow(self, graph, s, t, n):
        flow = 0
        level = [-1] * (n + 1)
        while self._bfs(graph, s, t, level, n):
            it = [0] * (n + 1)
            while True:
                pushed = self._dfs(graph, s, t, float('inf'), it, level)
                if pushed <= 0:
                    break
                flow += pushed
        return flow

if __name__ == '__main__':
    # Example usage:
    # Initialize network with 4 nodes, S=1, T=4.
    # Edges: (1,2)=5, (1,3)=10, (2,4)=5, (3,4)=10.
    N = 4
    S = 1
    T = 4
    edges = [
        (1, 2, 5),
        (1, 3, 10),
        (2, 4, 5),
        (3, 4, 10)
    ]
    statuses = {1: True, 2: True, 3: True, 4: True}
    network = OptimalFlowNetwork(N, S, T, edges, statuses)
    print("Max Flow:", network.query_flow())