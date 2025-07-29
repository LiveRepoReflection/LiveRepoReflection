## Quantum Circuit Compilation Optimization

**Problem Description:**

Quantum computing promises to revolutionize computation, but current quantum devices (quantum computers) are limited by the number of qubits and the fidelity of quantum gates. Compiling a quantum algorithm into a sequence of gates that can be executed on a specific quantum computer is a crucial step. This compilation process often requires optimizing the circuit to reduce the number of gates, especially two-qubit gates (e.g., CNOT), which are typically the most error-prone.

You are given a target quantum computer architecture represented as a connected, undirected graph, where each node represents a qubit, and an edge between two nodes indicates that a two-qubit gate can be directly implemented between those qubits. You are also given a quantum circuit represented as a sequence of quantum gates.

Your task is to implement an algorithm that optimizes the given quantum circuit for the target quantum computer architecture. Specifically, you need to minimize the number of SWAP gates required to execute the circuit on the target architecture. A SWAP gate exchanges the quantum states of two qubits and can be directly implemented only between adjacent qubits in the architecture graph.

**Input:**

1.  **Architecture Graph:** A dictionary where the keys are qubit IDs (integers starting from 0) and the values are lists of adjacent qubit IDs. For example:

    ```python
    architecture = {
        0: [1, 2],
        1: [0, 3],
        2: [0, 3],
        3: [1, 2]
    }
    ```

2.  **Quantum Circuit:** A list of quantum gates. Each gate is a tuple: `(gate_type, qubit1, qubit2)`.
    *   `gate_type`: A string representing the type of gate. Can be "CNOT" (Controlled-NOT gate) or "H" (Hadamard gate).  For simplicity, you only need to consider these two gate types.
    *   `qubit1`, `qubit2`: Integers representing the qubit IDs involved in the gate. For "CNOT", `qubit1` is the control qubit and `qubit2` is the target qubit. For "H", `qubit2` is the target qubit, and `qubit1` is always `None`.

    For example:

    ```python
    circuit = [
        ("H", None, 0),
        ("H", None, 1),
        ("CNOT", 0, 3),
        ("CNOT", 2, 1),
        ("H", None, 0)
    ]
    ```

**Output:**

A list of quantum gates representing the optimized circuit. This optimized circuit must include:

*   Original gates from the initial circuit.
*   SWAP gates (represented as `("SWAP", qubit1, qubit2)`) inserted to move qubits adjacent to each other so that the original gates can be executed on the architecture.
*   All the gate orders are still valid.

**Constraints:**

1.  The architecture graph is connected.
2.  Qubit IDs are non-negative integers.
3.  The circuit can contain an arbitrary number of gates.
4.  The number of qubits implied by the architecture and the circuit should be consistent.
5.  You must minimize the *total* number of SWAP gates inserted. Note that minimizing swaps locally at each gate may not lead to a global minimum.
6.  If a CNOT gate can be executed directly on the architecture (i.e., there's an edge between the two qubits), no SWAP gates should be inserted immediately before it.
7.  No gate reordering is allowed other than the insertion of SWAP gates immediately before CNOT gates. The SWAP gates you insert should be only right before the related CNOT gate.
8.  Optimize for efficiency. Brute-force approaches that explore all possible SWAP sequences may time out for larger circuits or architectures.

**Example:**

```python
architecture = {
    0: [1],
    1: [0, 2],
    2: [1]
}

circuit = [
    ("H", None, 0),
    ("CNOT", 0, 2),
    ("H", None, 1)
]
```

A possible (though not necessarily optimal) output might be:

```python
[
    ("H", None, 0),
    ("SWAP", 1, 2),
    ("CNOT", 0, 1),
    ("SWAP", 1, 2),
    ("H", None, 1)
]
```
Note that after inserting the first SWAP gate, qubits 1 and 2 are swapped. Thus, CNOT(0,2) can be executed by CNOT(0,1). In order to preserve the original computation, you need to swap the qubits back.

**Grading:**

The solution will be graded based on:

1.  **Correctness:** The optimized circuit must perform the same quantum computation as the original circuit (i.e., the inserted SWAP gates correctly re-arrange the qubits, and the circuit logic is preserved after the swaps).
2.  **Optimization:** The number of SWAP gates inserted should be minimized.  Solutions with significantly more SWAP gates than necessary will receive partial credit.
3.  **Efficiency:** The algorithm should be able to handle reasonably sized circuits and architectures within a reasonable time limit.
4.  **Clarity and Readability:** The code should be well-structured and easy to understand.

This problem requires a combination of graph algorithms (finding shortest paths), state management (keeping track of qubit positions after SWAP gates), and potentially heuristics or search algorithms to find good solutions in a reasonable time. Good luck!
