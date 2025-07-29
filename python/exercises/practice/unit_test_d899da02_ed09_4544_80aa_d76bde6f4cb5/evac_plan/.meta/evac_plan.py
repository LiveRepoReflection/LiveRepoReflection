from collections import deque

class Edge:
    def __init__(self, to, capacity, rev):
        self.to = to
        self.capacity = capacity
        self.rev = rev

class Dinic:
    def __init__(self, n):
        self.n = n
        self.graph = [[] for _ in range(n)]
    
    def add_edge(self, fr, to, cap):
        forward = Edge(to, cap, len(self.graph[to]))
        backward = Edge(fr, 0, len(self.graph[fr]))
        self.graph[fr].append(forward)
        self.graph[to].append(backward)
    
    def bfs(self, s, t, level):
        for i in range(len(level)):
            level[i] = -1
        q = deque()
        level[s] = 0
        q.append(s)
        while q:
            v = q.popleft()
            for e in self.graph[v]:
                if e.capacity > 0 and level[e.to] < 0:
                    level[e.to] = level[v] + 1
                    q.append(e.to)
        return level[t] != -1
    
    def dfs(self, v, t, upTo, iter, level):
        if v == t:
            return upTo
        for i in range(iter[v], len(self.graph[v])):
            e = self.graph[v][i]
            if e.capacity > 0 and level[v] + 1 == level[e.to]:
                d = self.dfs(e.to, t, min(upTo, e.capacity), iter, level)
                if d > 0:
                    e.capacity -= d
                    self.graph[e.to][e.rev].capacity += d
                    return d
            iter[v] += 1
        return 0
    
    def max_flow(self, s, t):
        flow = 0
        level = [-1]*self.n
        INF = 10**9
        while self.bfs(s, t, level):
            iter = [0]*self.n
            while True:
                f = self.dfs(s, t, INF, iter, level)
                if f == 0:
                    break
                flow += f
        return flow

def evacuate(N, M, K, E, EvacuationPoints, C):
    # Total number of employees in the building.
    total_employees = sum(sum(row) for row in E)
    # Office count - each office in grid arranged in row-major order.
    office_count = N * M
    # Determine maximum possible time possible: worst case from top floor and farthest column.
    max_time = (N - 1) + (M - 1)
    left, right = 0, max_time
    ans = -1

    # Function to check if a given time T is feasible.
    def is_feasible(T):
        # Build flow network.
        # Node numbering:
        # source = 0
        # office nodes: 1 to office_count
        # evacuation point nodes: office_count + 1 to office_count + K
        # sink = office_count + K + 1
        node_count = 1 + office_count + K + 1
        source = 0
        sink = node_count - 1
        dinic = Dinic(node_count)
        # Add edges from source to each office node.
        # Office nodes index mapping: for floor i (0-indexed) and office j (0-indexed), node index = i * M + j + 1.
        for i in range(N):
            for j in range(M):
                office_node = i * M + j + 1
                dinic.add_edge(source, office_node, E[i][j])
        # For each office, add edges to evacuation points if reachable within time T.
        # Cost from office at floor (i+1) and office (j+1) to evacuation point at column evac (1-indexed):
        # cost = i + abs((j+1) - evac)
        for i in range(N):
            for j in range(M):
                office_node = i * M + j + 1
                for k in range(K):
                    evac_col = EvacuationPoints[k]
                    cost = i + abs((j + 1) - evac_col)
                    if cost <= T:
                        evac_node = office_count + k + 1
                        # Use capacity equal to number of employees at the office.
                        dinic.add_edge(office_node, evac_node, E[i][j])
        # Add edges from evacuation points to sink with capacity C.
        for k in range(K):
            evac_node = office_count + k + 1
            dinic.add_edge(evac_node, sink, C[k])
        maxflow = dinic.max_flow(source, sink)
        return maxflow == total_employees

    # Binary search for minimal T feasible.
    result = right
    while left <= right:
        mid = (left + right) // 2
        if is_feasible(mid):
            result = mid
            right = mid - 1
        else:
            left = mid + 1
    return result