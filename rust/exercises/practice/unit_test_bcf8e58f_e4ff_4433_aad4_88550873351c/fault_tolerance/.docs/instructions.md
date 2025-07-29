## Project Name

`Distributed Consensus with Fault Tolerance`

## Question Description

You are tasked with implementing a simplified distributed consensus algorithm that can tolerate a certain number of node failures. Imagine you are building a highly available database or a distributed key-value store. A crucial component is ensuring that all nodes agree on the order of operations, even if some nodes crash or become temporarily unavailable.

Your system consists of `N` nodes, where `N` is a configurable parameter. You need to implement a consensus protocol that can tolerate up to `f` faulty nodes, where `f < N/2`. This constraint is important to ensure the safety and liveness of the consensus.

**Specifically, you need to implement a simplified version of the Raft consensus algorithm, focusing on the leader election and log replication aspects.**

**Core Requirements:**

1.  **Leader Election:** Implement a mechanism for electing a single leader among the `N` nodes.  Nodes should be able to detect leader failures and trigger a new election. You can assume a round-based election process. You should implement a heartbeat mechanism where the leader periodically sends messages to the followers to maintain its leadership. If a follower doesn't receive a heartbeat within a timeout period, it should start a new election. Your election should have a randomized timeout to avoid split votes.

2.  **Log Replication:** Once a leader is elected, it is responsible for replicating the operations (log entries) to the followers.  When a client submits an operation, the leader appends it to its log.  The leader then attempts to replicate the log entry to the followers. An entry is considered *committed* once a majority of the nodes (including the leader) have acknowledged it. You need to handle scenarios where followers may be unavailable or slow to respond. You do not need to implement persistence to disk - you can consider the log to be stored in memory.

3.  **Fault Tolerance:** The system must continue to function correctly even if up to `f` nodes fail. Node failures can be simulated by simply stopping the node's process.  The remaining nodes should still be able to elect a new leader and continue replicating operations. This also includes the case where the leader might fail.

4.  **Efficiency:** Strive for reasonable performance in terms of message passing and operation throughput.  Minimize unnecessary communication.

**Constraints:**

*   `N` (number of nodes): Configurable, but assume `3 <= N <= 7`.
*   `f` (number of tolerated failures): Must satisfy `f < N/2`.
*   Network: Assume a reliable network where messages are eventually delivered, but delivery order is not guaranteed. Messages can be lost, delayed, or duplicated.
*   Timeouts: Implement appropriate timeouts for heartbeats and election processes to handle network delays and node failures.
*   Log Entries: For simplicity, each log entry can be represented as a simple integer.
*   Safety: The system must never commit conflicting operations. Each operation must be committed in the same order on all nodes.
*   Liveness: Under normal operating conditions (less than `f` failures), the system should eventually commit operations submitted by clients.

**Testing:**

Your solution will be tested by simulating node failures, network delays, and message loss. The tests will verify that the system can correctly elect a leader, replicate log entries, and maintain consistency even in the presence of faults. The tests will also evaluate the system's throughput and latency.

**Bonus Challenges (Optional):**

*   Implement log compaction to limit the size of the log.
*   Optimize the log replication process to reduce latency and increase throughput.
*   Handle network partitions where the nodes are divided into two or more isolated groups.
*   Implement a mechanism for nodes to recover from failures and rejoin the cluster.

This problem requires a solid understanding of distributed systems principles, consensus algorithms, and fault tolerance techniques. Good luck!
