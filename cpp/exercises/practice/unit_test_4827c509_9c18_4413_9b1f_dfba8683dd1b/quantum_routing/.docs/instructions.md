## The Quantum Network Routing Problem

**Problem Description:**

You are tasked with designing a routing algorithm for a novel quantum communication network. This network consists of `N` quantum nodes, each capable of processing and forwarding qubits. Unlike classical networks, quantum communication faces unique challenges due to the principles of quantum mechanics, specifically entanglement and decoherence.

The network topology is represented as a weighted undirected graph. Each node represents a quantum computer, and each edge between two nodes represents a quantum channel capable of transmitting qubits. The weight of an edge represents the *fidelity* of the quantum channel, a value between 0 and 1 inclusive, representing the probability that a qubit transmitted across the channel will remain in its intended state.  Lower fidelity indicates a greater chance of decoherence, which corrupts the quantum information.

A key feature of this network is the ability to perform *entanglement swapping*. When two nodes share an entangled pair of qubits, and each node also shares an entangled pair with a third node, the two end nodes can establish an entangled pair via a process that "swaps" the entanglement. This is crucial for long-distance quantum communication.  Entanglement swapping can only be done between adjacent nodes.

Your task is to implement a function that finds the optimal path for transmitting a quantum state (qubit) from a source node `S` to a destination node `D`, maximizing the overall probability of successful transmission. This "success probability" is calculated as the product of the fidelities of the edges along the path, multiplied by a penalty factor for each entanglement swap performed.

**Input:**

*   `N`: The number of quantum nodes in the network (1 <= N <= 1000). Nodes are numbered from 0 to N-1.
*   `edges`: A vector of tuples, where each tuple `(u, v, fidelity)` represents an undirected edge between node `u` and node `v` with fidelity `fidelity` (0 <= u, v < N, 0 <= fidelity <= 1). There can be multiple edges between the same two nodes, and self-loops are not allowed.
*   `S`: The source node (0 <= S < N).
*   `D`: The destination node (0 <= D < N, S != D).
*   `swap_penalty`: A double value (0 < swap_penalty < 1) representing the penalty factor applied for each entanglement swap performed along the path. This penalty reflects the overhead and potential errors introduced by swapping.

**Output:**

A double value representing the maximum probability of successfully transmitting a qubit from node `S` to node `D`. If no path exists between `S` and `D`, return 0.0.

**Constraints and Considerations:**

*   **Path Finding:** You need to find a path from `S` to `D` that may involve multiple entanglement swaps.
*   **Entanglement Swaps:** Entanglement swaps can only occur at intermediate nodes along the path. The number of entanglement swaps directly impacts the success probability through the `swap_penalty`.
*   **Optimization:** You need to find the path that *maximizes* the overall success probability, considering both edge fidelities and the swap penalty. A naive shortest path algorithm won't work because it doesn't account for the swap penalty.
*   **Multiple Edges:** Your algorithm must handle the possibility of multiple edges between the same two nodes, choosing the edge with the highest fidelity for each connection.
*   **Computational Complexity:** Given the constraints on `N`, aim for an algorithm with reasonable time complexity. Consider that the graph may be dense.
*   **Large graphs and edge cases**: The graph may not be fully connected and may contain cycles.

**Example:**

```
N = 4
edges = {(0, 1, 0.9), (1, 2, 0.8), (2, 3, 0.7), (0, 2, 0.6)}
S = 0
D = 3
swap_penalty = 0.9

Possible paths:

1. Direct path using edges (0,1), (1,2), (2,3): Probability = 0.9 * 0.8 * 0.7 = 0.504.  Swaps = 2
Final probability = 0.504 * 0.9 * 0.9 = 0.40824
2. Direct path using edges (0,2), (2,3): Probability = 0.6 * 0.7 = 0.42. Swaps = 1
Final probability = 0.42 * 0.9 = 0.378

Optimal path: Path 1

Output: 0.40824
```

**Grading:**

The solution will be judged based on:

*   **Correctness:** The solution must produce the correct maximum probability for all valid inputs.
*   **Efficiency:** The solution should have a reasonable time complexity for the given constraints.
*   **Code Clarity:** The code should be well-structured, readable, and maintainable.
*   **Handling Edge Cases:** The solution should gracefully handle edge cases, such as disconnected graphs or invalid inputs.
