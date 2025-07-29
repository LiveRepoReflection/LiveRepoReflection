## Problem: Optimal Network Partitioning for High Availability

**Description:**

A large distributed system is represented as an undirected graph where nodes represent servers and edges represent network connections. Each server has a `cost` associated with it, representing the financial impact of that server becoming unavailable (e.g., due to a crash or network partition). Each edge also has a `weight` associated with it, representing the capacity of the network connection.

You are tasked with partitioning this network into two disjoint sets of servers (Partition A and Partition B) to minimize the *maximum potential availability loss*. The potential availability loss is calculated for each partition as the sum of the costs of the servers within that partition.

However, simply minimizing the maximum cost sum isn't enough.  The system must also be robust against network congestion. To ensure this, you must also minimize the *capacity cut* between the two partitions. The capacity cut is the sum of the weights of the edges that connect a server in Partition A to a server in Partition B.

The final objective function is to minimize the following:

`max(cost_sum(Partition A), cost_sum(Partition B)) + lambda * capacity_cut(A, B)`

where:

*   `cost_sum(Partition X)` is the sum of the costs of all servers in partition X.
*   `capacity_cut(A, B)` is the sum of the weights of all edges crossing between partition A and partition B.
*   `lambda` is a non-negative weighting factor that balances the trade-off between minimizing the maximum potential loss and minimizing network congestion.

**Input:**

*   `n`: The number of servers (nodes in the graph).
*   `edges`: A vector of tuples `(u, v, weight)`, representing an undirected edge between servers `u` and `v` with a capacity `weight`. Server indices are 0-based.
*   `costs`: A vector of integers, where `costs[i]` is the cost associated with server `i`.
*   `lambda`: A double representing the weighting factor.

**Constraints:**

*   `2 <= n <= 1000`
*   `0 <= edges.size() <= n * (n - 1) / 2`
*   `0 <= u, v < n`
*   `0 <= weight <= 100`
*   `0 <= costs[i] <= 1000`
*   `0.0 <= lambda <= 100.0`

**Output:**

Return a vector of integers representing the servers belonging to Partition A. The remaining servers implicitly belong to Partition B. The order of servers in the returned vector doesn't matter.

**Example:**

```
n = 4
edges = [(0, 1, 10), (0, 2, 15), (1, 3, 20), (2, 3, 30)]
costs = [100, 200, 300, 400]
lambda = 0.5

Possible solution: [0, 1] (Partition A)

Partition A: [0, 1] (cost_sum = 100 + 200 = 300)
Partition B: [2, 3] (cost_sum = 300 + 400 = 700)
Capacity Cut: Edge(0,2):15 + Edge(1,3):20 = 35

Objective Function: max(300, 700) + 0.5 * 35 = 700 + 17.5 = 717.5
```

**Requirements:**

*   The solution must provide a valid partition of the network (every server belongs to exactly one partition).
*   The solution must be efficient enough to handle the given constraints.  Brute-force solutions (checking all possible partitions) will likely time out.
*   Consider algorithmic efficiency and data structure choices carefully.
*   The problem encourages exploration of graph algorithms and optimization techniques.  There may be multiple valid approaches.  The goal is to find a solution that minimizes the objective function as much as possible.
*   Small differences in the objective function might occur due to floating point math.

**Grading:**

The solution will be evaluated based on its correctness and its ability to minimize the objective function on a set of hidden test cases. Solutions that are consistently closer to the optimal objective function will receive higher scores. Performance will be measured by the final score on all test cases.  Submissions that exceed the time limit for a test case will receive a score of 0 for that test case.
