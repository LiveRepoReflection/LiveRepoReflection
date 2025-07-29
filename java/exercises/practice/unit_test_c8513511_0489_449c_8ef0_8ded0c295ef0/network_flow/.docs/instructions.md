## Project Name

```
NetworkFlowOptimization
```

## Question Description

You are tasked with optimizing the flow of data through a complex network represented as a directed graph. The network consists of `n` nodes (numbered 0 to n-1) and `m` directed edges, each with a specific capacity. The goal is to determine the maximum amount of data that can be sent from a designated source node (`source`) to a designated sink node (`sink`).

However, this network has a unique constraint: **nodes also have capacities**. Each node `i` (excluding the source and sink) can only handle a certain amount of data passing through it.  If the total incoming flow to a node exceeds its capacity, the excess flow is lost. The source and sink nodes have unlimited capacity.

**Specifically, your task is to implement an algorithm to find the maximum flow from the source to the sink, respecting both edge and node capacities.**

**Input:**

*   `n`: The number of nodes in the network (2 <= n <= 200).
*   `m`: The number of edges in the network (0 <= m <= n*(n-1)).
*   `edges`: A 2D integer array representing the edges. Each `edges[i]` is an array of three integers: `[u, v, capacity]`, where `u` is the source node, `v` is the destination node, and `capacity` is the maximum flow allowed through that edge (1 <= capacity <= 1000).
*   `nodeCapacities`: An integer array of length `n` representing the capacity of each node. `nodeCapacities[i]` represents the maximum flow allowed to pass through node `i` (1 <= nodeCapacities[i] <= 1000). The `source` and `sink` nodes effectively have infinite capacities, but they are represented by finite maximum integer in `nodeCapacities`.
*   `source`: The index of the source node (0 <= source < n).
*   `sink`: The index of the sink node (0 <= sink < n, source != sink).

**Constraints:**

*   0 <= u, v < n for each edge.
*   No self-loops (u != v) in the edges array.
*   There might be multiple edges between two nodes, in which case they should be treated as separate edges.
*   The graph may not be strongly connected.
*   The node capacities for source and sink are large enough to be considered infinite, but algorithmically are capped at `Integer.MAX_VALUE`.

**Output:**

*   Return the maximum flow that can be sent from the source to the sink, respecting both edge and node capacities.

**Efficiency Requirements:**

Your solution should be efficient enough to handle test cases with up to 200 nodes and a dense graph. Consider the time and space complexity of your algorithm. Approaches that result in Time Limit Exceeded will not pass.

**Example:**

```
n = 4
m = 5
edges = [[0, 1, 10], [0, 2, 10], [1, 2, 2], [1, 3, 10], [2, 3, 10]]
nodeCapacities = [Integer.MAX_VALUE, 5, 8, Integer.MAX_VALUE]
source = 0
sink = 3

Output: 13
```

**Explanation:**

The maximum flow is 13.  5 units of flow go from 0 to 1, and then to 3.  8 units of flow go from 0 to 2, and then to 3. The flow through node 1 is limited to 5, and the flow through node 2 is limited to 8.

**Judging Criteria:**

Your solution will be judged based on the following criteria:

*   **Correctness:**  The solution must produce the correct maximum flow for all valid inputs.
*   **Efficiency:** The solution must be efficient enough to handle the problem constraints within the time limit.
*   **Code Quality:** The code should be well-structured, readable, and maintainable.
