import unittest
from collections import deque, defaultdict
from rail_network import optimize_network

def build_adjacency_list(edges, cities):
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    # Ensure every city is present even if isolated.
    for city in cities:
        cid = city[0]
        if cid not in graph:
            graph[cid] = []
    return graph

def is_connected(edges, cities):
    if not cities:
        return True
    adj = build_adjacency_list(edges, cities)
    start = cities[0][0]
    seen = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        for nbr in adj[node]:
            if nbr not in seen:
                stack.append(nbr)
    return seen == {city[0] for city in cities}

def build_flow_graph(edges, capacity_factors):
    """Builds and returns a directed graph (as a dict of dicts) for max flow.
    Each undirected edge (u, v) is converted to two directed edges with capacity.
    """
    flow_graph = defaultdict(dict)
    for u, v in edges:
        key = (min(u, v), max(u, v))
        cap = int(1000 * capacity_factors.get(key, 1))
        # For both directions, add capacity. If multiple edges occur, sum capacities.
        flow_graph[u][v] = flow_graph[u].get(v, 0) + cap
        flow_graph[v][u] = flow_graph[v].get(u, 0) + cap
    return flow_graph

def max_flow(flow_graph, source, sink):
    """Edmonds-Karp algorithm for maximum flow on directed graph represented as dict of dicts."""
    flow = 0
    while True:
        # BFS to find shortest augmenting path
        parent = {}
        visited = set()
        queue = deque()
        queue.append(source)
        visited.add(source)
        while queue and sink not in visited:
            u = queue.popleft()
            for v in flow_graph[u]:
                if v not in visited and flow_graph[u][v] > 0:
                    visited.add(v)
                    parent[v] = u
                    queue.append(v)
        if sink not in visited:
            break
        # Find minimum residual capacity in the found path
        v = sink
        path_flow = float('inf')
        while v != source:
            u = parent[v]
            path_flow = min(path_flow, flow_graph[u][v])
            v = u
        # Update residual capacities
        v = sink
        while v != source:
            u = parent[v]
            flow_graph[u][v] -= path_flow
            flow_graph[v][u] = flow_graph[v].get(u, 0) + path_flow
            v = u
        flow += path_flow
    return flow

def count_edge_disjoint_paths(edges, capacity_factors, src, dst):
    """Since each edge capacity is calculated as int(1000 * factor), and factor>=1,
    we can use max_flow with unit '1' capacity for each edge by setting capacity=1, to count edge-disjoint paths.
    We'll build a directed graph with capacity 1 for each edge.
    """
    graph = defaultdict(dict)
    for u, v in edges:
        # assign capacity 1 for each undirected edge
        if v not in graph[u]:
            graph[u][v] = 1
        else:
            graph[u][v] += 1
        if u not in graph[v]:
            graph[v][u] = 1
        else:
            graph[v][u] += 1
    # Use Edmonds-Karp on this graph
    return max_flow(graph, src, dst)

def compute_max_flow_for_pair(edges, capacity_factors, src, dst):
    """Compute maximum flow on the network (with actual capacities) for given src and dst."""
    flow_graph = build_flow_graph(edges, capacity_factors)
    return max_flow(flow_graph, src, dst)

class TestRailNetwork(unittest.TestCase):

    def test_single_city(self):
        # One city, no edges needed.
        N = 1
        cities = [
            (1, 500, 100, 100, False)
        ]
        potential_edges = []
        capacity_factors = {}
        # Expect empty list of edges.
        result = optimize_network(N, cities, potential_edges, capacity_factors)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
        self.assertTrue(is_connected(result, cities))

    def test_basic_two_cities(self):
        # Two cities, connected by a single potential edge.
        N = 2
        cities = [
            (1, 300, 0, 0, False),
            (2, 400, 10, 10, False)
        ]
        potential_edges = [
            (1, 2, 15, 1)  # cost = 15
        ]
        capacity_factors = { (1, 2): 1 }
        result = optimize_network(N, cities, potential_edges, capacity_factors)
        # Should return one edge connecting the two cities.
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        edge = result[0]
        self.assertTrue(set(edge) == {1, 2})
        self.assertTrue(is_connected(result, cities))
        # Check for flow requirement: minimum demand is 300.
        flow = compute_max_flow_for_pair(result, capacity_factors, 1, 2)
        self.assertGreaterEqual(flow, min(300, 400))

    def test_network_with_critical_cities(self):
        # Create a network with multiple cities and critical connectivity requirements.
        N = 5
        # cities: (city_id, population, x, y, is_critical)
        cities = [
            (1, 500, 100, 100, True),
            (2, 300, 200, 200, False),
            (3, 400, 300, 300, False),
            (4, 250, 400, 400, True),
            (5, 350, 500, 500, False)
        ]
        # potential_edges list with tuple: (city_id_1, city_id_2, base_cost, terrain_factor)
        potential_edges = [
            (1, 2, 10, 1),
            (1, 3, 20, 1),
            (2, 3, 5, 1),
            (2, 4, 15, 2),
            (3, 4, 10, 1),
            (3, 5, 25, 1),
            (4, 5, 5, 1),
            (1, 5, 50, 1)
        ]
        capacity_factors = {
            (1, 2): 1,
            (1, 3): 1,
            (2, 3): 1,
            (2, 4): 1,
            (3, 4): 1,
            (3, 5): 1,
            (4, 5): 1,
            (1, 5): 1
        }
        result = optimize_network(N, cities, potential_edges, capacity_factors)
        # Check that the network is connected.
        self.assertTrue(is_connected(result, cities))
        
        # For flow requirement, check that for every pair of cities the max flow is >= min(demand)
        demands = {city[0]: city[1] for city in cities}
        for i in range(len(cities)):
            for j in range(i+1, len(cities)):
                src = cities[i][0]
                dst = cities[j][0]
                required_flow = min(demands[src], demands[dst])
                flow = compute_max_flow_for_pair(result, capacity_factors, src, dst)
                self.assertGreaterEqual(flow, required_flow, f"Flow requirement not met between {src} and {dst}.")

        # For each critical city, ensure that for every other city there are at least two independent paths.
        critical_ids = [city[0] for city in cities if city[4]]
        for crit in critical_ids:
            for other in [city[0] for city in cities if city[0] != crit]:
                disjoint_paths = count_edge_disjoint_paths(result, capacity_factors, crit, other)
                self.assertGreaterEqual(disjoint_paths, 2, f"Critical city {crit} does not have 2 independent paths to {other}.")

    def test_invalid_no_feasible_network(self):
        # Test a case where the potential edges provided do not allow connectivity.
        N = 3
        cities = [
            (1, 300, 0, 0, False),
            (2, 400, 10, 10, True),
            (3, 500, 20, 20, False)
        ]
        potential_edges = [
            (1, 2, 10, 1)
            # City 3 is isolated.
        ]
        capacity_factors = { (1, 2): 1 }
        result = optimize_network(N, cities, potential_edges, capacity_factors)
        # The network must be connected, so if the solution returns an incomplete network,
        # the connectivity check will fail.
        self.assertFalse(is_connected(result, cities), "The network should be disconnected as city 3 is isolated.")

if __name__ == '__main__':
    unittest.main()