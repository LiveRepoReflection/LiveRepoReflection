## The Quantum Circuit Optimizer

### Question Description

You are tasked with optimizing a quantum circuit for execution on a noisy quantum computer. Quantum circuits are represented as a directed acyclic graph (DAG) where nodes are quantum gates and edges represent the flow of qubits. Each gate has an associated noise level, and the overall circuit fidelity is inversely proportional to the cumulative noise introduced by the gates along the critical path (the path with the highest cumulative noise). Your goal is to minimize the total noise introduced along the critical path by strategically inserting swap gates to re-route qubits and potentially avoid noisy gates.

**Input:**

*   **`num_qubits`**: An integer representing the number of qubits in the quantum computer. (1 <= `num_qubits` <= 16)
*   **`circuit`**: A list of tuples, where each tuple represents a quantum gate in the form `(qubit1, qubit2, gate_type, noise_level)`.

    *   `qubit1`, `qubit2`: Integers representing the qubit indices the gate operates on (0-indexed). If the gate operates on a single qubit, `qubit2` will be `-1`.
    *   `gate_type`: A string representing the type of quantum gate. Possible values: `"H"` (Hadamard), `"X"` (Pauli-X), `"CNOT"` (Controlled-NOT), `"T"` (T gate), `"SWAP"` (Swap gate).  You *cannot* change the `gate_type` of the initial gates.  You can *only* add `SWAP` gates.
    *   `noise_level`: A floating-point number representing the noise introduced by the gate.
*   **`coupling_map`**: A list of tuples representing the physical connectivity of the qubits on the quantum computer. Each tuple `(qubit_a, qubit_b)` indicates that qubits `qubit_a` and `qubit_b` are physically connected and can be directly swapped via a `SWAP` gate.
*   **`max_swaps`**: An integer representing the maximum number of `SWAP` gates that can be inserted into the circuit.  Inserting a swap gate can only happen between the existing gates from the input `circuit`.
*   **`swap_noise`**: A float representing the noise introduced by each `SWAP` gate.  This value is constant for all `SWAP` gates.

**Output:**

*   A list of tuples representing the optimized quantum circuit. The format is the same as the input `circuit`, but with potentially added `SWAP` gates. The optimized circuit *must* perform the same logical operation as the original circuit, but may have a different qubit mapping due to the added swaps.

**Constraints:**

*   The output circuit must implement the same logical operation as the original circuit. The added `SWAP` gates should only change the physical qubit mapping, not the overall computation.
*   You cannot change the order of the original gates in the circuit. You can only insert `SWAP` gates *between* existing gates.
*   The number of `SWAP` gates you insert must not exceed `max_swaps`.
*   `SWAP` gates can only be inserted between physically connected qubits as defined in the `coupling_map`.
*   The goal is to *minimize the cumulative noise along the critical path* in the optimized circuit.  The critical path is defined as the path (sequence of gates) from the beginning to the end of the circuit that has the highest sum of `noise_level` values.  If multiple paths have the same highest sum, then the one that reaches the end later is considered the critical path.  If they reach the end at the same time, any of them can be considered the critical path.
*   `num_qubits`, `len(circuit)`, `len(coupling_map)`, `max_swaps` are all less than or equal to 16.
*   `noise_level` and `swap_noise` are non-negative floating-point numbers.
*   All qubit indices are valid (i.e., within the range `0` to `num_qubits - 1`).

**Example:**

```python
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

# Possible optimized circuit (example only - your solution needs to minimize critical path noise):
optimized_circuit = [
    (0, 1, "CNOT", 0.1),
    (1, 2, "SWAP", 0.02),  # Inserted SWAP
    (2, -1, "H", 0.05),
    (1, 2, "SWAP", 0.02),  # Inserted SWAP
    (0, 1, "CNOT", 0.2),
    (1, -1, "X", 0.15)
]
```

**Judging Criteria:**

The solution will be judged based on the cumulative noise along the critical path in the optimized circuit, compared to the cumulative noise along the critical path in the original circuit. The lower the cumulative noise, the better the score. Solutions exceeding `max_swaps` or that change the logical operation of the circuit will be penalized. The solution that fails to produce an output in a reasonable time will be terminated.

**Hints:**

*   Consider using dynamic programming or search algorithms to explore the possible swap gate insertions.
*   Implement a function to efficiently calculate the critical path and its cumulative noise.
*   Think about how to track the qubit mapping as you insert swap gates.
*   Prioritize swapping qubits away from noisy gates on the critical path.
*   Be mindful of time complexity. Brute force will likely not be efficient enough.
