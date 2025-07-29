## The Quantum Circuit Optimizer

**Problem Description:**

You are tasked with optimizing a quantum circuit for execution on a noisy intermediate-scale quantum (NISQ) computer. A quantum circuit consists of a sequence of quantum gates acting on qubits. Due to limitations in qubit connectivity and gate fidelity on real quantum hardware, circuit optimization is crucial for achieving meaningful results.

**Input:**

1.  `num_qubits`: An integer representing the number of qubits in the quantum computer (indexed from 0 to `num_qubits - 1`).

2.  `coupling_map`: A list of tuples, where each tuple `(i, j)` indicates that qubits `i` and `j` are physically connected on the quantum chip. Two-qubit gates (e.g., CNOT) can only be directly applied between connected qubits.

3.  `circuit`: A list of operations representing the quantum circuit. Each operation is a tuple: `(gate_name, qubit_indices, parameters)`.

    *   `gate_name`: A string representing the name of the quantum gate (e.g., "H", "CNOT", "RZ", "SWAP").
    *   `qubit_indices`: A list of integers representing the qubit(s) the gate acts on. For example, `["H", [0], []]` means a Hadamard gate on qubit 0, `["CNOT", [0, 1], []]` means a CNOT gate with control qubit 0 and target qubit 1, and `["RZ", [2], [0.5]]` means an RZ gate on qubit 2 with a rotation angle of 0.5 radians.
    *   `parameters`: A list of floating-point numbers representing any parameters required by the gate.  Empty list if no parameters required.

**Gate Definitions:**

*   `H(qubit)`: Hadamard gate on the given qubit.
*   `CNOT(control_qubit, target_qubit)`: Controlled-NOT gate. Requires `control_qubit` and `target_qubit` to be directly connected in the `coupling_map`.
*   `RZ(qubit, angle)`: Rotation around the Z-axis by `angle` radians.
*   `SWAP(qubit1, qubit2)`: Swaps the states of `qubit1` and `qubit2`. Requires `qubit1` and `qubit2` to be directly connected in the `coupling_map`.

**Constraints:**

1.  **Connectivity Constraint:**  `CNOT` and `SWAP` gates can only be applied directly between physically connected qubits according to the `coupling_map`. If a `CNOT` or `SWAP` gate in the input circuit violates this constraint, you must insert a series of `SWAP` gates to bring the involved qubits to adjacent locations before applying the `CNOT` or `SWAP`, and then `SWAP` them back to their initial places.  Minimize the number of inserted `SWAP` gates.

2.  **Optimization Goal:** Your task is to re-write the input `circuit` to satisfy the connectivity constraint while **minimizing the total number of gates (including original gates and inserted SWAP gates) in the optimized circuit.** Note that the number of gates in the optimized circuit must be minimized as the primary objective.

3.  **Heuristics:** Due to the complexity of the problem, finding the absolute optimal solution is computationally expensive. You are expected to implement a *heuristic* algorithm that provides a reasonably good solution within a reasonable time.

4.  **Distance:** You are free to decide the method to calculate the distance between two qubits.

**Output:**

A list of operations representing the optimized quantum circuit, adhering to the connectivity constraint and minimizing the total number of gates.  Each operation in the output list should be in the same tuple format as the input `circuit`.

**Example:**

```python
num_qubits = 3
coupling_map = [(0, 1), (1, 2)]
circuit = [
    ("H", [0], []),
    ("CNOT", [0, 2], []),  # Violates connectivity constraint
    ("H", [2], [])
]
```

A possible (but not necessarily optimal) solution could involve inserting `SWAP` gates to move qubit 2 next to qubit 0:

```python
optimized_circuit = [
    ("H", [0], []),
    ("SWAP", [1, 2], []),
    ("CNOT", [0, 1], []),
    ("SWAP", [1, 2], []),
    ("H", [2], [])
]
```

**Scoring:**

The solution will be evaluated based on the following criteria:

1.  **Correctness:** The optimized circuit must perform the same quantum operation as the original circuit (i.e., be logically equivalent).
2.  **Gate Count:** The number of gates in the optimized circuit should be minimized. Solutions with fewer gates will receive higher scores.
3.  **Runtime:** The solution must execute within a reasonable time limit.

**Note:** This problem requires a good understanding of quantum computing concepts, graph algorithms (for finding shortest paths on the coupling map), and heuristic optimization techniques. It is designed to be challenging and requires careful consideration of different algorithmic approaches and trade-offs.
