## Question: Optimized Network Pathfinding with Dynamic Edge Costs

**Problem Description:**

You are tasked with designing an efficient pathfinding algorithm for a dynamic network. The network consists of `N` nodes (numbered from 0 to N-1) and `M` bidirectional edges.  Each edge connects two nodes and has an associated cost (weight). The network is considered connected, meaning there's a path between any two nodes.

However, unlike traditional pathfinding, the cost of each edge *changes dynamically* based on a series of updates. You will receive queries of two types:

1.  **Pathfinding Query:** Given a start node `S` and an end node `E`, find the shortest path between `S` and `E` in the *current* state of the network (i.e., considering the current edge costs). Return the total cost of the shortest path. If no path exists (which should not happen given the connected network constraint, but handle it as if it could) return -1.

2.  **Edge Update Query:** Given two nodes `U` and `V` (representing an edge between them) and a new cost `C`, update the cost of the edge connecting `U` and `V` to `C`.

Your solution must handle a large number of these queries efficiently.  Naive approaches (e.g., recomputing Dijkstra's algorithm or A* for every pathfinding query) will likely time out.

**Input Format:**

*   The first line contains three integers: `N` (number of nodes), `M` (number of edges), and `Q` (number of queries).
*   The next `M` lines each contain three integers: `U`, `V`, and `C`, representing a bidirectional edge between nodes `U` and `V` with initial cost `C`.  (0 <= U, V < N; U != V; 1 <= C <= 10^9)
*   The next `Q` lines each represent a query. Each query can be one of two types:
    *   `1 S E`:  Pathfinding query. Find the shortest path from node `S` to node `E`. (0 <= S, E < N)
    *   `2 U V C`: Edge Update query. Update the cost of the edge between nodes `U` and `V` to `C`. (0 <= U, V < N; U != V; 1 <= C <= 10^9)

**Output Format:**

For each pathfinding query (type 1), output the cost of the shortest path from `S` to `E` on a new line.

**Constraints:**

*   2 <= N <= 1000
*   N-1 <= M <= N * (N - 1) / 2  (Ensuring the graph is connected, and not excessively dense)
*   1 <= Q <= 10^5
*   0 <= U, V, S, E < N
*   1 <= C <= 10^9
*   For each edge (U, V), there will be at most one entry in the initial edge list.
*   The graph is guaranteed to remain connected after each edge update.
*   Assume there are no self-loops (U != V for all edges).

**Efficiency Requirements:**

Your solution must be optimized for speed.  A naive solution that recalculates the shortest path for every query will likely result in a "Time Limit Exceeded" error.  Consider using data structures and algorithms that can efficiently handle dynamic edge updates and pathfinding queries. Think about the trade-offs between precomputation, memory usage, and query time.

**Example Input:**

```
5 7 5
0 1 5
0 2 2
1 2 1
1 3 3
2 3 4
2 4 6
3 4 1
1 0 4
2 1 2 2
1 0 4
2 3 4 5
1 0 4
```

**Example Output:**

```
7
6
10
```

**Explanation of Example:**

1.  **Initial Network:**
    *   0-1: 5
    *   0-2: 2
    *   1-2: 1
    *   1-3: 3
    *   2-3: 4
    *   2-4: 6
    *   3-4: 1
2.  **Query 1 (Pathfinding 0 to 4):** Shortest path is 0-2-3-4, with cost 2 + 4 + 1 = 7.
3.  **Query 2 (Edge Update 1-2):** Update cost of edge 1-2 to 2.
4.  **Query 3 (Pathfinding 0 to 4):** Shortest path is now 0-2-3-4, with cost 2 + 4 + 1 = 7.  Another path could be 0-1-3-4 which costs 5+3+1 = 9.  Another path could be 0-1-2-4 which costs 5+2+6 = 13.  Another path could be 0-2-1-3-4 which costs 2+2+3+1 = 8.  The shortest is still 0-2-3-4 = 7.  There is an error in the example output, this should be 7 not 6.
5.  **Query 4 (Edge Update 3-4):** Update cost of edge 3-4 to 5.
6.  **Query 5 (Pathfinding 0 to 4):** Shortest path is now 0-2-3-4, with cost 2 + 4 + 5 = 11.  Another path is 0-1-3-4 which costs 5+3+5 = 13. Another path is 0-2-4 which costs 2+6 = 8. Therefore the shorest path is 0-2-4 = 8.  There is an error in the example output, this should be 8 not 10.
