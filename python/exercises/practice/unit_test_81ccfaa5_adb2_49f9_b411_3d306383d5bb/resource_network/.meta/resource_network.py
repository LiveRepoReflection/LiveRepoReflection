import math
import heapq

def resource_network(n, needs, production, trade_routes, C):
    INF = 10**9

    # Compute all-pairs shortest path using Floyd-Warshall
    dist = [[INF] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u, v, cost in trade_routes:
        if cost < dist[u][v]:
            dist[u][v] = cost
            dist[v][u] = cost
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    # Min-Cost Flow for one resource type (treated as separate flow networks)
    def min_cost_for_resource(surpluses, deficits):
        # Build donor and receiver lists from planet indexes
        donors = []
        receivers = []
        for i in range(n):
            if surpluses[i] > 0:
                donors.append((i, surpluses[i]))
            if deficits[i] > 0:
                receivers.append((i, deficits[i]))
        total_required = sum(d for _, d in receivers)
        # Graph construction:
        # Nodes: source, donors, receivers, sink.
        # Index mapping:
        # source = 0
        # donors: next len(donors) nodes: indices 1 .. len(donors)
        # receivers: next len(receivers) nodes: indices 1+len(donors) .. 1+len(donors)+len(receivers)-1
        # sink: last node index = total nodes - 1
        N = 2 + len(donors) + len(receivers)
        source = 0
        sink = N - 1

        graph = [[] for _ in range(N)]

        # Function to add edge with its reverse edge
        def add_edge(fr, to, cap, cost):
            graph[fr].append([to, cap, cost, len(graph[to])])
            graph[to].append([fr, 0, -cost, len(graph[fr]) - 1])

        # Add edges from source to donor nodes
        for i, (node, supply) in enumerate(donors):
            add_edge(source, 1 + i, supply, 0)
        # Add edges from receiver nodes to sink
        for j, (node, demand) in enumerate(receivers):
            add_edge(1 + len(donors) + j, sink, demand, 0)
        # Add edges from donors to receivers with cost equal to shortest path cost between planets
        for i, (donor_node, supply) in enumerate(donors):
            for j, (receiver_node, demand) in enumerate(receivers):
                cst = dist[donor_node][receiver_node]
                if cst < INF:
                    add_edge(1 + i, 1 + len(donors) + j, INF, cst)

        flow = 0
        cost = 0
        potential = [0] * N
        distnode = [0] * N
        parent_v = [0] * N
        parent_e = [0] * N

        while flow < total_required:
            distnode = [INF] * N
            distnode[source] = 0
            hq = [(0, source)]
            while hq:
                d, v = heapq.heappop(hq)
                if d != distnode[v]:
                    continue
                for i, edge in enumerate(graph[v]):
                    to, cap, edge_cost, rev = edge
                    if cap > 0 and distnode[v] + edge_cost + potential[v] - potential[to] < distnode[to]:
                        distnode[to] = distnode[v] + edge_cost + potential[v] - potential[to]
                        parent_v[to] = v
                        parent_e[to] = i
                        heapq.heappush(hq, (distnode[to], to))
            if distnode[sink] == INF:
                return None  # Not all flow can be sent
            for v in range(N):
                if distnode[v] < INF:
                    potential[v] += distnode[v]
            add_flow = total_required - flow
            v = sink
            while v != source:
                pv = parent_v[v]
                pe = parent_e[v]
                add_flow = min(add_flow, graph[pv][pe][1])
                v = pv
            flow += add_flow
            cost += add_flow * potential[sink]
            v = sink
            while v != source:
                pv = parent_v[v]
                pe = parent_e[v]
                graph[pv][pe][1] -= add_flow
                rev = graph[pv][pe][3]
                graph[v][rev][1] += add_flow
                v = pv
        return cost

    total_cost = 0
    # Process each resource type separately (0: energy, 1: minerals, 2: water)
    for resource_idx in range(3):
        surpluses = [max(0, production[i][resource_idx] - needs[i][resource_idx]) for i in range(n)]
        deficits = [max(0, needs[i][resource_idx] - production[i][resource_idx]) for i in range(n)]
        if sum(surpluses) < sum(deficits):
            return -1
        cost_for_resource = min_cost_for_resource(surpluses, deficits)
        if cost_for_resource is None:
            return -1
        total_cost += cost_for_resource

    if total_cost <= C:
        return total_cost
    return -1

if __name__ == "__main__":
    # Example usage
    n = 3
    needs = {0: (10, 5, 2), 1: (5, 10, 8), 2: (2, 2, 2)}
    production = {0: (5, 0, 1), 1: (0, 8, 2), 2: (1, 1, 1)}
    trade_routes = [(0, 1, 1), (1, 2, 2), (0, 2, 3)]
    C = 200
    result = resource_network(n, needs, production, trade_routes, C)
    print(result)