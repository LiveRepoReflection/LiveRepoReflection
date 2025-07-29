import math
from collections import deque

INF = 10**9

class Edge:
    __slots__ = ['to', 'cap', 'rev']
    def __init__(self, to, cap, rev):
        self.to = to
        self.cap = cap
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
        level = [-1] * self.n
        while self.bfs(s, t, level):
            it = [0] * self.n
            while True:
                pushed = self.dfs(s, t, INF, level, it)
                if pushed <= 0:
                    break
                flow += pushed
        return flow

def min_evacuation_time(N, edges, population, safe_zones):
    total_population = sum(population)
    if total_population == 0:
        return 0

    # Check if total safe zone capacity is enough.
    total_safe_capacity = sum(cap for _, cap in safe_zones)
    if total_safe_capacity < total_population:
        return -1

    # Get maximum travel time from edges for upper bound.
    max_travel_time = 0
    for (_, _, t, _) in edges:
        if t > max_travel_time:
            max_travel_time = t
    # Upper bound: worst-case sequential traversal on the slowest edge.
    upper_bound = max_travel_time + total_population
    lower_bound = 0
    answer = -1

    while lower_bound <= upper_bound:
        mid = (lower_bound + upper_bound) // 2
        if can_evacuate_in_time(N, edges, population, safe_zones, mid, total_population):
            answer = mid
            upper_bound = mid - 1
        else:
            lower_bound = mid + 1
    return answer

def can_evacuate_in_time(N, edges, population, safe_zones, T, total_population):
    # Build time-expanded network.
    # Each node (i, t) where i in [0,N-1] and t in [0, T]
    # Node id for (i, t) = i * (T+1) + t
    layered_nodes = N * (T + 1)
    
    # For safe zone aggregation, assign one node per safe zone.
    safe_zone_count = len(safe_zones)
    safe_zone_offset = layered_nodes
    # Next, source and sink nodes.
    source = safe_zone_offset + safe_zone_count
    sink = source + 1
    total_nodes = sink + 1

    mf = Dinic(total_nodes)

    # Add edge from source to each (i, 0) with capacity equal to population[i].
    for i in range(N):
        if population[i] > 0:
            node_id = i * (T + 1)  # time 0 copy
            mf.add_edge(source, node_id, population[i])
    
    # Add waiting edges for each node: (i, t) -> (i, t+1) with INF capacity.
    for i in range(N):
        for t in range(T):
            u = i * (T + 1) + t
            v = i * (T + 1) + (t + 1)
            mf.add_edge(u, v, INF)
    
    # Add travel edges for each road.
    # For each edge (u, v, travel_time, road_cap):
    # For every time t such that t + travel_time <= T, add edge from (u, t) to (v, t + travel_time) with capacity = road_cap.
    for (u, v, travel_time, road_cap) in edges:
        if travel_time > T:
            continue
        for t in range(T - travel_time + 1):
            u_time = u * (T + 1) + t
            v_time = v * (T + 1) + (t + travel_time)
            mf.add_edge(u_time, v_time, road_cap)
    
    # For safe zones, for each safe zone (loc, cap), 
    # create edges from every time copy of the safe zone node to its aggregator with INF capacity.
    for idx, (loc, sz_cap) in enumerate(safe_zones):
        safe_agg_node = safe_zone_offset + idx
        for t in range(T + 1):
            node_id = loc * (T + 1) + t
            mf.add_edge(node_id, safe_agg_node, INF)
        # Add edge from aggregator to sink with capacity = safe zone capacity.
        mf.add_edge(safe_agg_node, sink, sz_cap)
    
    flow = mf.max_flow(source, sink)
    return flow >= total_population