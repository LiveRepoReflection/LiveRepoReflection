import unittest
from circuit_optimizer import optimize_circuit

class CircuitOptimizerTest(unittest.TestCase):
    def setUp(self):
        # A helper function to extract non-SWAP gates from a circuit
        self.extract_non_swap = lambda circuit: [gate for gate in circuit if gate[2] != "SWAP"]
    
    def count_swaps(self, circuit):
        return sum(1 for gate in circuit if gate[2] == "SWAP")
    
    def is_valid_swap(self, gate, coupling_map):
        # A SWAP gate must operate on two connected qubits, i.e., gate[0] and gate[1] must be connected
        a, b, gate_type, _ = gate
        if gate_type != "SWAP":
            return True
        return (a, b) in coupling_map or (b, a) in coupling_map

    def test_empty_circuit(self):
        num_qubits = 3
        circuit = []
        coupling_map = [(0, 1), (1, 2)]
        max_swaps = 2
        swap_noise = 0.02
        
        optimized = optimize_circuit(num_qubits, circuit, coupling_map, max_swaps, swap_noise)
        self.assertEqual(optimized, [], "Optimized circuit of empty input should be empty")

    def test_single_gate_circuit(self):
        num_qubits = 2
        circuit = [(0, -1, "H", 0.05)]
        coupling_map = [(0, 1)]
        max_swaps = 1
        swap_noise = 0.02
        
        optimized = optimize_circuit(num_qubits, circuit, coupling_map, max_swaps, swap_noise)
        # The original single gate must remain and no SWAP gate should be inserted unnecessarily.
        non_swap_original = self.extract_non_swap(circuit)
        non_swap_optimized = self.extract_non_swap(optimized)
        self.assertEqual(non_swap_optimized, non_swap_original,
                         "Original non-swap gates should be in order in the optimized circuit")
        self.assertLessEqual(self.count_swaps(optimized), max_swaps,
                             "Number of inserted SWAP gates should not exceed max_swaps")
    
    def test_no_swaps_allowed(self):
        num_qubits = 3
        circuit = [
            (0, 1, "CNOT", 0.1),
            (1, -1, "H", 0.05),
            (0, 2, "CNOT", 0.2),
            (2, -1, "X", 0.15)
        ]
        coupling_map = [(0, 1), (1, 2)]
        max_swaps = 0  # No swaps allowed
        swap_noise = 0.02
        
        optimized = optimize_circuit(num_qubits, circuit, coupling_map, max_swaps, swap_noise)
        # Ensure that no SWAP gates were inserted
        self.assertEqual(self.count_swaps(optimized), 0, "No SWAP gates should be inserted when max_swaps is 0")
        non_swap_original = self.extract_non_swap(circuit)
        non_swap_optimized = self.extract_non_swap(optimized)
        self.assertEqual(non_swap_optimized, non_swap_original,
                         "Original non-swap gates should remain unchanged when no swaps are allowed")
    
    def test_insertion_of_swaps_within_limit(self):
        num_qubits = 3
        circuit = [
            (0, 1, "CNOT", 0.1),
            (1, -1, "H", 0.05),
            (0, 2, "CNOT", 0.2),
            (2, -1, "X", 0.15)
        ]
        coupling_map = [(0, 1), (1, 2)]
        max_swaps = 2
        swap_noise = 0.02
        
        optimized = optimize_circuit(num_qubits, circuit, coupling_map, max_swaps, swap_noise)
        # Check that the order of the original gates is preserved.
        non_swap_original = self.extract_non_swap(circuit)
        non_swap_optimized = self.extract_non_swap(optimized)
        self.assertEqual(non_swap_optimized, non_swap_original,
                         "The relative order of the original gates must be preserved.")
        
        # Verify that the number of SWAP gates does not exceed max_swaps
        self.assertLessEqual(self.count_swaps(optimized), max_swaps,
                             "Inserted SWAP gates should not exceed max_swaps")
        
        # Check validity of each inserted SWAP gate (physical connectivity)
        for gate in optimized:
            if gate[2] == "SWAP":
                self.assertTrue(self.is_valid_swap(gate, coupling_map),
                                "SWAP gate must operate on physically connected qubits")
    
    def test_complex_circuit(self):
        num_qubits = 4
        circuit = [
            (0, 1, "CNOT", 0.1),
            (2, -1, "H", 0.05),
            (1, 3, "CNOT", 0.2),
            (3, -1, "X", 0.15),
            (0, 2, "CNOT", 0.1),
            (2, -1, "T", 0.1),
            (1, 2, "CNOT", 0.2)
        ]
        coupling_map = [(0, 1), (1, 2), (2, 3), (0, 2)]
        max_swaps = 3
        swap_noise = 0.03
        
        optimized = optimize_circuit(num_qubits, circuit, coupling_map, max_swaps, swap_noise)
        # Check that the original gate order is preserved in non-swap gates.
        non_swap_original = self.extract_non_swap(circuit)
        non_swap_optimized = self.extract_non_swap(optimized)
        self.assertEqual(non_swap_optimized, non_swap_original,
                         "The sequence of original gates must remain intact in the optimized circuit.")
        
        # Verify swap count within the allowed limit
        self.assertLessEqual(self.count_swaps(optimized), max_swaps,
                             "The total number of SWAP gates inserted should be within max_swaps limit")
                             
        # Validate each SWAP gate for proper connectivity.
        for gate in optimized:
            if gate[2] == "SWAP":
                self.assertTrue(self.is_valid_swap(gate, coupling_map),
                                "SWAP gate must connect physically connected qubits as per the coupling map")
        
        # Additional check: ensure the optimized circuit is not empty and has more gates than the original when swaps are inserted.
        self.assertGreaterEqual(len(optimized), len(circuit),
                                "Optimized circuit should have at least as many gates as the original circuit.")

if __name__ == "__main__":
    unittest.main()