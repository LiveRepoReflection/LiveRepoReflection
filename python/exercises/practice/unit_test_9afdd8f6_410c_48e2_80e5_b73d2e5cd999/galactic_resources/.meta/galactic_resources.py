import heapq

INF = 10**9

class MinCostFlow:
    def __init__(self, N):
        self.N = N
        self.graph = [[] for _ in range(N)]

    def add_edge(self, fr, to, cap, cost):
        self.graph[fr].append([to, cap, cost, len(self.graph[to])])
        self.graph[to].append([fr, 0, -cost, len(self.graph[fr]) - 1])

    def min_cost_flow(self, s, t, f):
        N = self.N
        prev_v = [0] * N
        prev_e = [0] * N
        dist = [0] * N
        res = 0
        h = [0] * N  # potential
        while f > 0:
            dist = [INF] * N
            dist[s] = 0
            queue = [(0, s)]
            while queue:
                d, v = heapq.heappop(queue)
                if dist[v] < d:
                    continue
                for i, e in enumerate(self.graph[v]):
                    to, cap, cost, _ = e
                    if cap > 0 and dist[to] > d + cost + h[v] - h[to]:
                        dist[to] = d + cost + h[v] - h[to]
                        prev_v[to] = v
                        prev_e[to] = i
                        heapq.heappush(queue, (dist[to], to))
            if dist[t] == INF:
                return -1
            for v in range(N):
                if dist[v] < INF:
                    h[v] += dist[v]
            d = f
            v = t
            while v != s:
                d = min(d, self.graph[prev_v[v]][prev_e[v]][1])
                v = prev_v[v]
            f -= d
            res += d * h[t]
            v = t
            while v != s:
                e = self.graph[prev_v[v]][prev_e[v]]
                e[1] -= d
                self.graph[v][e[3]][1] += d
                v = prev_v[v]
        return res

def min_transportation_cost(N, M, demand, cost):
    total_cost = 0
    for j in range(M):
        supply = [ -demand[i][j] for i in range(N) ]
        total_supply = sum(x for x in supply if x > 0)
        V = N + 2
        S = N
        T = N + 1
        mcf = MinCostFlow(V)
        for i in range(N):
            if supply[i] > 0:
                mcf.add_edge(S, i, supply[i], 0)
            elif supply[i] < 0:
                mcf.add_edge(i, T, -supply[i], 0)
        for u in range(N):
            for v in range(N):
                if cost[u][v][j] != -1:
                    mcf.add_edge(u, v, total_supply, cost[u][v][j])
        flow_cost = mcf.min_cost_flow(S, T, total_supply)
        if flow_cost == -1:
            return -1
        total_cost += flow_cost
    return total_cost