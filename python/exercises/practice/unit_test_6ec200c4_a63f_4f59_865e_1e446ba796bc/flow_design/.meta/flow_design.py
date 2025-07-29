import sys
import heapq

INF = 10**9

class Edge:
    __slots__ = ('v', 'cap', 'cost', 'rev')
    def __init__(self, v, cap, cost, rev):
        self.v = v
        self.cap = cap
        self.cost = cost
        self.rev = rev

def add_edge(graph, u, v, cap, cost):
    graph[u].append(Edge(v, cap, cost, len(graph[v])))
    graph[v].append(Edge(u, 0, -cost, len(graph[u]) - 1))

def min_cost_flow(n, graph, s, t, f):
    res = 0
    h = [0] * n  # potentials
    prev_v = [0] * n
    prev_e = [0] * n
    while f > 0:
        dist = [INF] * n
        dist[s] = 0
        pq = [(0, s)]
        while pq:
            d, u = heapq.heappop(pq)
            if dist[u] != d:
                continue
            for i, e in enumerate(graph[u]):
                if e.cap > 0 and dist[e.v] > d + e.cost + h[u] - h[e.v]:
                    dist[e.v] = d + e.cost + h[u] - h[e.v]
                    prev_v[e.v] = u
                    prev_e[e.v] = i
                    heapq.heappush(pq, (dist[e.v], e.v))
        if dist[t] == INF:
            return -1, res  # cannot flow further
        for u in range(n):
            if dist[u] < INF:
                h[u] += dist[u]
        d = f
        u = t
        while u != s:
            d = min(d, graph[prev_v[u]][prev_e[u]].cap)
            u = prev_v[u]
        f -= d
        res += d * h[t]
        u = t
        while u != s:
            e = graph[prev_v[u]][prev_e[u]]
            e.cap -= d
            graph[u][e.rev].cap += d
            u = prev_v[u]
    return 0, res

def process_commodity(n, m, edge_info, global_free, s, t, demand):
    # Build graph with two arcs per original edge:
    #  - free arc: capacity = current global_free[i], cost = 0.
    #  - upgrade arc: capacity = demand, cost = cost from edge_info.
    graph = [[] for _ in range(n)]
    # Store mapping for updating global free capacity.
    mapping = []  # Each element: (u, free_idx, upg_idx, initial_free)
    for i, (u, v, cost_val) in enumerate(edge_info):
        init_free = global_free[i]
        free_idx = len(graph[u])
        add_edge(graph, u, v, init_free, 0)
        upg_idx = len(graph[u])
        add_edge(graph, u, v, demand, cost_val)
        mapping.append((u, free_idx, upg_idx, init_free))
    # Run min cost flow for 'demand' units on this commodity.
    ret, commodity_cost = min_cost_flow(n, graph, s, t, demand)
    if ret == -1:
        return -1, 0, global_free
    # Update global_free for each original edge.
    new_global = list(global_free)
    for i, (u, free_idx, upg_idx, init_free) in enumerate(mapping):
        # In the constructed graph, the free arc is the edge added at index free_idx of node u.
        free_edge = graph[u][free_idx]
        # The upgrade arc is at index upg_idx of node u.
        upg_edge = graph[u][upg_idx]
        used_free = init_free - free_edge.cap  # units used from free capacity
        used_upgrade = demand - upg_edge.cap  # units purchased in this commodity on this edge
        # The new free capacity is what remains from free arc plus new purchased capacity.
        new_global[i] = free_edge.cap + used_upgrade
    return 0, commodity_cost, new_global

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    it = iter(data)
    try:
        n = int(next(it))
        m = int(next(it))
        k = int(next(it))
    except StopIteration:
        return
    # edge_info: list of tuples (u, v, cost)
    edge_info = []
    init_cap = []
    for _ in range(m):
        u = int(next(it))
        v = int(next(it))
        cap = int(next(it))
        cost_val = int(next(it))
        edge_info.append((u, v, cost_val))
        init_cap.append(cap)
    # Global free capacities per edge; initially equals the given capacities.
    global_free = list(init_cap)
    # List of commodities: (s, t, demand)
    commodities = []
    for _ in range(k):
        s = int(next(it))
        t = int(next(it))
        d = int(next(it))
        commodities.append((s, t, d))
    total_cost = 0
    # Process each commodity in the given input order.
    for (s, t, demand) in commodities:
        ret, commodity_cost, global_free = process_commodity(n, m, edge_info, global_free, s, t, demand)
        if ret == -1:
            print(-1)
            return
        total_cost += commodity_cost
    print(total_cost)

if __name__ == '__main__':
    solve()