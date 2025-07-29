## Project Name

```
NetworkRouteOptimizer
```

## Question Description

You are tasked with designing an efficient route optimization algorithm for a large-scale communication network. The network consists of `N` nodes, each identified by a unique integer ID from 0 to `N-1`.  These nodes are interconnected by `M` bidirectional communication links. Each link connects two nodes and has an associated cost representing the latency or bandwidth usage of that connection.

Due to network congestion and varying traffic patterns, the cost of each link changes dynamically over time. You are given a log of these changes as a series of `Q` update events.  Each update event specifies a link (defined by the two node IDs it connects) and a new cost for that link at a particular timestamp.

Your goal is to implement a system that can efficiently answer queries about the minimum cost path between any two given nodes at any given timestamp.

Specifically, you must implement the following:

1.  **Initialization:**  Your system should be initialized with the initial network topology (nodes and links with their initial costs).

2.  **Update Processing:**  Process the `Q` update events in the order they are given.  Each event will consist of:
    *   `timestamp`: A positive integer representing the time of the update.
    *   `node1`: The ID of the first node of the link being updated.
    *   `node2`: The ID of the second node of the link being updated.
    *   `new_cost`:  A non-negative integer representing the new cost of the link.

3.  **Query Answering:**  Answer queries of the form: "What is the minimum cost to travel from node `start_node` to node `end_node` at timestamp `query_timestamp`?".  If no path exists between the `start_node` and `end_node` at the `query_timestamp`, return -1.

**Constraints:**

*   `1 <= N <= 1000` (Number of nodes)
*   `0 <= M <= N * (N - 1) / 2` (Number of links)
*   `0 <= Q <= 100000` (Number of update events)
*   `0 <= node1, node2 < N`
*   `0 <= new_cost <= 1000`
*   `1 <= timestamp, query_timestamp <= 1000000`
*   The graph is initially connected.
*   All timestamps are unique.

**Efficiency Requirements:**

*   Your solution should be able to handle a large number of updates and queries efficiently.  Naive recomputation of shortest paths for each query will likely time out. Consider techniques like dynamic shortest path algorithms or caching strategies.
*   Minimize memory usage where possible.  Storing the complete graph state for every timestamp may be infeasible.

**Input Format:**

The input will be provided in the following format:

1.  The first line contains two integers, `N` (number of nodes) and `M` (number of links).

2.  The next `M` lines each contain three integers: `node1`, `node2`, and `initial_cost`, representing a link between `node1` and `node2` with an initial cost of `initial_cost`.

3.  The next line contains a single integer, `Q` (number of update events).

4.  The next `Q` lines each contain four integers: `timestamp`, `node1`, `node2`, and `new_cost`, representing an update event.

5.  The next line contains a single integer, `K` (number of queries).

6.  The next `K` lines each contain three integers: `query_timestamp`, `start_node`, and `end_node`, representing a query.

**Output Format:**

For each query, output a single line containing the minimum cost to travel from `start_node` to `end_node` at the specified `query_timestamp`. If no path exists, output -1.

**Example:**

```
Input:
4 5
0 1 10
0 2 5
1 2 2
1 3 1
2 3 4
3
1 0 1 15
2 1 3 3
3 0 2 8
2
2 0 3
3 0 3

Output:
9
13
```

**Explanation of the Example:**

*   **Initial Graph:**  Nodes 0, 1, 2, 3 with links as described.
*   **Update 1 (timestamp 1):**  Link between 0 and 1 has cost changed to 15.
*   **Update 2 (timestamp 2):**  Link between 1 and 3 has cost changed to 3.
*   **Update 3 (timestamp 3):**  Link between 0 and 2 has cost changed to 8.
*   **Query 1 (timestamp 2):**  Shortest path from 0 to 3 at timestamp 2 is 0 -> 1 -> 3 with cost 10 (initial cost) + 3 (updated cost) = 13. Path 0 -> 2 -> 3 with cost 5 (initial cost) + 4 (initial cost) = 9. Hence, the answer is 9.
*   **Query 2 (timestamp 3):**  Shortest path from 0 to 3 at timestamp 3 is 0 -> 1 -> 3 with cost 15 (updated cost) + 3 (updated cost) = 18. Path 0 -> 2 -> 3 with cost 8 (updated cost) + 4 (initial cost) = 12. Hence, 12 is shortest path.

This question is designed to test your understanding of graph algorithms, dynamic programming, data structures, and efficient algorithm design.  Good luck!
