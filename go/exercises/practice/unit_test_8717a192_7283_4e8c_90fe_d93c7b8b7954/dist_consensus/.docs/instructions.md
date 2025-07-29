## Project Name

```
Distributed Consensus Simulator
```

## Question Description

You are tasked with building a simulator for a simplified distributed consensus algorithm in a network of `n` nodes. The algorithm aims to achieve consensus on a single integer value. Due to network partitions and node failures, achieving perfect consensus is difficult. Your simulator must handle these scenarios gracefully.

**Algorithm:**

1.  **Initial Proposal:** Each node `i` starts with an initial proposed integer value `initial_values[i]`.
2.  **Rounds of Communication:** The algorithm proceeds in rounds. In each round, each node broadcasts its current proposed value to all other nodes.
3.  **Value Selection:** Upon receiving proposals from other nodes, each node updates its own proposed value according to the following rule:
    *   If a strict majority of received proposals (including its own current proposal) are equal to a single value, the node adopts that value as its new proposal.
    *   Otherwise (no strict majority), the node adopts the *median* of all received proposals (including its own current proposal). If the number of received proposals is even, take the lower median.
4.  **Termination:** The simulation runs for a fixed number of rounds `max_rounds`.
5. **Node Failures & Network Partitions:** Simulate node failures and network partitions.

**Specific Requirements:**

*   **Nodes:** Implement a `Node` type that encapsulates a node's state (current proposed value, initial value).
*   **Network:** Implement a `Network` type that simulates the communication between nodes. The network must support:
    *   **Node Failures:** Simulate a node failing, meaning it stops sending or receiving messages. Failed nodes should not participate in any further rounds. The number of failed nodes are represented by `num_failed_nodes`.
    *   **Network Partitions:** Simulate a network partition, where nodes are divided into disjoint groups. Nodes within the same group can communicate freely, but nodes in different groups cannot communicate at all. The network partitions are represented by a 2D array of nodes `partitions`.
*   **Simulation:** Implement a `Simulate` function that takes:
    *   `initial_values`: An array of integers representing each node's initial proposed value.
    *   `max_rounds`: The maximum number of rounds the simulation should run for.
    *   `num_failed_nodes`: the number of failed nodes.
    *    `partitions`: A 2D array representing the network partitions, where each sub-array is a group of node indicies.
    *   `seed`: An integer to seed the random number generator for node failures.
*   **Output:** The `Simulate` function should return a final array of integer values representing the proposed values of each node after `max_rounds`. Failed nodes should still have a value in the output array, representing their last known value before failing.

**Constraints:**

*   `1 <= n <= 100` (Number of nodes)
*   `1 <= max_rounds <= 100`
*   `-1000 <= initial_values[i] <= 1000`
*   The median selection must be efficient.
*   The simulation must handle edge cases gracefully (e.g., all nodes fail, trivial network partitions).
* The random number generator must be seeded to guarantee determinism.

**Goal:**

Write a robust and efficient `Simulate` function that correctly simulates the distributed consensus algorithm under the specified constraints, including node failures and network partitions. The primary challenge is to manage the complexity of distributed communication and value updates while adhering to performance requirements and handling potential failure scenarios.
