## Question: Distributed Transaction Coordinator

### Question Description

You are tasked with designing and implementing a distributed transaction coordinator for a highly concurrent, eventually consistent distributed database system. This system consists of multiple independent storage nodes, each responsible for storing a subset of the overall data. Clients interact with the system by submitting transactions, each of which may involve operations (read/write) on multiple storage nodes.

Your goal is to implement a transaction coordinator that ensures atomicity and durability across these distributed operations, while maximizing throughput and minimizing latency. Due to the scale of the system, strict ACID properties are not feasible. Instead, you will implement a simplified version of a two-phase commit (2PC) protocol with the following characteristics:

1.  **Transaction Submission:** Clients submit transactions to the coordinator. Each transaction consists of a list of operations, where each operation specifies a storage node and the data to be read or written.

2.  **Prepare Phase:** The coordinator sends a "prepare" message to all storage nodes involved in the transaction. Each storage node attempts to tentatively apply its portion of the transaction. If successful, it logs the tentative changes and replies with "prepared". If any node fails (due to conflicts, resource limits, etc.), it replies with "abort".

3.  **Commit/Abort Phase:** If *all* storage nodes reply with "prepared", the coordinator sends a "commit" message to all nodes. Each node then permanently applies the changes from its log. If *any* node replies with "abort", the coordinator sends an "abort" message to all nodes. Each node then discards the tentative changes from its log.

4.  **Coordinator Failure Recovery:** If the coordinator fails after sending "prepare" but before sending "commit" or "abort", storage nodes must be able to resolve the transaction outcome on their own.  They should implement a timeout mechanism. If a storage node doesn't receive a "commit" or "abort" message within a defined timeout period after sending "prepared", it should assume the coordinator has failed.  Nodes should then attempt to contact other nodes involved in the transaction to determine the transaction's global status (i.e., whether any other node aborted). If any node aborted, the node should abort as well. If all nodes prepared, the node should commit.  Implement a simple gossip protocol for nodes to share their status.

5.  **Concurrency Control:** Assume the storage nodes have a basic mechanism for detecting write-write conflicts during the prepare phase. This mechanism is not your responsibility to implement. Your coordinator simply needs to handle the "abort" responses from the nodes.

**Constraints and Requirements:**

*   **Scalability:** The coordinator must be able to handle a large number of concurrent transactions.
*   **Fault Tolerance:** The system must be resilient to storage node failures and coordinator failures (as described above).
*   **Latency:** Minimize the latency of transaction processing.
*   **Eventual Consistency:** The system is eventually consistent. It is acceptable for some transactions to be aborted due to conflicts or failures.
*   **No strict ACID properties:** Transactions do not need to be isolated in the traditional sense. Concurrent transactions may see intermediate states.
*   **Timeout:** Implement a configurable timeout for storage nodes to wait for a commit/abort decision from the coordinator.
*   **Gossip Protocol:** Implement a simple gossip protocol for nodes to share their transaction status after the coordinator fails. Nodes should randomly select a subset of other involved nodes to query.
*   **Optimistic Locking:** The storage nodes use optimistic locking (versioning) to detect write-write conflicts.
*   **No External Libraries Allowed**: Only use the standard Java libraries for core implementation.

**Input:**

*   A list of transactions, where each transaction is a list of operations.
*   Each operation is a tuple: `(storage_node_id, operation_type, data_key, data_value)`.
    *   `storage_node_id`: A unique identifier for the storage node.
    *   `operation_type`: Either "read" or "write".
    *   `data_key`: The key of the data to be read or written.
    *   `data_value`: The value to be written (only applicable for "write" operations).

**Output:**

*   For each transaction, return a boolean indicating whether the transaction was committed (`true`) or aborted (`false`).

This problem requires careful consideration of concurrency, fault tolerance, and distributed systems principles. A well-designed solution will balance these competing factors to achieve a robust and performant distributed transaction coordinator.
