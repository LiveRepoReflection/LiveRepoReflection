import unittest

from quantum_compile import compile_circuit

def simulate_compiled_circuit(compiled_circuit, architecture, num_qubits):
    """
    Simulates the execution of the compiled circuit.
    Maintains a mapping from physical qubits to the logical qubits they hold.
    Initially, physical qubit i holds logical qubit i.
    For each gate in the compiled circuit:
      - "SWAP": swap the logical qubits between the two physical qubits.
      - "H": no mapping change.
      - "CNOT": checks that the two physical qubits currently hold qubits that are adjacent in the architecture.
    Returns the final mapping as a list where index is the physical qubit and value is the logical qubit.
    """
    # Initial mapping: physical qubit i holds logical qubit i
    mapping = list(range(num_qubits))
    
    for gate in compiled_circuit:
        gate_type, q1, q2 = gate
        if gate_type == "SWAP":
            # q1 and q2 are physical qubit indices, swap the logical qubits they hold.
            mapping[q1], mapping[q2] = mapping[q2], mapping[q1]
        elif gate_type == "H":
            # Single qubit gate; nothing changes.
            # But we assume that the gate is applied to the physical qubit q2.
            pass
        elif gate_type == "CNOT":
            # CNOT gate: check that physical qubits q1 (control) and q2 (target) are connected.
            if q2 not in architecture.get(q1, []):
                raise AssertionError(f"CNOT gate applied on non-adjacent qubits: {q1} and {q2}")
            # No mapping change for CNOT.
        else:
            raise AssertionError(f"Unknown gate type encountered: {gate_type}")
    return mapping

def count_gate_type(compiled_circuit, gate_type):
    return sum(1 for gate in compiled_circuit if gate[0] == gate_type)

class TestQuantumCompile(unittest.TestCase):
    def test_no_swap_needed(self):
        # Architecture: simple connectivity; two qubits directly connected.
        architecture = {
            0: [1],
            1: [0]
        }
        # Circuit: direct application of gates; no SWAP should be inserted.
        circuit = [
            ("H", None, 0),
            ("CNOT", 0, 1),
            ("H", None, 1)
        ]
        compiled = compile_circuit(architecture, circuit)
        # For a two-qubit system.
        num_qubits = 2
        
        # Check that there are no SWAP gates in the compiled circuit.
        self.assertEqual(count_gate_type(compiled, "SWAP"), 0)
        
        # Simulate the circuit, verifying that every CNOT is applied on adjacent physical qubits.
        final_mapping = simulate_compiled_circuit(compiled, architecture, num_qubits)
        # Final mapping must be identity to preserve the original computation.
        self.assertEqual(final_mapping, list(range(num_qubits)))
    
    def test_single_swap_insertion(self):
        # Architecture: 3 qubits in a line: 0 - 1 - 2.
        architecture = {
            0: [1],
            1: [0, 2],
            2: [1]
        }
        # Circuit requiring swap: a CNOT between qubits 0 and 2 cannot be directly applied.
        circuit = [
            ("H", None, 0),
            ("CNOT", 0, 2)
        ]
        compiled = compile_circuit(architecture, circuit)
        num_qubits = 3
        
        # There should be at least one SWAP gate inserted.
        self.assertGreaterEqual(count_gate_type(compiled, "SWAP"), 1)
        
        # Simulate the compiled circuit to validate CNOT connectivity and final mapping.
        final_mapping = simulate_compiled_circuit(compiled, architecture, num_qubits)
        self.assertEqual(final_mapping, list(range(num_qubits)))
    
    def test_multiple_swaps(self):
        # Architecture: 4 qubits in a square.
        architecture = {
            0: [1, 2],
            1: [0, 3],
            2: [0, 3],
            3: [1, 2]
        }
        # Circuit: multiple CNOTs that require swaps to be adjacent.
        circuit = [
            ("H", None, 0),
            ("H", None, 1),
            ("CNOT", 0, 3),
            ("CNOT", 2, 1),
            ("H", None, 0)
        ]
        compiled = compile_circuit(architecture, circuit)
        num_qubits = 4
        
        # At least one SWAP must be inserted.
        self.assertGreaterEqual(count_gate_type(compiled, "SWAP"), 2)
        
        # Simulate the circuit.
        final_mapping = simulate_compiled_circuit(compiled, architecture, num_qubits)
        self.assertEqual(final_mapping, list(range(num_qubits)))
    
    def test_preserve_gate_order(self):
        # Architecture: line of 3 qubits: 0 - 1 - 2.
        architecture = {
            0: [1],
            1: [0, 2],
            2: [1]
        }
        # Circuit with multiple gates.
        circuit = [
            ("H", None, 0),
            ("CNOT", 0, 2),
            ("H", None, 1),
            ("CNOT", 2, 0),
            ("H", None, 2)
        ]
        compiled = compile_circuit(architecture, circuit)
        num_qubits = 3
        
        # Verify that non-swap gates order is preserved.
        original_non_swap = [gate for gate in circuit]
        compiled_non_swap = [gate for gate in compiled if gate[0] in {"H", "CNOT"}]
        self.assertEqual(len(compiled_non_swap), len(original_non_swap))
        # Check that each non-swap gate in compiled circuit corresponds in type to the original order.
        for orig_gate, comp_gate in zip(original_non_swap, compiled_non_swap):
            self.assertEqual(orig_gate[0], comp_gate[0])
        
        final_mapping = simulate_compiled_circuit(compiled, architecture, num_qubits)
        self.assertEqual(final_mapping, list(range(num_qubits)))
    
    def test_complex_architecture(self):
        # Architecture: a more complex graph with 5 qubits.
        architecture = {
            0: [1, 2],
            1: [0, 3],
            2: [0, 3, 4],
            3: [1, 2, 4],
            4: [2, 3]
        }
        # Circuit: series of gates that require non-trivial swaps.
        circuit = [
            ("H", None, 0),
            ("CNOT", 0, 4),
            ("H", None, 2),
            ("CNOT", 2, 1),
            ("CNOT", 4, 3),
            ("H", None, 4)
        ]
        compiled = compile_circuit(architecture, circuit)
        num_qubits = 5
        
        # Ensure that each CNOT in the compiled circuit is applied on adjacent physical qubits.
        final_mapping = simulate_compiled_circuit(compiled, architecture, num_qubits)
        self.assertEqual(final_mapping, list(range(num_qubits)))
        
        # Check that some swaps are inserted.
        self.assertGreater(count_gate_type(compiled, "SWAP"), 0)

if __name__ == "__main__":
    unittest.main()