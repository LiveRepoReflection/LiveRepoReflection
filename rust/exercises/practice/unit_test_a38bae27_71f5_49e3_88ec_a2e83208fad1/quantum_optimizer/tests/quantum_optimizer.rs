use quantum_optimizer::optimize_circuit;

#[cfg(test)]
mod tests {
    use super::optimize_circuit;

    #[test]
    fn test_empty_circuit() {
        let num_qubits = 3;
        let gates: Vec<(u32, Vec<usize>)> = vec![];
        let dependencies: Vec<(usize, usize)> = vec![];
        let result = optimize_circuit(num_qubits, gates, dependencies);
        let expected: Vec<(u32, Vec<usize>)> = vec![];
        assert_eq!(result, expected);
    }

    #[test]
    fn test_consecutive_hadamards() {
        // Two consecutive Hadamard gates on the same qubit should cancel out.
        let num_qubits = 1;
        let gates = vec![(1, vec![0]), (1, vec![0])];
        let dependencies: Vec<(usize, usize)> = vec![];
        let result = optimize_circuit(num_qubits, gates, dependencies);
        // Both Hadamard gates cancel, resulting in an empty circuit.
        let expected: Vec<(u32, Vec<usize>)> = vec![];
        assert_eq!(result, expected);
    }

    #[test]
    fn test_sample_input() {
        // Provided sample from the problem description.
        // Circuit: H on qubit 0, H on qubit 0, CNOT(0,1), H on qubit 1.
        // Dependencies: (0 -> 2), (1 -> 2), (2 -> 3)
        let num_qubits = 2;
        let gates = vec![
            (1, vec![0]),
            (1, vec![0]),
            (2, vec![0, 1]),
            (1, vec![1]),
        ];
        let dependencies = vec![(0, 2), (1, 2), (2, 3)];
        let result = optimize_circuit(num_qubits, gates, dependencies);
        let expected = vec![(2, vec![0, 1]), (1, vec![1])];
        assert_eq!(result, expected);
    }
    
    #[test]
    fn test_commutation_on_disjoint_qubits() {
        // Gates on disjoint qubits with no dependencies.
        // Two Hadamard gates on qubit 0 and two on qubit 1 should cancel out.
        let num_qubits = 2;
        let gates = vec![
            (1, vec![0]),
            (1, vec![1]),
            (1, vec![0]),
            (1, vec![1]),
        ];
        let dependencies: Vec<(usize, usize)> = vec![];
        let result = optimize_circuit(num_qubits, gates, dependencies);
        // Expected output is an empty circuit after cancellation.
        let expected: Vec<(u32, Vec<usize>)> = vec![];
        assert_eq!(result, expected);
    }
    
    #[test]
    fn test_no_commutation_due_to_dependency() {
        // Even if gates act on different qubits, dependencies might prevent reordering.
        // In this circuit, dependencies force the order so that no fusion is possible.
        let num_qubits = 2;
        let gates = vec![
            (1, vec![0]), // H on q0
            (1, vec![1]), // H on q1
            (1, vec![0]), // H on q0
            (1, vec![1]), // H on q1
        ];
        // Force each gate to depend on the previous one.
        let dependencies = vec![(0, 1), (1, 2), (2, 3)];
        let result = optimize_circuit(num_qubits, gates, dependencies);
        // Since the dependencies force the order, no consecutive gates on the same qubit are adjacent.
        // Thus, no cancellation occurs.
        let expected = vec![
            (1, vec![0]),
            (1, vec![1]),
            (1, vec![0]),
            (1, vec![1]),
        ];
        assert_eq!(result, expected);
    }
    
    #[test]
    fn test_mixed_circuit() {
        // A more complex circuit mixing cancellation, commutation, and dependencies.
        // Circuit breakdown:
        // 0: H on q0
        // 1: T on q0
        // 2: H on q1
        // 3: H on q0
        // 4: H on q0  -> these two H's on q0 (indices 3 and 4) cancel.
        // 5: CNOT on q0 and q1
        // 6: T on q0
        // 7: T on q1
        //
        // Dependencies force:
        // 0 -> 5, 1 -> 5, 2 -> 5, 5 -> 6, 5 -> 7.
        let num_qubits = 2;
        let gates = vec![
            (1, vec![0]),  // index 0: H on q0
            (3, vec![0]),  // index 1: T on q0
            (1, vec![1]),  // index 2: H on q1
            (1, vec![0]),  // index 3: H on q0
            (1, vec![0]),  // index 4: H on q0 (should cancel with index 3)
            (2, vec![0, 1]),// index 5: CNOT(0,1)
            (3, vec![0]),  // index 6: T on q0
            (3, vec![1]),  // index 7: T on q1
        ];
        let dependencies = vec![
            (0, 5),
            (1, 5),
            (2, 5),
            (5, 6),
            (5, 7),
        ];
        let result = optimize_circuit(num_qubits, gates, dependencies);
        // Expected optimized circuit:
        // Index 3 and 4 cancel each other.
        // Final sequence:
        // 0: H on q0
        // 1: T on q0
        // 2: H on q1
        // 5: CNOT(0,1)
        // 6: T on q0
        // 7: T on q1
        let expected = vec![
            (1, vec![0]),
            (3, vec![0]),
            (1, vec![1]),
            (2, vec![0, 1]),
            (3, vec![0]),
            (3, vec![1]),
        ];
        assert_eq!(result, expected);
    }
}