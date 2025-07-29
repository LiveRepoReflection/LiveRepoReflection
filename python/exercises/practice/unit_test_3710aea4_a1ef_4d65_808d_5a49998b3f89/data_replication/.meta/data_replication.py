import heapq

INF = 10**18

class MinCostFlow:
    def __init__(self, N):
        self.N = N
        self.graph = [[] for _ in range(N)]
    
    def add_edge(self, fr, to, cap, cost):
        self.graph[fr].append([to, cap, cost, len(self.graph[to])])
        self.graph[to].append([fr, 0, -cost, len(self.graph[fr])])
    
    def flow(self, s, t, f):
        N = self.N
        res = 0
        h = [0] * N
        prevv = [0] * N
        preve = [0] * N
        
        while f:
            dist = [INF] * N
            dist[s] = 0
            queue = [(0, s)]
            while queue:
                d, v = heapq.heappop(queue)
                if dist[v] < d:
                    continue
                for i, (to, cap, cost, rev) in enumerate(self.graph[v]):
                    if cap > 0 and dist[to] > d + cost + h[v] - h[to]:
                        dist[to] = d + cost + h[v] - h[to]
                        prevv[to] = v
                        preve[to] = i
                        heapq.heappush(queue, (dist[to], to))
            if dist[t] == INF:
                return -1
            for v in range(N):
                h[v] += dist[v] if dist[v] < INF else 0
            d = f
            v = t
            while v != s:
                d = min(d, self.graph[prevv[v]][preve[v]][1])
                v = prevv[v]
            f -= d
            res += d * h[t]
            v = t
            while v != s:
                e = self.graph[prevv[v]][preve[v]]
                e[1] -= d
                self.graph[v][e[3]][1] += d
                v = prevv[v]
        return res

def replicate_data(N, M, K, capacity, initial_locations, cost):
    # Compute available capacity for each data center (each DC already has some data objects).
    available = [capacity[i] for i in range(N)]
    # Count number of objects initially in each data center.
    for i in range(N):
        for j in range(M):
            if initial_locations[j] & (1 << i):
                available[i] -= 1

    # For each object j, determine how many replications needed.
    needed = [max(0, K - bin(initial_locations[j]).count("1")) for j in range(M)]
    total_needed = sum(needed)
    if total_needed == 0:
        return 0

    # Check if sufficient total available capacity exists.
    if sum(available) < total_needed:
        return -1

    # Build bipartite graph using min cost flow:
    # Source node (s), then M object nodes, then N data center nodes, then sink node (t).
    num_nodes = 2 + M + N
    s = 0
    t = num_nodes - 1
    mcf = MinCostFlow(num_nodes)

    # Adding edges from source to each object node.
    for j in range(M):
        if needed[j] > 0:
            mcf.add_edge(s, 1 + j, needed[j], 0)

    # Adding edges from each object node to each data center if that data center does NOT already have the object.
    for j in range(M):
        for i in range(N):
            if not (initial_locations[j] & (1 << i)):
                mcf.add_edge(1 + j, 1 + M + i, 1, cost[i][j])

    # Adding edges from each data center node to sink.
    for i in range(N):
        if available[i] > 0:
            mcf.add_edge(1 + M + i, t, available[i], 0)

    result = mcf.flow(s, t, total_needed)
    return result