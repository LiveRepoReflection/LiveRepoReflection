## Question: Distributed Consensus with Byzantine Fault Tolerance

**Problem Description:**

You are tasked with designing a simplified, yet robust, distributed consensus algorithm for a network of nodes operating in a potentially hostile environment. The goal is to achieve agreement on a single, sequentially increasing, integer value (representing, for example, a transaction ID, a log sequence number, or a state version) despite the possible presence of Byzantine faults.

Byzantine faults imply that some nodes in the network might exhibit arbitrary behavior, including sending conflicting or malicious information to different nodes. You need to ensure that the correct (non-faulty) nodes can still reach consensus on the next integer value, even if a fraction of the nodes are compromised.

**System Setup:**

*   You have a network of `N` nodes, identified by unique integer IDs from `0` to `N-1`.
*   Assume that at most `f` nodes can be faulty, where `3f < N` (ensuring the network can tolerate the faults using a BFT algorithm).
*   Nodes communicate with each other via reliable, point-to-point communication channels (messages are guaranteed to be delivered without corruption or loss, although delivery order is not guaranteed).
*   Each node maintains a local clock, but clock synchronization is not guaranteed. You can assume that messages have an origin timestamp.
*   Each node starts with the initial integer value `0`. The goal is for all correct nodes to sequentially agree on the next integer value (`1`, `2`, `3`, and so on).

**Your Task:**

Implement a simplified Byzantine Fault Tolerant (BFT) consensus algorithm. The algorithm should operate in "rounds". Each round aims to achieve consensus on a single integer value.

Within each round, the following steps occur:

1.  **Proposal:** One node (the "leader" for that round) proposes the next integer value.  The leader is determined by a deterministic function of the round number and the total number of nodes (e.g., `leader_id = round_number % N`).
2.  **Broadcast:** The leader broadcasts its proposed value to all other nodes.
3.  **Voting:** Each node, upon receiving a proposal, validates that it is a valid integer and that it is strictly greater than the previously agreed value. If the proposal is valid, the node broadcasts a "vote" for that value to all other nodes. Otherwise, the node broadcasts a "vote" to reject the proposal.
4.  **Commit:** A node commits to the value proposed in the round if it receives valid votes from a quorum of nodes. The quorum size should be sufficient to guarantee that even with `f` faulty nodes, there are enough correct nodes voting for the value.
5. **Acknowledgement**: Once a node commits, it will broadcast an acknowledgement message of the commit.

**Implementation Requirements:**

*   Implement the core logic for a single node in the BFT consensus algorithm.
*   Your solution should handle potential Byzantine faults, such as:
    *   The leader proposing different values to different nodes.
    *   Faulty nodes sending conflicting votes.
    *   Faulty nodes not sending messages at all.
*   Your implementation should aim to minimize message complexity and latency while maintaining safety and liveness.
*   Your implementation should ensure that the next agreed-upon integer value is always greater than the previous one, even in the presence of faults.

**Constraints:**

*   `N` (number of nodes): `4 <= N <= 100`
*   `f` (maximum number of faulty nodes): `f < N/3`
*   The integer values to be agreed upon will always be positive.
*   Message size should be kept to a minimum.

**Output:**

The function should return the final agreed-upon integer value by a node after `K` number of consensus rounds.

**Bonus Challenges:**

*   Implement a mechanism to detect and penalize (e.g., exclude) nodes that consistently exhibit faulty behavior.
*   Optimize your solution to handle a larger number of nodes and higher fault tolerance.
*   Consider the impact of network latency and jitter on the performance of your algorithm.
