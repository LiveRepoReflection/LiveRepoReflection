import heapq
import itertools

def optimal_network_deployment(n, edges, building_data, max_latency, total_budget):
    # Build graph as adjacency list.
    graph = {i: [] for i in range(n)}
    edge_dict = {}
    for u, v, weight, bandwidth_limit in edges:
        graph[u].append((v, weight))
        graph[v].append((u, weight))
        key = (min(u, v), max(u, v))
        # Assume no duplicate edges; if duplicates, take the maximum bandwidth limit available.
        if key in edge_dict:
            # if duplicate, choose the one with higher bandwidth limit if weight is same,
            # or choose the one with lower weight if bandwidth is same.
            prev_weight, prev_bw = edge_dict[key]
            if weight < prev_weight or (weight == prev_weight and bandwidth_limit > prev_bw):
                edge_dict[key] = (weight, bandwidth_limit)
        else:
            edge_dict[key] = (weight, bandwidth_limit)

    # Helper: Check feasibility for a given set of server indices.
    def is_feasible(servers):
        # Multi-source Dijkstra to compute shortest paths and record predecessor.
        dist = [float('inf')] * n
        pred = [None] * n
        visited = [False] * n
        heap = []
        for s in servers:
            dist[s] = 0
            heapq.heappush(heap, (0, s, None))  # (distance, node, predecessor)
        while heap:
            d, u, p = heapq.heappop(heap)
            if visited[u]:
                continue
            visited[u] = True
            pred[u] = p
            for v, w in graph[u]:
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    heapq.heappush(heap, (nd, v, u))
                # Tie-break: if distances are equal, prefer smaller predecessor id (for consistency)
                elif nd == dist[v] and p is not None and (pred[v] is None or p < pred[v]):
                    heapq.heappush(heap, (nd, v, p))
        # Check latency constraint: every building must be within max_latency.
        for i in range(n):
            if dist[i] > max_latency:
                return False

        # Compute load on each edge used in the shortest path tree.
        # For each node (except if it is a server), walk backwards using pred until a server is reached.
        edge_load = {}
        for node in range(n):
            if node in servers:
                continue  # server nodes do not add load on any edge.
            load = building_data[node][0]  # processing_requirement
            cur = node
            # Walk back until reaching a server.
            while cur not in servers:
                parent = pred[cur]
                if parent is None:
                    # disconnected (should not happen because of latency check)
                    break
                key = (min(cur, parent), max(cur, parent))
                edge_load[key] = edge_load.get(key, 0) + load
                cur = parent
        
        # Now check each edge load against its bandwidth capacity.
        for key, total_load in edge_load.items():
            if key not in edge_dict:
                # This should not happen since tree path edges must be in graph.
                return False
            _, bandwidth_limit = edge_dict[key]
            if total_load > bandwidth_limit:
                return False
        return True

    # We need to select a subset of nodes as servers.
    # We want to minimize the number of servers. For each possible k, try all combinations.
    # Since n can be as high as 100, full enumeration is not tractable in worst-case.
    # However, given the intended usage and constraints (e.g. low number of servers are expected),
    # we try combinations for k = 1 up to n.
    # We also prune based on budget upfront.
    nodes = list(range(n))
    best = -1
    for k in range(1, n + 1):
        # Generate all combinations of k servers.
        found = False
        for subset in itertools.combinations(nodes, k):
            total_cost = sum(building_data[i][1] for i in subset)
            if total_cost > total_budget:
                continue
            if is_feasible(set(subset)):
                best = k
                found = True
                break
        if found:
            return best
    return -1

if __name__ == '__main__':
    # Sample simple test run
    # For example, a single building test:
    n = 1
    edges = []
    building_data = [(10, 100)]
    max_latency = 50
    total_budget = 1000
    print(optimal_network_deployment(n, edges, building_data, max_latency, total_budget))