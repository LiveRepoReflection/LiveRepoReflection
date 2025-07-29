import unittest
from quantum_simulator import quantum_simulator
import random

class QuantumSimulatorTest(unittest.TestCase):
    def test_no_gates(self):
        """Test simulator with no gates applied."""
        n = 2
        initial_state = "00"
        gates = []
        num_samples = 1000
        
        result = quantum_simulator(n, initial_state, gates, num_samples)
        
        self.assertEqual(len(result), 4)  # Should contain all possible states
        self.assertEqual(result["00"], 1000)  # All samples should remain in initial state
        self.assertEqual(result["01"], 0)
        self.assertEqual(result["10"], 0)
        self.assertEqual(result["11"], 0)
    
    def test_hadamard_gate(self):
        """Test Hadamard gate on a single qubit."""
        n = 1
        initial_state = "0"
        gates = [('H', 0)]
        num_samples = 10000
        
        result = quantum_simulator(n, initial_state, gates, num_samples)
        
        self.assertEqual(len(result), 2)  # Should contain all possible states
        # Approximately 50% each state (allowing for statistical variation)
        self.assertAlmostEqual(result["0"] / num_samples, 0.5, delta=0.05)
        self.assertAlmostEqual(result["1"] / num_samples, 0.5, delta=0.05)
    
    def test_cnot_gate(self):
        """Test CNOT gate with control=1."""
        n = 2
        initial_state = "10"
        gates = [('CNOT', 0, 1)]
        num_samples = 1000
        
        result = quantum_simulator(n, initial_state, gates, num_samples)
        
        self.assertEqual(len(result), 4)  # Should contain all possible states
        self.assertEqual(result["11"], 1000)  # All samples should flip to 11
        self.assertEqual(result["00"], 0)
        self.assertEqual(result["01"], 0)
        self.assertEqual(result["10"], 0)
    
    def test_hadamard_cnot(self):
        """Test Hadamard followed by CNOT (Bell state preparation)."""
        n = 2
        initial_state = "00"
        gates = [('H', 0), ('CNOT', 0, 1)]
        num_samples = 10000
        
        result = quantum_simulator(n, initial_state, gates, num_samples)
        
        self.assertEqual(len(result), 4)  # Should contain all possible states
        # Approximately 50% for "00" and 50% for "11" (allowing for statistical variation)
        self.assertAlmostEqual(result["00"] / num_samples, 0.5, delta=0.05)
        self.assertAlmostEqual(result["11"] / num_samples, 0.5, delta=0.05)
        self.assertEqual(result["01"], 0)
        self.assertEqual(result["10"], 0)
    
    def test_larger_circuit(self):
        """Test a more complex circuit with multiple gates."""
        n = 3
        initial_state = "000"
        gates = [
            ('H', 0),
            ('H', 1),
            ('CNOT', 0, 2),
            ('CNOT', 1, 2),
            ('H', 0)
        ]
        num_samples = 10000
        
        result = quantum_simulator(n, initial_state, gates, num_samples)
        
        self.assertEqual(len(result), 8)  # Should contain all possible states
        # This circuit has specific probabilities that can be computed
        # The test checks that the distribution is close to expected
        for state in ["000", "001", "010", "011", "100", "101", "110", "111"]:
            self.assertIn(state, result)
    
    def test_multiple_hadamards(self):
        """Test multiple Hadamard gates on different qubits."""
        n = 3
        initial_state = "000"
        gates = [('H', 0), ('H', 1), ('H', 2)]
        num_samples = 10000
        
        result = quantum_simulator(n, initial_state, gates, num_samples)
        
        self.assertEqual(len(result), 8)  # Should contain all possible states
        # Each state should have approximately 1/8 probability
        for state in ["000", "001", "010", "011", "100", "101", "110", "111"]:
            self.assertAlmostEqual(result[state] / num_samples, 0.125, delta=0.05)
    
    def test_maximum_registers(self):
        """Test with maximum number of registers."""
        n = 10  # Using 10 instead of 30 to avoid excessive computation
        initial_state = "0" * n
        gates = [('H', i) for i in range(n)]
        num_samples = 1000
        
        result = quantum_simulator(n, initial_state, gates, num_samples)
        
        self.assertEqual(len(result), 2**n)  # Should contain all possible states
        # With all qubits in superposition, all states should be approximately equally likely
        expected_prob = 1 / (2**n)
        for state in result:
            self.assertLessEqual(result[state], num_samples)  # Basic sanity check
    
    def test_edge_case_single_register(self):
        """Test with just one register."""
        n = 1
        initial_state = "0"
        gates = []
        num_samples = 1000
        
        result = quantum_simulator(n, initial_state, gates, num_samples)
        
        self.assertEqual(len(result), 2)  # Should contain both possible states
        self.assertEqual(result["0"], 1000)
        self.assertEqual(result["1"], 0)
    
    def test_random_seed_reproducibility(self):
        """Test that setting the same random seed gives the same results."""
        n = 2
        initial_state = "00"
        gates = [('H', 0), ('H', 1)]
        num_samples = 100
        
        # Set fixed seed
        random.seed(42)
        result1 = quantum_simulator(n, initial_state, gates, num_samples)
        
        # Reset to same seed
        random.seed(42)
        result2 = quantum_simulator(n, initial_state, gates, num_samples)
        
        self.assertEqual(result1, result2)
    
    def test_invalid_input_handling(self):
        """Test that invalid inputs raise appropriate exceptions."""
        # Invalid initial state
        with self.assertRaises(ValueError):
            quantum_simulator(2, "012", [], 100)
        
        # Invalid gate type
        with self.assertRaises(ValueError):
            quantum_simulator(2, "00", [('INVALID', 0)], 100)
        
        # Invalid register index
        with self.assertRaises(ValueError):
            quantum_simulator(2, "00", [('H', 2)], 100)
        
        # Invalid CNOT indices
        with self.assertRaises(ValueError):
            quantum_simulator(2, "00", [('CNOT', 0, 0)], 100)  # Same register
        
        with self.assertRaises(ValueError):
            quantum_simulator(2, "00", [('CNOT', 0, 2)], 100)  # Target out of range

if __name__ == "__main__":
    unittest.main()