Okay, I'm ready to craft a challenging problem. Here it is:

### Project Name

```
network-dominating-set
```

### Question Description

You are given a representation of a communication network as an undirected graph. The nodes of the graph represent devices, and the edges represent direct communication links between devices.  Each device has a unique ID, represented by a positive integer.

A *Dominating Set* in a graph is a subset of nodes such that every node in the graph is either in the set itself, or adjacent to at least one node in the set.  In simpler terms, every device in the network is either a member of the dominating set, or has a direct communication link with a device that *is* in the dominating set.

A *Minimum Dominating Set* is a dominating set with the smallest possible number of nodes. Finding the absolute minimum dominating set is an NP-hard problem. Instead, we focus on finding an efficient *Network-Aware Dominating Set* that minimizes the communication overhead.

**Your Task:**

You are tasked with implementing an algorithm that finds a "good" (but not necessarily minimal) dominating set for the given communication network, prioritizing network resilience and operational efficiency.

**Input:**

The input will be provided as:

1.  **`n`**: An integer representing the number of devices (nodes) in the network. Devices are numbered from `1` to `n`.
2.  **`edges`**: A list of tuples, where each tuple `(u, v)` represents an undirected communication link (edge) between device `u` and device `v`.

**Output:**

Return a *sorted list* of device IDs (integers) that form your computed dominating set.

**Constraints and Requirements:**

1.  `1 <= n <= 100,000` (Number of nodes)
2.  `0 <= len(edges) <= 200,000` (Number of edges)
3.  Device IDs are integers from `1` to `n`.
4.  The graph is undirected and may contain cycles, but will not contain self-loops (an edge from a node to itself) or parallel edges (multiple edges between the same two nodes).
5.  Your solution **must** run within a time limit of **2 seconds** on standard test cases. Solutions exceeding this time limit will be terminated.
6.  The quality of your dominating set will be evaluated based on its size relative to the optimal dominating set (which is unknown to you). Solutions that produce significantly larger dominating sets may be penalized.
7.   **Operational Efficiency:** Prioritize selecting nodes with higher degrees (more connections) into the dominating set. This simulates choosing devices that are more centrally located and can cover more of the network.
8.  **Network Resilience:** If multiple nodes have similar degrees, prioritize selecting nodes that, when added to the dominating set, cover nodes that have the fewest remaining uncovered neighbors. This prevents creating isolated uncovered regions in the network and improves resilience.

**Example:**

```
n = 6
edges = [(1, 2), (1, 3), (2, 4), (3, 4), (3, 5), (5, 6)]

# One possible valid output:
# [1, 3, 6]  (Device 1 covers 2 and 3, Device 3 covers 1, 4, and 5, Device 6 covers 5).
# Another possible valid output:
# [2, 3, 5] (Device 2 covers 1 and 4, Device 3 covers 1, 4 and 5, Device 5 covers 3 and 6)
```

**Judging Criteria:**

Your solution will be judged on:

*   **Correctness:**  Does the returned set actually form a dominating set for the input graph?
*   **Efficiency:**  Does your solution run within the time limit for large graphs?
*   **Optimality:**  How close is the size of your dominating set to a reasonable (though not necessarily minimal) size? This will be evaluated by comparing your solution against other valid solutions.

Good luck! This problem requires a thoughtful combination of graph algorithms, data structures, and optimization techniques.
