import heapq
from collections import defaultdict

class NetworkRouting:
    def __init__(self, N):
        self.N = N
        self.graph = defaultdict(dict)
        self.distance = [[float('inf')] * N for _ in range(N)]
        for i in range(N):
            self.distance[i][i] = 0

    def add_edge(self, u, v, cost):
        self.graph[u][v] = cost
        self.graph[v][u] = cost
        self._update_distances(u, v, cost)

    def remove_edge(self, u, v):
        if v in self.graph[u]:
            del self.graph[u][v]
            del self.graph[v][u]
            self._recompute_distances()

    def query(self, start, end):
        if self.distance[start][end] == float('inf'):
            return -1
        return self.distance[start][end]

    def _update_distances(self, u, v, cost):
        old_cost = self.distance[u][v]
        if cost < old_cost:
            self.distance[u][v] = cost
            self.distance[v][u] = cost
            for i in range(self.N):
                for j in range(self.N):
                    if self.distance[i][j] > self.distance[i][u] + cost + self.distance[v][j]:
                        self.distance[i][j] = self.distance[i][u] + cost + self.distance[v][j]
                    if self.distance[i][j] > self.distance[i][v] + cost + self.distance[u][j]:
                        self.distance[i][j] = self.distance[i][v] + cost + self.distance[u][j]

    def _recompute_distances(self):
        self.distance = [[float('inf')] * self.N for _ in range(self.N)]
        for i in range(self.N):
            self.distance[i][i] = 0
        
        for u in self.graph:
            for v in self.graph[u]:
                if self.distance[u][v] > self.graph[u][v]:
                    self.distance[u][v] = self.graph[u][v]
                    self.distance[v][u] = self.graph[u][v]

        for k in range(self.N):
            for i in range(self.N):
                for j in range(self.N):
                    if self.distance[i][j] > self.distance[i][k] + self.distance[k][j]:
                        self.distance[i][j] = self.distance[i][k] + self.distance[k][j]