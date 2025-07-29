## Quantum Network Optimization

Imagine you are designing a quantum communication network connecting `n` quantum computers distributed geographically. Each quantum computer is a node in your network. Due to physical limitations, not every pair of quantum computers can directly communicate. The ability to directly communicate is represented by edges in a graph.

Each potential communication link (edge) between two quantum computers `u` and `v` has a associated *entanglement cost* `c(u, v)` and a *fidelity* `f(u, v)`. Entanglement cost represents the amount of quantum resources needed to establish the link, and fidelity represents the quality of the quantum connection (higher is better).

Given two specific quantum computers, a *source* `s` and a *destination* `d`, you need to establish a quantum communication path between them. This path might involve multiple intermediate quantum computers relaying the quantum information. The fidelity of a path is the *product* of the fidelities of all the links in the path. The cost of a path is the *sum* of the entanglement costs of all the links in the path.

Your task is to design an algorithm to find the *minimum cost* path between the source `s` and destination `d` such that the fidelity of the path is *at least* a given threshold `F`.

**Input:**

*   `n`: The number of quantum computers (nodes), numbered from 0 to `n-1`.
*   `edges`: A list of tuples `(u, v, c, f)` representing the potential communication links, where:
    *   `u` and `v` are the indices of the quantum computers connected by the link (0 <= `u`, `v` < `n`).
    *   `c` is the entanglement cost of the link (0 <= `c` <= 1000).
    *   `f` is the fidelity of the link (0 < `f` <= 1.0).
*   `s`: The index of the source quantum computer (0 <= `s` < `n`).
*   `d`: The index of the destination quantum computer (0 <= `d` < `n`).
*   `F`: The minimum required fidelity of the path (0 < `F` <= 1.0).

**Output:**

*   The minimum entanglement cost of a path between `s` and `d` with fidelity at least `F`. If no such path exists, return `-1`.

**Constraints:**

*   1 <= `n` <= 1000
*   0 <= number of `edges` <= `n * (n - 1) / 2`
*   The graph is undirected (if `(u, v, c, f)` exists, then `(v, u, c, f)` is also implicitly defined).
*   There may be multiple edges between the same pair of nodes.
*   The graph may not be fully connected.
*   Consider potential floating point precision issues when dealing with fidelity calculation.

**Optimization Requirements:**

*   The algorithm should be efficient in terms of time complexity.  Aim for a solution significantly better than brute-force (exploring all possible paths).
*   Consider how to handle potential cycles in the graph.
*   Think about data structures that can efficiently store and retrieve path costs and fidelities.

**Example:**

```
n = 5
edges = [[0, 1, 10, 0.9], [0, 2, 15, 0.8], [1, 2, 5, 0.95], [1, 3, 12, 0.85], [2, 4, 8, 0.9], [3, 4, 7, 0.92]]
s = 0
d = 4
F = 0.65

Output: 30

Explanation:
One possible path is 0 -> 2 -> 4.  The cost is 15 + 8 = 23, and the fidelity is 0.8 * 0.9 = 0.72 >= 0.65.
Another possible path is 0 -> 1 -> 2 -> 4. The cost is 10 + 5 + 8 = 23, and the fidelity is 0.9 * 0.95 * 0.9 = 0.7695 >= 0.65.
Another possible path is 0 -> 1 -> 3 -> 4.  The cost is 10 + 12 + 7 = 29, and the fidelity is 0.9 * 0.85 * 0.92 = 0.7062 >= 0.65.
The optimal path is 0 -> 2 -> 4 with a cost of 23.

Another Path is 0->1->2->4 with a cost of 23 and a fidelity of 0.7695
```

```
n = 3
edges = [[0, 1, 5, 0.5], [1, 2, 7, 0.6]]
s = 0
d = 2
F = 0.3

Output: 12
```

```
n = 3
edges = [[0, 1, 5, 0.5], [1, 2, 7, 0.6]]
s = 0
d = 2
F = 0.4

Output: -1
```
