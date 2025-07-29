## Project Name

`Network Partitioning for Distributed Consensus`

## Question Description

You are building a distributed key-value store that relies on a consensus algorithm (like Raft or Paxos) to ensure data consistency across multiple nodes. Your system is susceptible to network partitions, where the network is split into two or more isolated groups of nodes.

Your task is to implement a function that analyzes the network topology and determines the *minimum* number of nodes that need to be moved to a different partition to ensure no partition has more than `K` nodes and can still function correctly.

**Input:**

*   `nodes`: A `Vec<Node>` representing the nodes in the network. Each `Node` struct has a unique `id` (`usize`) and `partition_id` (`usize`).
*   `adj_matrix`: A `Vec<Vec<bool>>` representing the adjacency matrix of the network. `adj_matrix[i][j] == true` if there is a direct network connection between `nodes[i]` and `nodes[j]`, and `false` otherwise. Note that `adj_matrix[i][i] == true` for all `i`.
*   `K`: An integer representing the maximum number of nodes allowed in a single partition.

**Output:**

*   An `usize` representing the minimum number of nodes that need to be moved to a different partition to ensure no partition has more than `K` nodes.

**Data Structures:**

```rust
struct Node {
    id: usize,
    partition_id: usize,
}
```

**Constraints and Edge Cases:**

*   The number of nodes can be large (up to 1000).  Naive solutions with O(n^3) complexity may not pass.
*   The network can be disconnected even before any nodes are moved.
*   The adjacency matrix is symmetric.
*   Nodes within the same partition may not necessarily be fully connected. Connectivity is only guaranteed by the `partition_id` assignment.
*   Moving a node means changing its `partition_id`. Moving a node also removes all of its connections from the original partition.
*   It is possible that no solution exists (i.e., even after moving all nodes, a partition still has > K nodes because all nodes started out in the same partition). Your solution should return the minimum possible moves even if it cannot bring all partitions to be less than K.

**Optimization Requirements:**

*   The solution should be as efficient as possible in terms of time and space complexity. Consider using appropriate data structures and algorithms.
*   Assume the initial `partition_id` assignments are arbitrary and may not be optimal.
*   The primary goal is to minimize the number of nodes moved, regardless of the resulting number of partitions.

**Example:**

```rust
let nodes = vec![
    Node { id: 0, partition_id: 0 },
    Node { id: 1, partition_id: 0 },
    Node { id: 2, partition_id: 0 },
    Node { id: 3, partition_id: 1 },
    Node { id: 4, partition_id: 1 },
];
let adj_matrix = vec![
    vec![true, true, false, false, false],
    vec![true, true, true, false, false],
    vec![false, true, true, false, false],
    vec![false, false, false, true, true],
    vec![false, false, false, true, true],
];
let k = 2;

// Here, partition 0 has 3 nodes and partition 1 has 2 nodes. To satisfy K = 2,
// we need to move at least one node from partition 0 to partition 1.
// The function should return 1.

```
This problem requires a combination of graph traversal, optimization techniques, and careful consideration of edge cases to achieve an efficient and correct solution. Good luck!
