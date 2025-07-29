import unittest
from collections import defaultdict, deque
from toll_placement import optimal_toll_placement

def build_graph(N, edges, toll_edges=set()):
    """
    Build an undirected graph as an adjacency list.
    If toll_edges is provided, they will be removed from the graph.
    """
    graph = defaultdict(list)
    for (u, v, L, T) in edges:
        # if the edge (in either order) is marked as having a toll booth, and we are removing toll booth edges, skip adding it.
        if (u, v) in toll_edges or (v, u) in toll_edges:
            continue
        graph[u].append((v, L))
        graph[v].append((u, L))
    return graph

def is_connected(N, graph):
    visited = [False] * N
    q = deque([0])
    visited[0] = True
    count = 1
    while q:
        node = q.popleft()
        for neighbor, _ in graph[node]:
            if not visited[neighbor]:
                visited[neighbor] = True
                q.append(neighbor)
                count += 1
    return count == N

def edge_in_edges(edge, edges):
    (u, v) = edge
    for e in edges:
        if (u == e[0] and v == e[1]) or (u == e[1] and v == e[0]):
            return True
    return False

class TollPlacementTest(unittest.TestCase):
    def setUp(self):
        # Common function to verify solution constraints:
        self.verify_solution = self._verify_solution

    def _verify_solution(self, N, edges, B, C, R, D, selected):
        # 1. Check that selected edges are valid edges from input.
        valid_edges = set()
        cost_sum = 0
        edge_length = {}
        for (u, v, L, T) in edges:
            key = (min(u, v), max(u, v))
            valid_edges.add(key)
            edge_length[key] = L

        selected_keys = set()
        for (u, v) in selected:
            key = (min(u, v), max(u, v))
            self.assertIn(key, valid_edges, f"Selected edge {(u, v)} is not in input edges")
            selected_keys.add(key)
            cost_sum += C * edge_length[key]
        
        # 2. Budget constraint.
        self.assertLessEqual(cost_sum, B, "Total cost of selected toll booths exceeds the budget.")

        # 3. Connectivity constraint: Remove all selected toll booth edges and ensure graph remains connected.
        toll_edges = set()
        for key in selected_keys:
            toll_edges.add(key)
        graph = build_graph(N, edges, toll_edges)
        self.assertTrue(is_connected(N, graph), "Graph is disconnected after removing toll booth edges.")

        # 4. Distance constraint:
        # For simplicity, assume that if D > 0 then no vertex can have more than one incident toll booth.
        if D > 0:
            incident_count = [0] * N
            for (u, v) in selected:
                incident_count[u] += 1
                incident_count[v] += 1
            for idx, count in enumerate(incident_count):
                self.assertLessEqual(count, 1, f"Vertex {idx} has {count} incident tolls, violating the distance constraint.")
        # If D == 0, no special check is needed.

    def test_basic_case(self):
        N = 5
        edges = [
            (0, 1, 10, 100),
            (0, 2, 15, 50),
            (1, 2, 5, 200),
            (1, 3, 20, 30),
            (2, 4, 25, 40),
            (3, 4, 10, 150)
        ]
        B = 500
        C = 2
        R = 1
        D = 30
        result = optimal_toll_placement(N, edges, B, C, R, D)
        self.verify_solution(N, edges, B, C, R, D, result)

    def test_no_toll_due_to_budget(self):
        N = 4
        edges = [
            (0, 1, 10, 80),
            (1, 2, 12, 90),
            (2, 3, 15, 70),
            (3, 0, 20, 60)
        ]
        # Budget is too low to place any toll booth.
        B = 5
        C = 3
        R = 2
        D = 10
        result = optimal_toll_placement(N, edges, B, C, R, D)
        self.assertEqual(result, [], "Expected no toll booths to be placed due to insufficient budget.")

    def test_bridge_edge_removal(self):
        # Create a graph where one of the edges is a bridge.
        N = 4
        edges = [
            (0, 1, 8, 100),
            (1, 2, 10, 80),
            (2, 3, 12, 90),
            (0, 3, 15, 50),
            (1, 3, 9, 110)
        ]
        B = 200
        C = 2
        R = 1
        D = 5
        # The edge (1,2) is a bridge if removed from the graph.
        result = optimal_toll_placement(N, edges, B, C, R, D)
        # Verify that no selected edge is a bridge.
        for edge in result:
            (u, v) = edge
            # Remove only this edge and check connectivity.
            toll_edges = {(min(u, v), max(u, v))}
            graph = build_graph(N, edges, toll_edges)
            self.assertTrue(is_connected(N, graph), f"Selected edge {(u, v)} disconnects the graph.")

        self.verify_solution(N, edges, B, C, R, D, result)

    def test_distance_constraint_enforced(self):
        # Two edges share a vertex. With D > 0, they should not be both selected.
        N = 3
        edges = [
            (0, 1, 10, 100),
            (1, 2, 10, 100),
            (0, 2, 25, 50)
        ]
        B = 100
        C = 1
        R = 1
        D = 15  # With D > 0, cannot have both (0,1) and (1,2) selected because they share vertex 1.
        result = optimal_toll_placement(N, edges, B, C, R, D)
        # Check that no vertex appears in two toll booths.
        incident = {}
        for (u, v) in result:
            incident[u] = incident.get(u, 0) + 1
            incident[v] = incident.get(v, 0) + 1
        for v in incident:
            self.assertLessEqual(incident[v], 1, f"Vertex {v} is incident to more than one toll booth, violating distance constraint.")

        self.verify_solution(N, edges, B, C, R, D, result)

    def test_multiple_optimal_solutions(self):
        # Graph with several equally valid placements.
        N = 6
        edges = [
            (0, 1, 10, 100),
            (1, 2, 15, 120),
            (2, 3, 20, 80),
            (3, 4, 25, 90),
            (4, 5, 10, 110),
            (0, 5, 30, 70),
            (1, 4, 18, 95),
            (2, 5, 22, 85)
        ]
        B = 400
        C = 2
        R = 1
        D = 10
        result = optimal_toll_placement(N, edges, B, C, R, D)
        self.verify_solution(N, edges, B, C, R, D, result)

    def test_zero_distance_constraint(self):
        # When D is 0, multiple toll booths can share the same vertex.
        N = 4
        edges = [
            (0, 1, 12, 100),
            (1, 2, 12, 100),
            (2, 3, 12, 100),
            (3, 0, 12, 100),
            (0, 2, 18, 80)
        ]
        B = 300
        C = 1
        R = 1
        D = 0
        result = optimal_toll_placement(N, edges, B, C, R, D)
        # For D == 0, we do not enforce the single toll per vertex rule.
        self.verify_solution(N, edges, B, C, R, D, result)

if __name__ == '__main__':
    unittest.main()