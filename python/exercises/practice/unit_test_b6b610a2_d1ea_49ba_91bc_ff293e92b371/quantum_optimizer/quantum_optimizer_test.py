import unittest
from quantum_optimizer import optimize_quantum_circuit


class QuantumOptimizerTest(unittest.TestCase):
    def test_simple_circuit(self):
        circuit_dag = {
            "gate_1": {
                "qubits": [0],
                "gate_type": "H",
                "execution_time": 1,
                "fidelity": 0.99,
                "dependencies": []
            },
            "gate_2": {
                "qubits": [1],
                "gate_type": "H",
                "execution_time": 1,
                "fidelity": 0.99,
                "dependencies": []
            },
            "gate_3": {
                "qubits": [0, 1],
                "gate_type": "CNOT",
                "execution_time": 2,
                "fidelity": 0.95,
                "dependencies": ["gate_1", "gate_2"]
            }
        }
        qubit_adjacency_graph = {0: [1], 1: [0]}
        allowed_gates = {0: ["H", "CNOT"], 1: ["H", "CNOT"]}
        gate_dependencies = {}

        schedule, total_time, fidelity = optimize_quantum_circuit(
            circuit_dag, qubit_adjacency_graph, allowed_gates, gate_dependencies
        )

        # Verify the result is valid
        self.assertEqual(total_time, 3)  # H gates in parallel (t=1), then CNOT (t=2)
        self.assertAlmostEqual(fidelity, 0.99 * 0.99 * 0.95, places=6)
        
        # Check that the schedule is sorted by start time
        for i in range(len(schedule) - 1):
            self.assertLessEqual(schedule[i][1], schedule[i+1][1])
        
        # Check that all gates are scheduled
        scheduled_gates = [gate_id for gate_id, _ in schedule]
        self.assertCountEqual(scheduled_gates, ["gate_1", "gate_2", "gate_3"])

    def test_complex_circuit(self):
        circuit_dag = {
            "gate_1": {
                "qubits": [0],
                "gate_type": "H",
                "execution_time": 1,
                "fidelity": 0.99,
                "dependencies": []
            },
            "gate_2": {
                "qubits": [1],
                "gate_type": "X",
                "execution_time": 1,
                "fidelity": 0.98,
                "dependencies": []
            },
            "gate_3": {
                "qubits": [2],
                "gate_type": "H",
                "execution_time": 1,
                "fidelity": 0.99,
                "dependencies": []
            },
            "gate_4": {
                "qubits": [0, 1],
                "gate_type": "CNOT",
                "execution_time": 2,
                "fidelity": 0.95,
                "dependencies": ["gate_1", "gate_2"]
            },
            "gate_5": {
                "qubits": [1, 2],
                "gate_type": "CNOT",
                "execution_time": 2,
                "fidelity": 0.94,
                "dependencies": ["gate_2", "gate_3"]
            },
            "gate_6": {
                "qubits": [0],
                "gate_type": "RZ",
                "execution_time": 1,
                "fidelity": 0.97,
                "dependencies": ["gate_4"]
            },
            "gate_7": {
                "qubits": [2],
                "gate_type": "RX",
                "execution_time": 1,
                "fidelity": 0.96,
                "dependencies": ["gate_5"]
            }
        }
        qubit_adjacency_graph = {0: [1], 1: [0, 2], 2: [1]}
        allowed_gates = {
            0: ["H", "CNOT", "RZ"],
            1: ["X", "CNOT"],
            2: ["H", "CNOT", "RX"]
        }
        gate_dependencies = {
            "gate_6": [("gate_1", 5)],
            "gate_7": [("gate_3", 6)]
        }

        schedule, total_time, fidelity = optimize_quantum_circuit(
            circuit_dag, qubit_adjacency_graph, allowed_gates, gate_dependencies
        )

        # Verify all gates are in schedule
        scheduled_gates = [gate_id for gate_id, _ in schedule]
        self.assertCountEqual(scheduled_gates, 
                              ["gate_1", "gate_2", "gate_3", "gate_4", 
                               "gate_5", "gate_6", "gate_7"])
        
        # Check dependencies are respected
        gate_start_times = {gate_id: start_time for gate_id, start_time in schedule}
        
        # Check gate dependencies
        self.assertLess(gate_start_times["gate_1"], gate_start_times["gate_4"])
        self.assertLess(gate_start_times["gate_2"], gate_start_times["gate_4"])
        self.assertLess(gate_start_times["gate_2"], gate_start_times["gate_5"])
        self.assertLess(gate_start_times["gate_3"], gate_start_times["gate_5"])
        self.assertLess(gate_start_times["gate_4"], gate_start_times["gate_6"])
        self.assertLess(gate_start_times["gate_5"], gate_start_times["gate_7"])
        
        # Check temporal constraints
        self.assertLessEqual(gate_start_times["gate_6"] - gate_start_times["gate_1"], 5)
        self.assertLessEqual(gate_start_times["gate_7"] - gate_start_times["gate_3"], 6)
        
        # Check fidelity calculation
        expected_fidelity = 0.99 * 0.98 * 0.99 * 0.95 * 0.94 * 0.97 * 0.96
        self.assertAlmostEqual(fidelity, expected_fidelity, places=6)

    def test_architectural_constraints(self):
        circuit_dag = {
            "gate_1": {
                "qubits": [0],
                "gate_type": "H",
                "execution_time": 1,
                "fidelity": 0.99,
                "dependencies": []
            },
            "gate_2": {
                "qubits": [1],
                "gate_type": "H",
                "execution_time": 1,
                "fidelity": 0.99,
                "dependencies": []
            },
            "gate_3": {
                "qubits": [0, 2],  # Non-adjacent qubits
                "gate_type": "CNOT",
                "execution_time": 2,
                "fidelity": 0.95,
                "dependencies": ["gate_1"]
            },
            "gate_4": {
                "qubits": [0],
                "gate_type": "RZ",  # Not allowed on qubit 0
                "execution_time": 1,
                "fidelity": 0.97,
                "dependencies": ["gate_1"]
            }
        }
        qubit_adjacency_graph = {0: [1], 1: [0, 2], 2: [1]}
        allowed_gates = {
            0: ["H", "CNOT"],  # RZ not allowed
            1: ["H", "CNOT", "RZ"],
            2: ["H", "CNOT", "RZ"]
        }
        gate_dependencies = {}

        with self.assertRaises(ValueError):
            optimize_quantum_circuit(
                circuit_dag, qubit_adjacency_graph, allowed_gates, gate_dependencies
            )

    def test_edge_case_empty_circuit(self):
        circuit_dag = {}
        qubit_adjacency_graph = {0: [1], 1: [0]}
        allowed_gates = {0: ["H", "CNOT"], 1: ["H", "CNOT"]}
        gate_dependencies = {}

        schedule, total_time, fidelity = optimize_quantum_circuit(
            circuit_dag, qubit_adjacency_graph, allowed_gates, gate_dependencies
        )

        self.assertEqual(schedule, [])
        self.assertEqual(total_time, 0)
        self.assertEqual(fidelity, 1.0)  # No gates, perfect fidelity

    def test_complex_dependency_chain(self):
        # Create a long chain of dependencies where each gate depends on the previous one
        circuit_dag = {}
        for i in range(10):
            dependencies = [] if i == 0 else [f"gate_{i}"]
            circuit_dag[f"gate_{i+1}"] = {
                "qubits": [0],
                "gate_type": "H",
                "execution_time": 1,
                "fidelity": 0.99,
                "dependencies": dependencies
            }
        
        qubit_adjacency_graph = {0: []}
        allowed_gates = {0: ["H"]}
        gate_dependencies = {}

        schedule, total_time, fidelity = optimize_quantum_circuit(
            circuit_dag, qubit_adjacency_graph, allowed_gates, gate_dependencies
        )

        # In a perfect chain, total time should be sum of all execution times
        self.assertEqual(total_time, 10)  # 10 gates with execution_time=1
        self.assertAlmostEqual(fidelity, 0.99 ** 10, places=6)
        
        # Verify the schedule follows dependencies
        gate_start_times = {gate_id: start_time for gate_id, start_time in schedule}
        for i in range(1, 10):
            self.assertLess(gate_start_times[f"gate_{i}"], gate_start_times[f"gate_{i+1}"])

    def test_parallel_execution(self):
        # Create a circuit where many gates can run in parallel
        circuit_dag = {}
        for i in range(5):
            circuit_dag[f"gate_{i+1}"] = {
                "qubits": [i],
                "gate_type": "H",
                "execution_time": 1,
                "fidelity": 0.99,
                "dependencies": []
            }
        
        qubit_adjacency_graph = {i: [] for i in range(5)}
        allowed_gates = {i: ["H"] for i in range(5)}
        gate_dependencies = {}

        schedule, total_time, fidelity = optimize_quantum_circuit(
            circuit_dag, qubit_adjacency_graph, allowed_gates, gate_dependencies
        )

        # All gates can run in parallel, so total time should be max of execution times
        self.assertEqual(total_time, 1)
        self.assertAlmostEqual(fidelity, 0.99 ** 5, places=6)

    def test_temporal_constraints(self):
        circuit_dag = {
            "gate_1": {
                "qubits": [0],
                "gate_type": "H",
                "execution_time": 1,
                "fidelity": 0.99,
                "dependencies": []
            },
            "gate_2": {
                "qubits": [1],
                "gate_type": "H",
                "execution_time": 1,
                "fidelity": 0.99,
                "dependencies": []
            },
            "gate_3": {
                "qubits": [2],
                "gate_type": "H", 
                "execution_time": 1,
                "fidelity": 0.99,
                "dependencies": []
            },
            "gate_4": {
                "qubits": [0],
                "gate_type": "X",
                "execution_time": 1,
                "fidelity": 0.98,
                "dependencies": ["gate_1"]
            }
        }
        qubit_adjacency_graph = {0: [1], 1: [0, 2], 2: [1]}
        allowed_gates = {
            0: ["H", "X"],
            1: ["H"],
            2: ["H"]
        }
        # Gate_4 must be executed within 2 time units after gate_1
        gate_dependencies = {
            "gate_4": [("gate_1", 2)]
        }

        schedule, total_time, fidelity = optimize_quantum_circuit(
            circuit_dag, qubit_adjacency_graph, allowed_gates, gate_dependencies
        )

        # Check that temporal constraint is satisfied
        gate_start_times = {gate_id: start_time for gate_id, start_time in schedule}
        self.assertLessEqual(
            gate_start_times["gate_4"] - gate_start_times["gate_1"], 
            2,
            "Temporal constraint violated"
        )

if __name__ == "__main__":
    unittest.main()