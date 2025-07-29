## Question: Optimal Network Routing

**Problem Description:**

You are tasked with designing an efficient routing algorithm for a large-scale communication network. The network consists of `N` nodes, numbered from 1 to `N`. Each node represents a router. The connections between routers are represented by a set of bidirectional links. Each link connects two nodes and has an associated cost (latency, bandwidth usage, etc.).

You are given a series of `Q` routing requests. Each request specifies a source node `S` and a destination node `D`. For each request, your algorithm must determine the optimal path from `S` to `D`, minimizing the total cost.

However, the network is dynamic. Before each routing request, a certain number of link costs may change. These changes are provided as updates. You must process these updates and re-evaluate the optimal paths accordingly.

**Input Format:**

*   The first line contains two integers, `N` (number of nodes) and `M` (number of links), separated by a space.
*   The next `M` lines each contain three integers, `U`, `V`, and `C`, representing a bidirectional link between nodes `U` and `V` with cost `C`.
*   The next line contains an integer, `Q` (number of routing requests).
*   For each of the `Q` routing requests:
    *   The first line contains an integer `K` (number of link cost updates before this request).
    *   The next `K` lines each contain three integers, `U`, `V`, and `NEW_C`, indicating that the cost of the link between nodes `U` and `V` should be updated to `NEW_C`. Note that the link `U-V` already exists. Also, `U` and `V` are given in their original order, you should update the link between `U` and `V` only.
    *   The next line contains two integers, `S` (source node) and `D` (destination node), representing the routing request.

**Output Format:**

For each routing request, output a single integer representing the minimum cost of the path from `S` to `D`. If no path exists, output `-1`.

**Constraints:**

*   `1 <= N <= 10^5`
*   `1 <= M <= 3 * 10^5`
*   `1 <= Q <= 100`
*   `1 <= U, V, S, D <= N`
*   `1 <= C, NEW_C <= 10^5`
*   `0 <= K <= 100`
*   The graph is not guaranteed to be connected initially.

**Efficiency Requirements:**

Your solution must be efficient enough to handle a large number of nodes and links within a reasonable time limit (e.g., a few seconds).  Consider the algorithmic complexity of your solution, as brute-force approaches will likely time out. You must find the optimal path, not just any path.

**Edge Cases:**

*   `S` and `D` might be the same node.
*   No path exists between `S` and `D`.
*   The graph might be disconnected.
*   Duplicate links in the initial input are possible. If duplicate links exist, consider only the last given cost for that link.
*   The updates must be applied correctly before calculating the shortest path for each query.

This question challenges the solver to combine graph algorithms (shortest path), dynamic updates, and efficiency considerations. A good solution will likely require careful selection of data structures and algorithms to meet the performance requirements.
