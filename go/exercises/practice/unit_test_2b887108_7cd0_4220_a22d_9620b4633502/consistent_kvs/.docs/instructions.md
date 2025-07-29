## Problem Title: Distributed Key-Value Store with Consistency Guarantees

### Question Description

You are tasked with designing and implementing a simplified distributed key-value store with consistency guarantees. The system consists of multiple nodes that can communicate with each other over a network. Your implementation should support the following operations:

*   `Put(key, value)`: Writes the given value to the specified key.
*   `Get(key)`: Reads the value associated with the given key.

**Consistency Requirements:**

Your system must provide **sequential consistency**. This means that the result of any execution is the same as if the operations of all the nodes were executed in some sequential order, and the operations of each individual node appear in this sequence in the order specified by its program.

**System Design Considerations:**

*   **Fault Tolerance:** The system should be able to tolerate a certain number of node failures.
*   **Concurrency:** Multiple clients may be accessing the system concurrently.
*   **Scalability:** The system should be designed to handle a large number of keys and values.
*   **Network:** Assume the network is unreliable and messages can be lost, duplicated, or arrive out of order. However, you can assume that if two nodes can communicate, they eventually will.

**Implementation Details:**

1.  **Data Partitioning:** Implement a consistent hashing mechanism to distribute keys across the nodes.
2.  **Replication:** Implement data replication to ensure fault tolerance. You must allow the user to specify the replication factor (the number of nodes that store each key-value pair).
3.  **Consensus:** Implement a consensus algorithm (e.g., Raft, Paxos, or a simplified version suitable for this problem) to ensure that all replicas agree on the order of operations.
4.  **Client Interaction:** Implement a client library that allows clients to interact with the distributed key-value store. The client should be able to discover the available nodes and send requests to them. The client should also handle retries in case of failures.

**Constraints:**

*   The number of nodes in the system can vary.
*   The replication factor must be configurable.
*   The size of keys and values can be large.
*   The system must be able to handle a high volume of read and write requests.
*   You should optimize for read performance while maintaining sequential consistency.
*   Assume a crash-fault-tolerant model (nodes can fail by crashing).
*   Provide mechanisms for node discovery and failure detection.

**Deliverables:**

*   A well-documented Go codebase implementing the distributed key-value store.
*   A design document describing the architecture of your system, the data structures used, the consensus algorithm implemented, and the fault tolerance mechanisms employed. The document should also discuss the trade-offs made in the design and justify the choices made.
*   A set of unit tests and integration tests to verify the correctness and performance of your implementation. Include tests that specifically check the sequential consistency of the system under concurrent access and node failures.
*   A simple benchmark to measure the read and write throughput of your system under different load conditions and replication factors.

**Evaluation Criteria:**

*   Correctness: The system must correctly implement the `Put` and `Get` operations and provide sequential consistency.
*   Fault Tolerance: The system must be able to tolerate node failures without losing data or compromising consistency.
*   Performance: The system should have good read and write throughput.
*   Scalability: The system should be able to handle a large number of keys and values.
*   Code Quality: The code should be well-structured, well-documented, and easy to understand.
*   Design: The design should be well-thought-out and justify the choices made.

**Bonus:**

*   Implement a mechanism for automatic node recovery.
*   Implement a mechanism for dynamic reconfiguration of the system (e.g., adding or removing nodes).
*   Implement a more sophisticated consensus algorithm (e.g., Raft or Paxos).
*   Implement support for more advanced data types (e.g., lists, sets, maps).

Good luck!
