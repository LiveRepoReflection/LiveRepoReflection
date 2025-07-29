import unittest
from collections import deque, defaultdict
from copy import deepcopy

from cnot_optimizer import optimize_circuit

def is_topologically_sorted(order, dag):
    # Build position map: gate id -> index in order
    pos = {gate_id: idx for idx, gate_id in enumerate(order)}
    # For each edge, ensure that src comes before dest
    for src, dests in dag["edges"].items():
        for dest in dests:
            if pos[src] >= pos[dest]:
                return False
    return True

def compute_crossings(order, dag):
    # Compute number of crossing pairs among CNOT gates.
    # For each pair of CNOT gates (i, j) with i < j, if they share common qubits, count one crossing.
    nodes = dag["nodes"]
    cnot_orders = []
    for gate_id in order:
        gate = nodes[gate_id]
        if gate["type"] == "CNOT":
            cnot_orders.append((gate_id, gate["qubits"]))
    count = 0
    n = len(cnot_orders)
    for i in range(n):
        for j in range(i+1, n):
            # if overlapping qubits, count as crossing
            if cnot_orders[i][1] & cnot_orders[j][1]:
                count += 1
    return count

def baseline_topological_order(dag):
    # Compute a valid topological ordering using Kahn's algorithm with sorted order for tie breaking.
    in_degree = defaultdict(int)
    for node in dag["nodes"]:
        in_degree[node] = 0
    for src, dests in dag["edges"].items():
        for dest in dests:
            in_degree[dest] += 1

    queue = deque(sorted([node for node in dag["nodes"] if in_degree[node] == 0]))
    order = []
    while queue:
        current = queue.popleft()
        order.append(current)
        for neighbor in dag["edges"].get(current, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
        queue = deque(sorted(queue))
    return order

class CNOTOptimizerTest(unittest.TestCase):

    def test_empty_graph(self):
        dag = {
            "nodes": {},
            "edges": {}
        }
        ordering = optimize_circuit(dag)
        self.assertEqual(ordering, [])

    def test_single_gate(self):
        dag = {
            "nodes": {
                "G1": {"id": "G1", "type": "CNOT", "qubits": {0, 1}}
            },
            "edges": {
                "G1": []
            }
        }
        ordering = optimize_circuit(dag)
        self.assertEqual(ordering, ["G1"])
        self.assertTrue(is_topologically_sorted(ordering, dag))
        self.assertEqual(compute_crossings(ordering, dag), 0)

    def test_only_single_qubit_gates(self):
        dag = {
            "nodes": {
                "G1": {"id": "G1", "type": "SingleQubit", "qubits": {0}},
                "G2": {"id": "G2", "type": "SingleQubit", "qubits": {1}},
                "G3": {"id": "G3", "type": "SingleQubit", "qubits": {2}},
            },
            "edges": {
                "G1": ["G2"],
                "G2": ["G3"],
                "G3": []
            }
        }
        ordering = optimize_circuit(dag)
        self.assertEqual(len(ordering), 3)
        self.assertTrue(is_topologically_sorted(ordering, dag))
        # Since there are no CNOT gates, crossing count must be 0
        self.assertEqual(compute_crossings(ordering, dag), 0)

    def test_complex_dag(self):
        dag = {
            "nodes": {
                "A": {"id": "A", "type": "CNOT", "qubits": {0, 1}},
                "B": {"id": "B", "type": "CNOT", "qubits": {1, 2}},
                "C": {"id": "C", "type": "SingleQubit", "qubits": {2}},
                "D": {"id": "D", "type": "CNOT", "qubits": {0, 2}},
                "E": {"id": "E", "type": "CNOT", "qubits": {2, 3}},
                "F": {"id": "F", "type": "SingleQubit", "qubits": {3}},
            },
            "edges": {
                "A": ["B", "D"],
                "B": ["C", "E"],
                "C": ["F"],
                "D": ["E"],
                "E": ["F"],
                "F": []
            }
        }
        ordering = optimize_circuit(deepcopy(dag))
        self.assertEqual(set(ordering), set(dag["nodes"].keys()))
        self.assertTrue(is_topologically_sorted(ordering, dag))
        # Compare crossing count with baseline ordering
        baseline_order = baseline_topological_order(dag)
        optimized_crossings = compute_crossings(ordering, dag)
        baseline_crossings = compute_crossings(baseline_order, dag)
        self.assertLessEqual(optimized_crossings, baseline_crossings)

    def test_multiple_valid_paths(self):
        # This test ensures that the optimizer respects dependencies even when multiple valid orders exist.
        dag = {
            "nodes": {
                "G1": {"id": "G1", "type": "CNOT", "qubits": {0, 1}},
                "G2": {"id": "G2", "type": "CNOT", "qubits": {1, 2}},
                "G3": {"id": "G3", "type": "CNOT", "qubits": {0, 2}},
                "G4": {"id": "G4", "type": "SingleQubit", "qubits": {3}},
                "G5": {"id": "G5", "type": "CNOT", "qubits": {2, 3}},
            },
            "edges": {
                "G1": ["G2", "G3"],
                "G2": ["G5"],
                "G3": ["G5"],
                "G4": ["G5"],
                "G5": []
            }
        }
        ordering = optimize_circuit(deepcopy(dag))
        self.assertEqual(set(ordering), set(dag["nodes"].keys()))
        self.assertTrue(is_topologically_sorted(ordering, dag))
        # Ensure that the computed crossing count is an integer and non-negative.
        crossings = compute_crossings(ordering, dag)
        self.assertIsInstance(crossings, int)
        self.assertGreaterEqual(crossings, 0)

if __name__ == '__main__':
    unittest.main()