import unittest
from quantum_optimize import optimize_circuit

class QuantumOptimizeTest(unittest.TestCase):
    def test_simple_circuit(self):
        circuit = {
            0: {'type': 'H', 'qubits': [0], 'time': 1.0, 'error': 0.001},
            1: {'type': 'CNOT', 'qubits': [0, 1], 'time': 2.0, 'error': 0.002}
        }
        connectivity = [(0, 1), (1, 2)]
        swap_time = 3.0
        swap_error = 0.003
        max_error = 0.01
        initial_mapping = {0: 0, 1: 1, 2: 2}

        result = optimize_circuit(circuit, connectivity, swap_time, swap_error, max_error, initial_mapping)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)  # Should remain the same as no SWAP needed

    def test_requires_swap(self):
        circuit = {
            0: {'type': 'H', 'qubits': [0], 'time': 1.0, 'error': 0.001},
            1: {'type': 'CNOT', 'qubits': [0, 2], 'time': 2.0, 'error': 0.002}
        }
        connectivity = [(0, 1), (1, 2)]
        swap_time = 3.0
        swap_error = 0.003
        max_error = 0.01
        initial_mapping = {0: 0, 1: 1, 2: 2}

        result = optimize_circuit(circuit, connectivity, swap_time, swap_error, max_error, initial_mapping)
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 2)  # Should include SWAP gate(s)

    def test_exceeds_error_rate(self):
        circuit = {
            0: {'type': 'H', 'qubits': [0], 'time': 1.0, 'error': 0.005},
            1: {'type': 'CNOT', 'qubits': [0, 2], 'time': 2.0, 'error': 0.006}
        }
        connectivity = [(0, 1), (1, 2)]
        swap_time = 3.0
        swap_error = 0.003
        max_error = 0.01  # Too low for the required SWAP
        initial_mapping = {0: 0, 1: 1, 2: 2}

        result = optimize_circuit(circuit, connectivity, swap_time, swap_error, max_error, initial_mapping)
        self.assertIsNone(result)

    def test_complex_circuit(self):
        circuit = {
            0: {'type': 'H', 'qubits': [0], 'time': 1.0, 'error': 0.001},
            1: {'type': 'CNOT', 'qubits': [0, 2], 'time': 2.0, 'error': 0.002},
            2: {'type': 'H', 'qubits': [1], 'time': 1.0, 'error': 0.001},
            3: {'type': 'CNOT', 'qubits': [2, 3], 'time': 2.0, 'error': 0.002}
        }
        connectivity = [(0, 1), (1, 2), (2, 3)]
        swap_time = 3.0
        swap_error = 0.003
        max_error = 0.02
        initial_mapping = {0: 0, 1: 1, 2: 2, 3: 3}

        result = optimize_circuit(circuit, connectivity, swap_time, swap_error, max_error, initial_mapping)
        self.assertIsNotNone(result)
        
    def test_invalid_connectivity(self):
        circuit = {
            0: {'type': 'CNOT', 'qubits': [0, 1], 'time': 2.0, 'error': 0.002}
        }
        connectivity = []  # Empty connectivity
        swap_time = 3.0
        swap_error = 0.003
        max_error = 0.01
        initial_mapping = {0: 0, 1: 1}

        result = optimize_circuit(circuit, connectivity, swap_time, swap_error, max_error, initial_mapping)
        self.assertIsNone(result)

    def test_large_circuit(self):
        # Create a larger circuit with multiple operations
        circuit = {}
        for i in range(10):
            circuit[i] = {
                'type': 'H' if i % 2 == 0 else 'CNOT',
                'qubits': [i % 4] if i % 2 == 0 else [i % 4, (i + 1) % 4],
                'time': 1.0 if i % 2 == 0 else 2.0,
                'error': 0.001
            }
        
        connectivity = [(i, i+1) for i in range(3)]
        swap_time = 3.0
        swap_error = 0.002
        max_error = 0.05
        initial_mapping = {i: i for i in range(4)}

        result = optimize_circuit(circuit, connectivity, swap_time, swap_error, max_error, initial_mapping)
        self.assertIsNotNone(result)

    def test_total_execution_time(self):
        circuit = {
            0: {'type': 'H', 'qubits': [0], 'time': 1.0, 'error': 0.001},
            1: {'type': 'CNOT', 'qubits': [0, 2], 'time': 2.0, 'error': 0.002}
        }
        connectivity = [(0, 1), (1, 2)]
        swap_time = 3.0
        swap_error = 0.003
        max_error = 0.01
        initial_mapping = {0: 0, 1: 1, 2: 2}

        result = optimize_circuit(circuit, connectivity, swap_time, swap_error, max_error, initial_mapping)
        
        # Calculate total execution time
        total_time = sum(gate['time'] for gate in result.values())
        # Should be less than original circuit plus 3 SWAP operations
        self.assertLess(total_time, 3.0 + 3 * swap_time)

    def test_error_rate_calculation(self):
        circuit = {
            0: {'type': 'H', 'qubits': [0], 'time': 1.0, 'error': 0.002},
            1: {'type': 'CNOT', 'qubits': [0, 1], 'time': 2.0, 'error': 0.003}
        }
        connectivity = [(0, 1)]
        swap_time = 3.0
        swap_error = 0.001
        max_error = 0.006
        initial_mapping = {0: 0, 1: 1}

        result = optimize_circuit(circuit, connectivity, swap_time, swap_error, max_error, initial_mapping)
        
        # Calculate total error rate
        total_error = sum(gate['error'] for gate in result.values())
        self.assertLessEqual(total_error, max_error)

if __name__ == '__main__':
    unittest.main()