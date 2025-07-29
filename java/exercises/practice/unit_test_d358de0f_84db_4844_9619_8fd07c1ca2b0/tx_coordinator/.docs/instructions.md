## Problem: Distributed Transaction Coordinator with Conflict Resolution

**Description:**

You are tasked with designing and implementing a distributed transaction coordinator for a highly concurrent, geographically distributed system. This system manages a set of shared resources. Each transaction involves multiple operations across different resources, and strong consistency is required. Due to network latency and potential failures, traditional two-phase commit (2PC) protocols are deemed too slow and brittle.  Your coordinator should aim for *eventual* consistency while minimizing the impact of conflicts.

**System Model:**

*   **Resources:** Represented by unique IDs. Resources can be read from or written to. Resources are distributed across multiple nodes.
*   **Transactions:** Each transaction has a unique ID and consists of a series of operations. An operation specifies the resource ID, the type of operation (READ or WRITE), and, for WRITE operations, the data to be written.
*   **Nodes:**  Nodes host a subset of the resources. They can process read and write operations.
*   **Coordinator:** Your distributed transaction coordinator. It receives transaction requests, orchestrates the operations across the relevant nodes, and resolves conflicts.

**Requirements:**

1.  **Concurrency Control:** Implement a conflict detection and resolution mechanism. Assume WRITE-WRITE conflicts are the most significant. You can choose your conflict resolution strategy (e.g., last-write-wins, timestamp-based resolution, application-specific conflict resolution logic). Justify your choice based on potential trade-offs.

2.  **Fault Tolerance:** The system must tolerate node failures. Design the coordinator such that transactions can still eventually complete even if some nodes are temporarily unavailable. Consider using techniques like transaction logging, replication, or quorum-based consensus.

3.  **Scalability:** The coordinator should be able to handle a large number of concurrent transactions and a large number of resources. Consider partitioning the transaction processing and/or resource management across multiple coordinator instances.

4.  **Asynchronous Communication:**  The coordinator should use asynchronous communication (e.g., message queues, asynchronous procedure calls) to interact with the nodes.  This is crucial for minimizing latency and improving responsiveness.

5.  **Idempotency:**  Ensure all operations are idempotent. This is critical for handling retries after failures and preventing data corruption.

6. **Real-Time Conflict Notification:** When a conflict is detected and resolved, the system must notify any affected transactions about the resolution and final state of the involved resources. This allows applications to react accordingly. The notification mechanism must be efficient and scalable.

**Constraints:**

*   **Latency:** Minimize the latency of transaction completion. Aim for eventual consistency but strive for low latency under normal operating conditions.
*   **Resource Utilization:** Optimize the use of resources (CPU, memory, network bandwidth). Avoid unnecessary overhead.
*   **Complexity:**  Keep the design as simple as possible while meeting the requirements. Document your design decisions and trade-offs clearly.
*   **Data Consistency:** Ensure eventual data consistency across all resources involved in a transaction.

**Input:**

The input to your system will be a stream of transaction requests. Each request contains:

*   Transaction ID
*   List of operations (resource ID, operation type, data for WRITE operations)

**Output:**

For each transaction, the system should eventually produce an outcome (COMMIT or ABORT) along with the final state of any resources modified by the transaction (after conflict resolution).  The output should also include the list of transactions notified due to conflict resolution for each transaction.

**Evaluation Criteria:**

Your solution will be evaluated based on:

*   **Correctness:**  Does the system correctly implement the distributed transaction protocol and conflict resolution?
*   **Performance:**  How does the system perform under high load and with simulated node failures? (Latency, throughput, resource utilization)
*   **Scalability:** Can the system handle a large number of transactions and resources?
*   **Fault Tolerance:**  How well does the system tolerate node failures and network partitions?
*   **Code Quality:** Is the code well-structured, documented, and maintainable?
*   **Design Justification:** Are the design decisions clearly explained and justified?
