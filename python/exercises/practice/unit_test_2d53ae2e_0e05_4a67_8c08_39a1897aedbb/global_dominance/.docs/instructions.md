Okay, here's a challenging problem designed to test a programmer's understanding of graph algorithms, data structures, and optimization techniques.

## Project Name

`GlobalNetworkDominance`

## Question Description

Imagine a global communication network represented as a directed graph. Each node in the graph represents a server, and each directed edge represents a communication channel between servers. The weight of each edge represents the latency of the communication channel.

Your task is to identify a minimal set of "Dominating Servers" within this network. A set of servers is considered "dominating" if, for *every* server *not* in the dominating set, there exists at least *one* server in the dominating set that can reach it within a maximum latency threshold `K`.

**Formally:**

*   **Input:**
    *   A directed graph `G = (V, E)` represented as an adjacency list, where `V` is the set of servers (nodes) and `E` is the set of communication channels (directed edges). Each edge `e ∈ E` has a weight (latency) `w(e)`. The number of node is `N` and the number of edges is `M`.
    *   An integer `K` representing the maximum allowed latency.
*   **Output:**
    *   The *minimum* size of a dominating set of servers.
    *   A list containing the nodes which are in the dominating set. If multiple dominating sets of the same minimum size exist, return the lexicographically smallest one (i.e., the one that would come first if the sets were sorted as strings).

**Constraints and Requirements:**

1.  **Large Graph:** The graph can be quite large (up to 10,000 servers and 100,000 communication channels).  Your solution needs to be efficient.
2.  **Latency Threshold:** The latency threshold `K` can vary significantly, requiring you to consider different network coverage strategies.  `0 <= K <= 1000`
3.  **Edge Weights:** Edge weights (latencies) are positive integers. `1 <= w(e) <= 100`
4.  **Directed Graph:**  Communication channels are directed; server A can send data to server B, but that doesn't necessarily mean server B can send data to server A.
5.  **Connectivity:** The graph may not be fully connected.
6.  **Multiple Solutions:** There might be multiple valid dominating sets of the same *minimum* size. Your solution *must* return the lexicographically smallest one.
7.  **Time Complexity:** Solutions with time complexity significantly worse than O(V * (V + E)) or O(V^2 * logV) are unlikely to pass all test cases, where `V` is the number of vertices (servers) and `E` is the number of edges (communication channels).
8.  **Space Complexity:** Be mindful of memory usage.  Storing all possible paths between all nodes can quickly lead to memory issues.  Consider using iterative deepening or other memory-efficient techniques.
9.  **Lexicographical Order:** Ensure your code correctly identifies and returns the lexicographically smallest dominating set when multiple sets of the same minimum size exist. This will require careful handling of set generation and comparison.
10. **Handling Disconnected Components**: The graph may consist of multiple disconnected components. Your algorithm should correctly identify dominating sets for each component separately, and then appropriately combine them to find the global minimum dominating set. Incorrect handling of disconnected components may lead to suboptimal solutions.

**Example:**

Let's say the graph is represented as follows (adjacency list with weighted edges):

```
{
    0: [(1, 10), (2, 5)],  // Server 0 can reach Server 1 with latency 10, Server 2 with latency 5
    1: [(2, 3)],
    2: [(3, 2)],
    3: []
}
```

And `K = 7`.

A possible dominating set could be `{0, 1}`. Server 2 is reachable from Server 0 (latency 5) and Server 3 is reachable from Server 2, which is reachable from Server 1 (latency 3) for a total latency of 5 which are all less than `K = 7`.

Another possible dominating set is `{0, 2}`. Server 1 is reachable from Server 0 (latency 10), which is greater than K=7. Therefore, this is not a valid dominating set.

Your program should return the size of the minimum dominating set (e.g., `2`) and the lexicographically smallest dominating set (e.g., `[0, 1]`).

**Grading:**

Solutions will be evaluated based on:

*   Correctness (passing all test cases)
*   Efficiency (meeting the time and memory constraints)
*   Code clarity and readability

This problem requires a combination of graph traversal (e.g., Dijkstra's algorithm, BFS, DFS), set cover concepts, and optimization techniques to find the optimal solution efficiently. Good luck!
