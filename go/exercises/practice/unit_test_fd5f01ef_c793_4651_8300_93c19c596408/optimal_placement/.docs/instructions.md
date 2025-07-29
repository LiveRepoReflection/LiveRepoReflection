Okay, here's a challenging Go coding problem designed for a competitive programming context, aiming for LeetCode Hard difficulty.

**Project Name:** `OptimalNetworkPlacement`

**Question Description:**

A large-scale distributed system consists of `n` nodes, numbered from `0` to `n-1`. The system is modeled as an undirected graph, where an edge between node `i` and node `j` represents a direct communication link with a latency of `latency[i][j]` (and `latency[j][i]` which are always equal). If there's no direct link between node `i` and `j`, `latency[i][j]` is `-1`.

To improve the system's performance, you need to place `k` identical server instances within the system. These server instances can be placed on any node. Any node in the system can access the nearest server. The latency for a node to access a server is the shortest path distance between that node and the server.

Your task is to determine the optimal placement of these `k` server instances to minimize the *maximum* latency experienced by any node in the system. In other words, minimize the worst-case latency. If multiple server placement configurations achieve the same minimum worst-case latency, choose the configuration with the smallest sum of latencies for all nodes in the system.

You are given:

*   `n`: The number of nodes in the system (1 <= `n` <= 100).
*   `latency`: An `n x n` matrix where `latency[i][j]` represents the communication latency between node `i` and node `j`. If `latency[i][j]` is `-1`, there is no direct link between node `i` and node `j`. Diagonal elements `latency[i][i]` are always `0`. All non-negative latencies are integers between `1` and `1000` inclusive.
*   `k`: The number of server instances to place (1 <= `k` <= min(10, n)).

Your function should return a list of `k` integers representing the optimal node indices (from `0` to `n-1`) where the server instances should be placed. The list should be sorted in ascending order.

**Constraints and Requirements:**

*   **Time Limit:** Strict time limit enforced.  Solutions requiring exponential time will not pass.
*   **Space Limit:** Memory usage should be carefully considered. Large auxiliary data structures might lead to memory limit exceeded errors.
*   **Optimization:** The objective is to minimize the *maximum* latency.  A solution that focuses solely on minimizing the *average* latency might not be optimal.
*   **Tie-breaking:** If multiple server placements result in the same minimum maximum latency, select the one that minimizes the sum of all latencies.
*   **Completeness:** The returned list must contain exactly `k` distinct node indices.
*   **Correctness:** The solution must be demonstrably correct for all valid input cases.
*   **Edge Cases:** Handle cases where `k = 1` or `k = n` efficiently.
*   **Graph Structure:** The graph may not be fully connected.

This problem requires a combination of graph algorithms (shortest path), combinatorial reasoning, and careful optimization to achieve a passing solution within the given constraints.  Good luck!
