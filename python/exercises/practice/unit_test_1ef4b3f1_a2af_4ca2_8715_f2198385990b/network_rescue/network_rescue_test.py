import unittest
from collections import defaultdict, deque
from network_rescue import deploy_routers

def build_graph(num_locations, edges):
    graph = defaultdict(list)
    for u, v, w in edges:
        graph[u].append((v, w))
        graph[v].append((u, w))
    return graph

def get_connected_components(num_locations, graph):
    seen = [False] * num_locations
    components = []
    for start in range(num_locations):
        if not seen[start]:
            comp = set()
            queue = deque([start])
            seen[start] = True
            while queue:
                u = queue.popleft()
                comp.add(u)
                for v, _ in graph[u]:
                    if not seen[v]:
                        seen[v] = True
                        queue.append(v)
            components.append(comp)
    return components

def check_connectivity(num_locations, edges, router_set):
    """
    For every connected component in the graph defined by edges, at least one node must be in router_set.
    """
    graph = build_graph(num_locations, edges)
    components = get_connected_components(num_locations, graph)
    # If a location is isolated (no edges), it forms its own component.
    for comp in components:
        if comp.isdisjoint(router_set):
            return False
    return True

def compute_direct_link_cost(num_locations, edges, router_set):
    """
    For every node that is not a router but is directly connected (via an edge) to one or more routers,
    assign the minimum cost edge from a router to that node. If a node is not directly adjacent to any router,
    assume that it is covered indirectly and incurs no direct link cost.
    Return the sum of these costs.
    """
    # Build a mapping for quick lookup of direct connection costs.
    # For each non-router node, for every router neighbor, note the edge weight and take the minimum.
    cost = 0
    # Create an adjacency dictionary that maps (u, v) with cost for both directions.
    adj = defaultdict(dict)
    for u, v, w in edges:
        # if multiple edges exist between same nodes, consider the minimum cost.
        if v not in adj[u] or w < adj[u][v]:
            adj[u][v] = w
        if u not in adj[v] or w < adj[v][u]:
            adj[v][u] = w

    for node in range(num_locations):
        if node in router_set:
            continue
        # Check if node has any router neighbor via a direct edge.
        min_cost = None
        for neighbor, w in adj[node].items():
            if neighbor in router_set:
                if min_cost is None or w < min_cost:
                    min_cost = w
        if min_cost is not None:
            cost += min_cost
    return cost

class NetworkRescueTest(unittest.TestCase):

    def test_single_node(self):
        num_locations = 1
        edges = []
        router_range = [10]
        router_power = [5]
        budget = 0
        result = deploy_routers(num_locations, edges, router_range, router_power, budget)
        # Expect a router placed at the only node.
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 0)
        self.assertTrue(check_connectivity(num_locations, edges, set(result)))
        direct_cost = compute_direct_link_cost(num_locations, edges, set(result))
        self.assertLessEqual(direct_cost, budget)

    def test_two_nodes(self):
        num_locations = 2
        edges = [(0, 1, 3)]
        router_range = [10, 10]
        router_power = [5, 4]
        budget = 3
        result = deploy_routers(num_locations, edges, router_range, router_power, budget)
        # The result should be a non-empty list containing one valid router index.
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        for r in result:
            self.assertTrue(0 <= r < num_locations)
        # Check connectivity: both nodes must be in a component that has at least one router.
        self.assertTrue(check_connectivity(num_locations, edges, set(result)))
        direct_cost = compute_direct_link_cost(num_locations, edges, set(result))
        self.assertLessEqual(direct_cost, budget)

    def test_complex_graph(self):
        # Create a graph with 5 nodes and multiple edges.
        num_locations = 5
        edges = [
            (0, 1, 2),
            (1, 2, 10),
            (2, 3, 1),
            (3, 4, 3),
            (0, 2, 4),
            (1, 3, 2),
            (2, 4, 2)
        ]
        router_range = [15, 15, 15, 15, 15]
        router_power = [4, 3, 5, 2, 6]
        budget = 5
        result = deploy_routers(num_locations, edges, router_range, router_power, budget)
        self.assertIsInstance(result, list)
        # Ensure that the returned routers are valid indices.
        for r in result:
            self.assertTrue(0 <= r < num_locations)
        self.assertTrue(check_connectivity(num_locations, edges, set(result)))
        direct_cost = compute_direct_link_cost(num_locations, edges, set(result))
        self.assertLessEqual(direct_cost, budget)

    def test_all_nodes_router_due_to_budget(self):
        # In this scenario, a minimal direct link cost demands that every node should be a router,
        # as any direct link from a router to a non-router would exceed the extremely strict budget.
        num_locations = 4
        edges = [
            (0, 1, 1),
            (1, 2, 1),
            (2, 3, 1),
            (3, 0, 1)
        ]
        router_range = [10, 10, 10, 10]
        router_power = [5, 4, 6, 7]
        budget = 0  # Budget is zero; direct link cost cannot be incurred.
        result = deploy_routers(num_locations, edges, router_range, router_power, budget)
        self.assertIsInstance(result, list)
        # The only valid way is to have every node as a router.
        self.assertEqual(set(result), set(range(num_locations)))
        self.assertTrue(check_connectivity(num_locations, edges, set(result)))
        direct_cost = compute_direct_link_cost(num_locations, edges, set(result))
        self.assertEqual(direct_cost, 0)

if __name__ == '__main__':
    unittest.main()