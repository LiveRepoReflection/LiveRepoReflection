## Project Name

`Distributed Consensus Simulator`

## Question Description

You are tasked with building a simplified simulator for a distributed consensus algorithm. The focus is on implementing a protocol that allows a cluster of nodes to agree on a single value, even in the presence of failures (specifically, node crashes).

**Scenario:**

Imagine a system where multiple servers need to agree on a log of events. Each server starts with its own initial proposed log.  The goal is for all non-faulty servers to eventually converge on the *same* log, even if some servers crash during the process.  We'll be simulating a simplified version of this.

**Specifics:**

You will simulate a cluster of `N` nodes (numbered 0 to N-1). Each node starts with an initial *proposed value* (an integer). The system operates in *rounds*. In each round:

1.  **Propose:** Each node proposes a value to the cluster.
2.  **Collect:** Each node collects the proposals from all other nodes in the cluster. If a node does not receive a proposal from another node in a given round, it considers that node to have crashed.
3.  **Decide:** Based on the collected proposals, each node decides on a new value. The decision rule is as follows: If a node receives a majority of the same value, it adopts that value for the next round. Otherwise, it chooses the *smallest* value proposed to it (including its own previous value). A crashed node proposes no value.
4.  **Update:** Each node updates its own current value to the decided value for the next round.

The simulator should run for a specified number of rounds, or until all non-faulty nodes have agreed on the same value.

**Input:**

*   `N`: The number of nodes in the cluster (1 <= N <= 100).
*   `initial_values`: A list of N integers, representing the initial proposed value for each node.
*   `crash_pattern`: A list of lists. Each inner list represents a round, and contains the node IDs that crash *before* proposing their value in that round. For example `[[0], [1,2], []]` means node 0 crashes in the first round, nodes 1 and 2 crash in the second round, and no nodes crash in the third round.
*   `max_rounds`: The maximum number of rounds the simulation should run for (1 <= max_rounds <= 100).

**Output:**

*   A list of N integers, representing the final value of each node after the simulation completes, or after `max_rounds` if consensus is not reached.

**Constraints and Edge Cases:**

*   Node IDs are 0-indexed.
*   A node can crash in multiple rounds, or not at all.
*   If a node crashes, it remains crashed for the rest of the simulation.
*   The initial values can be any integer.
*   The solution must handle the case where no consensus is reached within `max_rounds`.
*   The solution must handle the case of network partition that might prevent consensus.

**Optimization Considerations:**

*   Aim for a solution that is efficient in terms of time complexity. A naive implementation could lead to unnecessary iterations.
*   Consider how to represent the state of the system (node values, crashed nodes) to optimize data access.

**Example:**

```
N = 3
initial_values = [1, 2, 1]
crash_pattern = [[], [1], []]
max_rounds = 5

# Expected output (may vary depending on the decision rule tie-breaker):
# [1, 1, 1]
```

**Explanation of Example:**

*   **Round 1:**
    *   Node 0 proposes 1, Node 1 proposes 2, Node 2 proposes 1.
    *   Node 0 decides on 1 (majority). Node 1 decides on 1 (1,1 < 2). Node 2 decides on 1 (majority).
    *   Values: \[1, 1, 1]
*   **Round 2:**
    *   Node 0 proposes 1, Node 1 crashes, Node 2 proposes 1.
    *   Node 0 decides on 1 (majority). Node 1 remains crashed. Node 2 decides on 1 (majority).
    *   Values: \[1, 1, 1]
*   Consensus is reached.

**Judging Criteria:**

*   Correctness: The solution must produce the correct final values for all nodes, even in the presence of crashes and edge cases.
*   Efficiency: The solution should be reasonably efficient and avoid unnecessary computations.
*   Code Clarity: The code should be well-structured and easy to understand.
*   Handling of Constraints: The solution must adhere to all input constraints.

This problem requires careful consideration of data structures, control flow, and handling of potentially complex failure scenarios. Good luck!
