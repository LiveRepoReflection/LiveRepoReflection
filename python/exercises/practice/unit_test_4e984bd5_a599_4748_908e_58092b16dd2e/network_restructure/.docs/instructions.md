## Question: Optimal Network Restructuring

**Problem Description:**

You are tasked with optimizing the structure of a communication network represented as a weighted, undirected graph. The network consists of `N` nodes (numbered from 1 to N) and `M` edges. Each edge connects two nodes and has an associated cost representing the expense of maintaining that connection.

Due to budget constraints, the network administrator wants to restructure the network. The goal is to find a set of edges such that:

1.  **Connectivity:** All nodes remain connected (there exists a path between any two nodes).
2.  **Minimization of Maximum Degree:** The maximum degree of any node in the restructured network is minimized. The degree of a node is the number of edges connected to it.
3.  **Cost Constraint:** The total cost of the edges in the restructured network must be less than or equal to a given budget `B`.
4. **Stability:** The new network must include at least K edges from the original network to maintain stability of service.

**Input:**

*   `N`: The number of nodes in the network (1 <= N <= 200).
*   `M`: The number of edges in the network (N-1 <= M <= N*(N-1)/2).
*   `edges`: A list of tuples `(u, v, cost)`, where `u` and `v` are the nodes connected by the edge (1 <= u, v <= N, u != v), and `cost` is the cost of maintaining the edge (1 <= cost <= 10<sup>5</sup>).  There are no duplicate edges.
*   `B`: The maximum budget allowed for the restructured network (1 <= B <= 10<sup>8</sup>).
*   `K`: The minimum number of edges required from the original network (0 <= K <= M)

**Output:**

*   The minimum possible maximum degree of any node in a restructured network that satisfies all the given constraints. If no such network exists, return `-1`.

**Constraints:**

*   The graph represented by the input edges is guaranteed to be connected.
*   You must use Python 3.
*   Your solution should be as efficient as possible. Solutions that run in exponential time will likely time out.
*   Consider using appropriate data structures and algorithms for graph manipulation, connectivity checks, and optimization.

**Example:**

```
N = 4
M = 5
edges = [(1, 2, 10), (1, 3, 15), (1, 4, 20), (2, 3, 5), (3, 4, 8)]
B = 40
K = 2
```

One possible restructured network could consist of the edges `(1, 2, 10)`, `(2, 3, 5)`, and `(3, 4, 8)`. The total cost is 23, which is less than the budget 40. The maximum degree of any node in this network is 2. Two edges are also from the original network.

A better network could be `(1,2,10), (1,3,15), (3,4,8)`. This network has a maximum degree of 2 with total cost 33, and two original edges.

Therefore, the output is `2`.

**Note:** Focus on finding the minimum *maximum* degree. The distribution of degrees among nodes doesn't matter as long as the maximum degree is minimized.

**Additional Challenge (Optional, but highly encouraged):**

Consider how your solution would scale if `N` and `M` were significantly larger (e.g., N <= 1000, M <= 100000). What optimizations could you make to improve performance further?  This consideration is important for demonstrating a strong understanding of algorithmic efficiency.
