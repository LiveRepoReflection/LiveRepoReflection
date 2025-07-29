## The Critical Infrastructure Resilience Game

**Problem Description:**

You are tasked with designing a system to evaluate the resilience of a critical infrastructure network against cascading failures. This network represents essential services like power grids, water supplies, or communication networks, where the failure of one component can trigger failures in others.

The infrastructure is represented as a weighted, directed graph. Nodes represent infrastructure components (e.g., power stations, water treatment plants, servers), and directed edges represent dependencies between them. The weight of an edge represents the dependency strength.  A higher weight indicates a stronger dependency, meaning the failure of the source node is more likely to cause the target node to fail.

Initially, the network is fully operational. However, a disruptive event can cause the failure of one or more initial nodes. Your system must simulate the propagation of failures through the network and determine the final set of failed nodes.

**Specifics:**

1.  **Input:**
    *   `n`: The number of nodes in the graph (numbered 0 to n-1).
    *   `edges`: A list of tuples, where each tuple `(u, v, w)` represents a directed edge from node `u` to node `v` with weight `w`.  Weights are positive integers.
    *   `initial_failures`: A set of node IDs that fail initially.
    *   `threshold`: A floating-point number between 0 and 1, representing the failure threshold.

2.  **Failure Propagation:**
    *   A node `v` fails if the *weighted sum* of its *operational* incoming neighbors exceeds a certain threshold.
    *   The *weighted sum* of operational incoming neighbors is calculated as the sum of the weights of all incoming edges from nodes that are still operational.
    *   A node `v` fails if this *weighted sum* is greater than or equal to `threshold` multiplied by the *total weight* of all incoming edges (from both operational and failed neighbors).
    *   Formally, if `W_in(v)` is the set of incoming edge weights to node `v`, `W_op(v)` is the set of weights from operational incoming edges to node `v`, and `S_op(v)` is the sum of weights in `W_op(v)`, then `v` fails if `S_op(v) >= threshold * sum(W_in(v))`.
    *   Failures propagate iteratively. In each iteration, you check for new failures based on the current state of the network. The process continues until no new nodes fail in an iteration.

3.  **Output:**
    *   A sorted list of node IDs that have failed after the failure propagation stabilizes.

**Constraints:**

*   `1 <= n <= 1000`
*   `0 <= number of edges <= 5000`
*   `0 <= u, v < n` for each edge `(u, v, w)`
*   `1 <= w <= 100` for each edge `(u, v, w)`
*   `0 <= threshold <= 1`
*   The graph can contain cycles.
*   Multiple edges between the same pair of nodes are allowed. The weights should be considered separately.
*   Optimization: The solution should be efficient enough to handle large graphs within a reasonable time limit (e.g., a few seconds). The algorithm's complexity is an important consideration.

**Example:**

```
n = 4
edges = [(0, 1, 50), (0, 2, 30), (1, 2, 20), (2, 3, 60)]
initial_failures = {0}
threshold = 0.6

Output: [0, 1, 2, 3]
```

**Explanation:**

1.  Initially, node 0 fails.
2.  **Iteration 1:**
    *   Node 1 has only one incoming edge from node 0 (weight 50). Since node 0 has failed, the weighted sum of operational neighbors is 0. The total incoming weight is 50. 0 < 0.6 * 50 = 30. Node 1 remains operational.
    *   Node 2 has incoming edges from nodes 0 (weight 30) and 1 (weight 20). Node 0 has failed. The weighted sum of operational neighbors is 20. The total incoming weight is 30 + 20 = 50. 20 < 0.6 * 50 = 30. Node 2 remains operational.
    *   Node 3 has only one incoming edge from node 2 (weight 60). Node 2 is operational. The weighted sum of operational neighbors is 60. The total incoming weight is 60. 60 >= 0.6 * 60 = 36. Node 3 fails.
3.  **Iteration 2:**
    *   Node 1 has only one incoming edge from node 0 (weight 50). Since node 0 has failed, the weighted sum of operational neighbors is 0. The total incoming weight is 50. 0 < 0.6 * 50 = 30. Node 1 remains operational.
    *   Node 2 has incoming edges from nodes 0 (weight 30) and 1 (weight 20). Node 0 has failed. The weighted sum of operational neighbors is 20. The total incoming weight is 30 + 20 = 50. 20 < 0.6 * 50 = 30. Node 2 remains operational.
4. **Iteration 3:**
     * Node 1 has only one incoming edge from node 0 (weight 50). Since node 0 has failed, the weighted sum of operational neighbors is 0. The total incoming weight is 50. 0 < 0.6 * 50 = 30. Node 1 remains operational.
     * Node 2 has incoming edges from nodes 0 (weight 30) and 1 (weight 20). Node 0 has failed. The weighted sum of operational neighbors is 20. The total incoming weight is 30 + 20 = 50. 20 < 0.6 * 50 = 30. Node 2 remains operational.

5. **Iteration 4:**
    *Node 1 fails since node 0 has failed. 0 < 0.6*50 is false.
6. **Iteration 5:**
    * Node 2 fails since node 1 has failed. 0 < 0.6*50 is false.

Thus, final failed nodes are [0,1,2,3].

**Challenge:**

Design an efficient algorithm to simulate the failure propagation and return the correct output under the given constraints. Consider how to handle cycles and optimize for performance.
