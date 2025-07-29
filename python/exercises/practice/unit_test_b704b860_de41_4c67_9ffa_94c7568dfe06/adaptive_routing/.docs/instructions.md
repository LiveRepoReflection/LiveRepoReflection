Okay, here is a challenging problem designed for a high-level programming competition.

**Problem Title: Adaptive Network Routing**

**Problem Description:**

You are tasked with designing an adaptive routing algorithm for a dynamic network. The network consists of `N` nodes (numbered from 0 to N-1) and `M` bidirectional edges. The network's connectivity and edge weights (representing latency) change over time. Your algorithm must efficiently handle these changes and route packets between nodes with minimal latency, given a set of constraints.

Specifically, you will be given a series of events. There are three types of events:

1.  **`EDGE_UPDATE u v w`**: This event indicates that the weight of the edge between nodes `u` and `v` has been updated to `w`. If the edge does not exist, create the edge. If `w` is -1, remove the edge between nodes `u` and `v`. Edge weights are non-negative integers.
2.  **`ROUTE s d`**: This event requires you to find the shortest path (minimum total latency) from source node `s` to destination node `d` at the current state of the network. If no path exists, report `-1`.
3.  **`NODE_FAILURE x`**: This event indicates that node `x` has failed and is no longer available for routing. Any path going through this node will be invalid. All edges connected to the failed node are also considered removed.

Your routing algorithm must adhere to the following constraints:

*   **Real-time Response:** The `ROUTE` queries must be answered as quickly as possible. The judge system will be sensitive to the time taken to answer each query. Pre-computation is allowed, but should be done efficiently.
*   **Dynamic Updates:** The network changes frequently, so your data structures and algorithms must be able to handle edge updates and node failures efficiently.
*   **Large Network:** The network can be large, with up to `N = 10^5` nodes and `M = 5 * 10^5` edges.
*   **Numerous Queries:** There will be a significant number of `ROUTE` queries, up to `Q = 10^5`.
*   **Integer Overflow:** Be mindful of potential integer overflows when calculating path lengths.
*   **Memory Limit:** You are limited to a reasonable amount of memory.
*   **Node Failures are Permanent:** Once a node fails, it remains failed for the rest of the execution.

**Input Format:**

The input will be provided as follows:

*   The first line contains two integers, `N` (number of nodes) and `M` (initial number of edges).
*   The next `M` lines each contain three integers, `u v w`, representing an edge between nodes `u` and `v` with weight `w`.
*   The next line contains an integer, `Q` (number of events).
*   The following `Q` lines each describe an event in one of the following formats:
    *   `EDGE_UPDATE u v w`
    *   `ROUTE s d`
    *   `NODE_FAILURE x`

**Output Format:**

For each `ROUTE` event, print the shortest path length from the source node `s` to the destination node `d` on a new line. If no path exists, print `-1`.

**Example:**

**Input:**

```
5 4
0 1 2
1 2 3
2 3 1
3 4 4
5
ROUTE 0 4
EDGE_UPDATE 1 2 5
ROUTE 0 4
NODE_FAILURE 2
ROUTE 0 4
EDGE_UPDATE 1 3 -1
ROUTE 0 4
```

**Output:**

```
10
12
-1
-1
```

**Explanation:**

1.  **Initial Network:** Shortest path from 0 to 4 is 0 -> 1 -> 2 -> 3 -> 4, with a total latency of 2 + 3 + 1 + 4 = 10.
2.  **Edge Update:** The weight of the edge between 1 and 2 is updated to 5.
3.  **Updated Network:** Shortest path from 0 to 4 is now 0 -> 1 -> 2 -> 3 -> 4, with a total latency of 2 + 5 + 1 + 4 = 12.
4.  **Node Failure:** Node 2 fails.
5.  **Network After Failure:**  The edges (1,2) and (2,3) are also removed. Therefore, there is no path from 0 to 4.
6.  **Edge Update:** Edge (1,3) is removed.
7.  **Network After Update:** There is still no path from 0 to 4.

**Constraints:**

*   `1 <= N <= 10^5`
*   `0 <= M <= 5 * 10^5`
*   `0 <= Q <= 10^5`
*   `0 <= u, v, s, d, x < N`
*   `-1 <= w <= 10^3`
*   The graph does not contain self-loops or parallel edges in the initial state.

This problem requires careful consideration of data structures (adjacency list/matrix, priority queue), graph algorithms (Dijkstra's or A\*), and optimization techniques to achieve acceptable performance within the given constraints. Good luck!
