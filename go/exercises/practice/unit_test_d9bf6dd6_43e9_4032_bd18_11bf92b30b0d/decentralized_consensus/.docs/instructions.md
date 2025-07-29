## Question: Decentralized Consensus Simulation

### Question Description

You are tasked with simulating a simplified decentralized consensus protocol within a network of nodes. The goal is to determine if the network can reach a consensus on a single value, given specific network conditions and node behaviors. This is a complex system design problem with a focus on algorithmic efficiency and handling multiple failure scenarios.

**Network Model:**

*   The network consists of `N` nodes, numbered from `0` to `N-1`.
*   Nodes communicate by sending messages to each other. Message delivery is not guaranteed and can be delayed or lost (Byzantine fault tolerance is not required, but handling message loss is important).
*   Each node has a unique initial value represented as a 64-bit integer.
*   Nodes operate in rounds. In each round, a node can:
    *   Receive messages from other nodes.
    *   Update its internal state based on received messages.
    *   Send messages to a subset of other nodes.

**Consensus Protocol:**

The consensus protocol is a simplified version of a voting-based system:

1.  **Initialization:** Each node starts with its unique initial value.
2.  **Communication:** In each round, each node sends its *current* value to `K` randomly chosen nodes (without replacement).
3.  **Value Update:** After receiving messages in a round, each node updates its current value. The new value is calculated as the **median** of all values the node *currently* holds (including its own). If the number of values is even, the median is the smaller of the two middle values after sorting.
4.  **Termination:** The simulation runs for a maximum of `R` rounds. Consensus is reached if *all* nodes have the same value at the end of any round.

**Task:**

Write a Go program that simulates this decentralized consensus protocol and determines if the network reaches consensus within `R` rounds.

**Input:**

*   `N`: The number of nodes in the network (1 <= N <= 1000).
*   `K`: The number of nodes each node communicates with in each round (1 <= K < N).
*   `R`: The maximum number of rounds to run the simulation (1 <= R <= 100).
*   `initialValues`: A slice of `N` 64-bit integers representing the initial value of each node.
*   `messageLossProbability`: A floating-point number between 0 and 1 (inclusive) representing the probability that a message sent between any two nodes is lost.

**Output:**

*   Return `true` if the network reaches consensus within `R` rounds.
*   Return `false` if the network does not reach consensus within `R` rounds.

**Constraints:**

*   The solution must be efficient. Naive implementations that perform excessive copying or repeated sorting will likely time out.
*   The random number generation should be deterministic for testing purposes. Use a fixed seed for the random number generator.
*   The solution should gracefully handle message loss.
*   The solution should be correct, even with varying values of `N`, `K`, `R`, `initialValues`, and `messageLossProbability`.

**Optimization Requirements:**

*   Minimize memory allocations and copying within each round.
*   Optimize the median calculation to avoid unnecessary sorting. Consider using an efficient selection algorithm.

**Real-world Practical Scenarios:**

This problem models a simplified version of distributed agreement protocols, which are fundamental in blockchain technology, distributed databases, and fault-tolerant systems. The challenge lies in achieving consensus despite unreliable communication channels and potentially inconsistent initial states.

This description should be enough to challenge even experienced Go programmers! Good luck!
