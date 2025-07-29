Okay, here's a challenging Python coding problem.

## Project Name

```
Optimal_Network_Partitioning
```

## Question Description

You are tasked with designing a resilient communication network for a distributed system. The system consists of `n` nodes, each representing a server or a processing unit. These nodes are interconnected through a network with a given topology. Due to budget constraints, you need to partition this network into `k` distinct clusters such that:

1.  **Connectivity within Clusters:** Each cluster must be internally connected. This means that from any node within a cluster, you can reach any other node within the same cluster using existing network links *without* traversing nodes outside the cluster.

2.  **Minimizing Inter-Cluster Dependencies:** Some nodes have dependencies on others for correct operation. These dependencies are represented as directed edges between nodes. Your goal is to minimize the number of dependency edges that cross cluster boundaries. In other words, you want to minimize the number of directed edges where the source node and the target node belong to different clusters.

3.  **Cluster Size Constraints:** Each cluster must contain at least `min_size` nodes and at most `max_size` nodes. This ensures a balanced distribution of workload across the clusters.

4.  **Fault Tolerance:**  To ensure fault tolerance, the *minimum* number of nodes in each cluster should be `min_size`.

**Input:**

*   `n`: The number of nodes in the network (numbered from 0 to n-1).
*   `k`: The desired number of clusters.
*   `edges`: A list of tuples representing undirected edges in the network. Each tuple `(u, v)` indicates an undirected edge between nodes `u` and `v`.
*   `dependencies`: A list of tuples representing directed dependency edges. Each tuple `(u, v)` indicates a dependency where node `u` depends on node `v`.
*   `min_size`: The minimum allowed size of a cluster.
*   `max_size`: The maximum allowed size of a cluster.

**Output:**

A list of lists, where each inner list represents a cluster containing the node indices that belong to it. If no valid partitioning exists, return `None`. If multiple optimal solutions exist, return any one of them.

**Constraints:**

*   `1 <= n <= 100`
*   `1 <= k <= n`
*   `0 <= edges.length <= n * (n - 1) / 2`
*   `0 <= dependencies.length <= n * (n - 1)`
*   `1 <= min_size <= max_size <= n`
*   It is guaranteed that `min_size * k <= n <= max_size * k`
*   Node indices are 0-based.

**Optimization Requirement:**

The solution must be efficient enough to handle inputs of the maximum size specified in the constraints within a reasonable time limit (e.g., a few seconds).  Consider the algorithmic complexity of your approach. Exhaustive search will likely time out.

**Example:**

```python
n = 6
k = 2
edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]
dependencies = [(0, 3), (2, 5), (4, 1)]
min_size = 2
max_size = 4

# Possible valid output:
# [[0, 1, 2], [3, 4, 5]]
# Number of cross cluster dependencies is 2: (0,3), (2,5)
```
```python
n = 6
k = 3
edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]
dependencies = [(0, 3), (2, 5), (4, 1)]
min_size = 1
max_size = 3

# Possible valid output:
# [[0, 1], [2,3], [4,5]]
# Number of cross cluster dependencies is 3: (0,3), (2,5), (4,1)
```

**Judging Criteria:**

*   Correctness: The solution must produce a valid partitioning that satisfies all constraints.
*   Optimization: The solution must minimize the number of inter-cluster dependency edges.
*   Efficiency: The solution must be able to handle reasonably large inputs within the time limit.
*   Completeness: Return `None` if no solution exists.
