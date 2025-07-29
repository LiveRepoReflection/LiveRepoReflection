import unittest
from circuit_optimize import optimize_circuit

class TestCircuitOptimize(unittest.TestCase):
    def test_basic_connectivity(self):
        num_qubits = 3
        coupling_map = [(0, 1), (1, 2)]
        circuit = [
            ("H", [0], []),
            ("CNOT", [0, 2], []),
            ("H", [2], [])
        ]
        optimized = optimize_circuit(num_qubits, coupling_map, circuit)
        self.assertTrue(self.validate_circuit(optimized, coupling_map))
        self.assertTrue(self.circuits_equivalent(circuit, optimized, num_qubits))

    def test_no_swap_needed(self):
        num_qubits = 2
        coupling_map = [(0, 1)]
        circuit = [
            ("H", [0], []),
            ("CNOT", [0, 1], []),
            ("H", [1], [])
        ]
        optimized = optimize_circuit(num_qubits, coupling_map, circuit)
        self.assertEqual(len(optimized), 3)  # No additional gates should be added
        self.assertEqual(optimized, circuit)

    def test_multiple_swaps(self):
        num_qubits = 4
        coupling_map = [(0, 1), (1, 2), (2, 3)]
        circuit = [
            ("CNOT", [0, 3], []),
            ("CNOT", [3, 0], [])
        ]
        optimized = optimize_circuit(num_qubits, coupling_map, circuit)
        self.assertTrue(self.validate_circuit(optimized, coupling_map))
        self.assertTrue(self.circuits_equivalent(circuit, optimized, num_qubits))

    def test_parameterized_gates(self):
        num_qubits = 3
        coupling_map = [(0, 1), (1, 2)]
        circuit = [
            ("RZ", [0], [0.5]),
            ("CNOT", [0, 2], []),
            ("RZ", [2], [1.0])
        ]
        optimized = optimize_circuit(num_qubits, coupling_map, circuit)
        self.assertTrue(self.validate_circuit(optimized, coupling_map))
        self.assertTrue(self.circuits_equivalent(circuit, optimized, num_qubits))

    def test_complex_circuit(self):
        num_qubits = 5
        coupling_map = [(0, 1), (1, 2), (2, 3), (3, 4)]
        circuit = [
            ("H", [0], []),
            ("CNOT", [0, 4], []),
            ("RZ", [2], [0.3]),
            ("CNOT", [4, 1], []),
            ("H", [3], [])
        ]
        optimized = optimize_circuit(num_qubits, coupling_map, circuit)
        self.assertTrue(self.validate_circuit(optimized, coupling_map))
        self.assertTrue(self.circuits_equivalent(circuit, optimized, num_qubits))

    def validate_circuit(self, circuit, coupling_map):
        """Check if all two-qubit gates in circuit satisfy coupling constraints"""
        for gate in circuit:
            if gate[0] in ["CNOT", "SWAP"]:
                q1, q2 = gate[1]
                if (q1, q2) not in coupling_map and (q2, q1) not in coupling_map:
                    return False
        return True

    def circuits_equivalent(self, original, optimized, num_qubits):
        """Simplified equivalence check - in practice would need full unitary comparison"""
        # Count the number of each gate type in both circuits
        orig_counts = self.count_gates(original)
        opt_counts = self.count_gates(optimized)
        
        # Check that all original gates are present (though possibly in different order)
        for gate in ["H", "CNOT", "RZ", "SWAP"]:
            if orig_counts.get(gate, 0) > opt_counts.get(gate, 0):
                return False
        
        # Additional checks could be added here for more thorough verification
        return True

    def count_gates(self, circuit):
        counts = {}
        for gate in circuit:
            counts[gate[0]] = counts.get(gate[0], 0) + 1
        return counts

if __name__ == '__main__':
    unittest.main()