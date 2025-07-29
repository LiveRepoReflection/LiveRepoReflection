## The Hypergraph Connectivity Oracle

**Question Description:**

You are given a hypergraph. A hypergraph is a generalization of a graph, where an edge (called a hyperedge) can connect any number of vertices.

More formally, a hypergraph `H = (V, E)` consists of:

*   `V`: A set of vertices, numbered from `1` to `n`.
*   `E`: A set of hyperedges. Each hyperedge `e` is a subset of `V`.

A *path* between two vertices `u` and `v` in a hypergraph is a sequence of vertices and hyperedges: `u = v_0, e_1, v_1, e_2, v_2, ..., e_k, v_k = v`, where:

*   `v_i` are vertices in `V`.
*   `e_i` are hyperedges in `E`.
*   `v_{i-1} ∈ e_i` and `v_i ∈ e_i` for all `1 <= i <= k`.

Two vertices `u` and `v` are *connected* if there exists a path between them. A *connected component* is a maximal set of vertices that are all connected to each other.

Your task is to implement a data structure called `HypergraphConnectivityOracle` that efficiently answers connectivity queries on a dynamic hypergraph.  The data structure must support the following operations:

1.  **`HypergraphConnectivityOracle(int n)`:** Constructor. Initializes the data structure with `n` vertices and no hyperedges.

2.  **`void add_hyperedge(const std::vector<int>& vertices)`:** Adds a new hyperedge to the hypergraph. The `vertices` vector contains the IDs of the vertices that the hyperedge connects. Vertex IDs are 1-indexed.

3.  **`bool are_connected(int u, int v)`:** Returns `true` if vertices `u` and `v` are connected in the current hypergraph, and `false` otherwise.  `u` and `v` are guaranteed to be valid vertex IDs (i.e., `1 <= u, v <= n`).

**Constraints:**

*   `1 <= n <= 10^5` (Number of vertices)
*   `0 <= m <= 10^5` (Number of `add_hyperedge` operations)
*   `0 <= q <= 10^5` (Number of `are_connected` queries)
*   The sum of the sizes of all hyperedges added is at most `5 * 10^5`.
*   Each hyperedge will contain unique vertices.

**Performance Requirements:**

*   The constructor `HypergraphConnectivityOracle(int n)` must run in O(n) time.
*   The `add_hyperedge` operation should be optimized to minimize the impact on future `are_connected` queries.  Aim for a solution where adding hyperedges has a reasonable amortized time complexity.
*   The `are_connected` query must be answered in O(f(n)) time, where `f(n)` should be significantly better than O(n) in practice (e.g., O(sqrt(n)), O(log n), or close to constant).  Solutions with O(n) query time will likely time out.

**Example:**

```
HypergraphConnectivityOracle oracle(5); // 5 vertices

oracle.add_hyperedge({1, 2, 3});
oracle.add_hyperedge({3, 4});

oracle.are_connected(1, 4); // Returns true (path: 1 - {1,2,3} - 3 - {3,4} - 4)
oracle.are_connected(1, 5); // Returns false

oracle.add_hyperedge({5});
oracle.are_connected(1, 5); // Returns false

oracle.add_hyperedge({2, 5});
oracle.are_connected(1, 5); // Returns true (path: 1 - {1,2,3} - 2 - {2,5} - 5)
```

**Scoring:**

Solutions will be judged based on correctness and performance. Solutions that fail to meet the performance requirements will likely time out. Partial credit may be awarded for solutions that pass some test cases. Solutions must handle all edge cases correctly to receive full credit.
