import heapq

class Edge:
    def __init__(self, to, cap, cost, rev):
        self.to = to
        self.cap = cap
        self.cost = cost
        self.rev = rev

class MinCostFlow:
    def __init__(self, N):
        self.N = N
        self.graph = [[] for _ in range(N)]
    
    def add_edge(self, fr, to, cap, cost):
        self.graph[fr].append(Edge(to, cap, cost, len(self.graph[to])))
        self.graph[to].append(Edge(fr, 0, -cost, len(self.graph[fr]) - 1))
    
    def flow(self, s, t, f):
        N = self.N
        prevv = [0] * N
        preve = [0] * N
        INF = 10**18
        res = 0
        h = [0] * N  # potential
        dist = [0] * N
        
        while f > 0:
            dist = [INF] * N
            dist[s] = 0
            queue = []
            heapq.heappush(queue, (0, s))
            while queue:
                d, v = heapq.heappop(queue)
                if dist[v] < d:
                    continue
                for i, e in enumerate(self.graph[v]):
                    if e.cap > 0 and dist[e.to] > d + e.cost + h[v] - h[e.to]:
                        dist[e.to] = d + e.cost + h[v] - h[e.to]
                        prevv[e.to] = v
                        preve[e.to] = i
                        heapq.heappush(queue, (dist[e.to], e.to))
            if dist[t] == INF:
                # Cannot push more flow
                break
            for v in range(N):
                if dist[v] < INF:
                    h[v] += dist[v]
            d = f
            v = t
            while v != s:
                d = min(d, self.graph[prevv[v]][preve[v]].cap)
                v = prevv[v]
            f -= d
            res += d * h[t]
            v = t
            while v != s:
                e = self.graph[prevv[v]][preve[v]]
                e.cap -= d
                self.graph[v][e.rev].cap += d
                v = prevv[v]
        return res

def solve(substations, power_lines, power_demands):
    # Build nodes:
    # We'll use string identifiers for nodes. Later, assign each unique node a unique index.
    nodes = set()
    nodes.add("S")
    nodes.add("T")
    # For each substation, add in and out nodes.
    for v in substations:
        nodes.add(f"v_in_{v}")
        nodes.add(f"v_out_{v}")
    # For each demand, create unique nodes.
    num_demands = len(power_demands)
    for i in range(num_demands):
        nodes.add(f"ds_{i}")
        nodes.add(f"dt_{i}")
    # For power lines, nodes already exist via substations.
    
    # Create mapping from node name to index
    node2idx = {}
    idx = 0
    for node in nodes:
        node2idx[node] = idx
        idx += 1
    N = idx  # total number of nodes
    
    mcf = MinCostFlow(N)
    
    # Add substation internal capacity edges: from v_in to v_out with available capacity = capacity - current_load (if positive)
    for v, data in substations.items():
        available = data['capacity'] - data['current_load']
        if available < 0:
            available = 0
        mcf.add_edge(node2idx[f"v_in_{v}"], node2idx[f"v_out_{v}"], available, 0)
    
    # Add power line edges: from u_out to v_in, with given capacity and cost.
    for u, v, cap, cost in power_lines:
        mcf.add_edge(node2idx[f"v_out_{u}"], node2idx[f"v_in_{v}"], cap, cost)
    
    # Record mapping for each demand edge from ds_i to v_in_{s} to retrieve delivered flow later.
    demand_edges = []
    
    total_request = 0
    # For each demand, add branch nodes:
    for i, (s, t, req) in enumerate(power_demands):
        total_request += req
        # From S to ds_i edge
        mcf.add_edge(node2idx["S"], node2idx[f"ds_{i}"], req, 0)
        # From ds_i to source substation in-node
        # Save this edge index to track delivered flow.
        start_idx = len(mcf.graph[node2idx[f"ds_{i}"]])
        mcf.add_edge(node2idx[f"ds_{i}"], node2idx[f"v_in_{s}"], req, 0)
        # The edge we just added is the last edge on ds_i's list.
        demand_edges.append((f"ds_{i}", start_idx))
        # From destination substation out-node to dt_i
        mcf.add_edge(node2idx[f"v_out_{t}"], node2idx[f"dt_{i}"], req, 0)
        # From dt_i to T
        mcf.add_edge(node2idx[f"dt_{i}"], node2idx["T"], req, 0)
    
    # Run min cost flow from S to T with desired flow = total_request 
    total_cost = mcf.flow(node2idx["S"], node2idx["T"], total_request)
    
    # Determine fulfilled flow for each demand.
    fulfilled_demands = {}
    for i, (s, t, req) in enumerate(power_demands):
        # The edge from ds_i to v_in_{s} is stored in demand_edges[i]
        ds_node, edge_index = demand_edges[i]
        edge = mcf.graph[node2idx[ds_node]][edge_index]
        # Delivered flow = original capacity (req) - remaining capacity on this edge.
        delivered = req - edge.cap
        fulfilled_demands[(s, t, req)] = delivered
    return total_cost, fulfilled_demands