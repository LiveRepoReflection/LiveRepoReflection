## Project Name

`Distributed Key-Value Store with Strong Consistency`

## Question Description

You are tasked with designing and implementing a simplified distributed key-value store. This store must guarantee strong consistency, meaning that all clients see the same, up-to-date data, even in the presence of concurrent writes and network partitions.

**System Requirements:**

1.  **Basic Key-Value Operations:** Implement `put(key, value)` and `get(key)` operations. Keys and values are strings.

2.  **Replication:** Data must be replicated across multiple nodes (replicas) to ensure fault tolerance. The number of replicas `N` is configurable.

3.  **Strong Consistency:** All reads must return the latest written value, regardless of which replica they contact. Implement a consensus algorithm (e.g., Raft or Paxos - simplified versions are acceptable) to ensure this.

4.  **Fault Tolerance:** The system must remain available for reads and writes as long as a majority of replicas are available (at least `(N/2) + 1` replicas).

5.  **Network Partitions:**  The system must handle network partitions gracefully. If a node becomes isolated from the majority, it must not serve stale data or accept writes that could violate consistency.

6.  **Concurrency:** Handle concurrent `put` requests for the same key from different clients. The last write should win, and all clients should eventually observe this.

7.  **Scalability (Considerations):** While a full implementation isn't required, consider how your design would scale to a larger number of nodes and clients. Discuss potential bottlenecks and mitigation strategies.

**Constraints:**

*   The number of replicas `N` will be a small odd number (e.g., 3, 5, 7).
*   Assume a relatively small number of keys and values. Focus on correctness and consistency over raw performance.
*   Network communication can be simulated using message passing (e.g., channels in Rust) or a simple network library.
*   You do NOT need to handle node joins or leaves dynamically. The initial set of nodes is fixed.
*   Assume no Byzantine faults (nodes don't intentionally lie).

**Implementation Details:**

You are free to choose your own architecture and data structures, but consider the following:

*   Each node in the system should have a unique identifier.
*   Nodes communicate with each other via messages.  Define a clear message format for requests, responses, and internal consensus messages.
*   Implement a basic consensus algorithm. A simplified version of Raft or Paxos is sufficient for this problem.  Focus on the core concepts of leader election, log replication, and commitment.
*   Use appropriate data structures for storing data, logs, and node state.

**Evaluation Criteria:**

*   **Correctness:** Does the system implement `put` and `get` correctly, and does it guarantee strong consistency?
*   **Fault Tolerance:** Does the system remain available in the presence of node failures and network partitions?
*   **Concurrency Handling:** Does the system handle concurrent writes correctly?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?
*   **Design Explanation:** Can you clearly explain your design choices and the reasoning behind them?
*   **Scalability Considerations:** Do you understand the potential scalability challenges and have ideas for addressing them?

This problem is designed to be open-ended and challenging. The goal is to demonstrate your understanding of distributed systems concepts, your ability to design and implement a complex system, and your problem-solving skills. Good luck!
