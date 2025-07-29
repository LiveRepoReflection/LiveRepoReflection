## Problem Title: Distributed Transaction Coordinator

### Question Description:

You are tasked with designing and implementing a distributed transaction coordinator (DTC) for a simplified database system. This DTC must ensure atomicity and consistency across multiple data nodes when executing transactions.

Your system will consist of:

*   **Clients:** Entities that initiate transactions.
*   **Transaction Coordinator (TC):** The central component responsible for orchestrating the transaction across participating data nodes. This is the component you will implement.
*   **Data Nodes (DNs):** Independent database instances that store data. Each DN can execute operations (read, write) within a transaction and must support the Two-Phase Commit (2PC) protocol.

**Simplified 2PC Protocol:**

1.  **Prepare Phase:** The TC sends a "prepare" message to all participating DNs. Each DN attempts to prepare the transaction (e.g., write to a transaction log). If successful, the DN replies with "vote-commit"; otherwise, it replies with "vote-abort."
2.  **Commit/Abort Phase:**
    *   If the TC receives "vote-commit" from all DNs, it sends a "commit" message to all DNs.
    *   If the TC receives "vote-abort" from any DN, or if a timeout occurs before receiving all votes, it sends an "abort" message to all DNs.
    *   Upon receiving a "commit" message, a DN permanently applies the transaction's changes.
    *   Upon receiving an "abort" message, a DN rolls back the transaction's changes.

**Your Task:**

Implement the `TransactionCoordinator` class with the following functionalities:

*   **`begin_transaction(transaction_id)`:** Starts a new transaction with the given `transaction_id`.  A unique transaction id is guaranteed for each transaction.
*   **`register_data_node(transaction_id, data_node)`:** Registers a `data_node` as a participant in the transaction identified by `transaction_id`.
*   **`execute_transaction(transaction_id)`:** Executes the 2PC protocol for the transaction. This method should:
    1.  Send a "prepare" message to all registered DNs.
    2.  Collect votes from DNs, handling potential timeouts.
    3.  Based on the votes, send either "commit" or "abort" messages to all DNs.
    4.  Handle any exceptions raised by DNs during commit or abort.
    5.  Return `true` if the transaction committed successfully (all DNs voted to commit and successfully committed), and `false` otherwise.
*   **Concurrency:** Your implementation MUST be thread-safe.  Multiple clients may attempt to start and execute transactions concurrently.
*   **Failure Handling:**
    *   **Timeouts:** Implement a timeout mechanism for the prepare phase. If a DN doesn't respond within a specified timeout period (e.g., 5 seconds), consider its vote as "vote-abort".
    *   **Data Node Failures:** Simulate data node failures. A DN may become unavailable during the prepare, commit, or abort phases. The TC should handle these failures gracefully, ensuring the transaction eventually either commits or aborts consistently across the remaining available DNs. When a DN fails, assume the operation it was attempting (prepare, commit, abort) also fails.
    *   **Idempotency:** The commit and abort operations on DNs should be idempotent. That is, if a DN receives the same commit/abort command multiple times, it should only execute it once.
*   **Optimization (Important for performance):** Minimize the time it takes to complete a transaction. Consider using concurrent operations where possible.  The efficiency of the prepare phase will be heavily scrutinized.

**Assumptions:**

*   You can assume that the `DataNode` interface is already defined (see below).
*   You do NOT need to implement the actual database operations on the data nodes.  You only need to simulate the 2PC protocol.
*   The network is unreliable. Messages may be lost or delayed.

**Constraints:**

*   The number of data nodes participating in a transaction can be large (up to 1000).
*   Transactions may have dependencies on each other (not handled in this problem).
*   You can use any standard Java libraries for concurrency, networking, and data structures.

**DataNode Interface (Provided):**

```java
interface DataNode {
    boolean prepare(int transactionId) throws RemoteException; // Returns true for vote-commit, false for vote-abort
    void commit(int transactionId) throws RemoteException;
    void abort(int transactionId) throws RemoteException;
    boolean isAvailable(); // Returns true if the DataNode is currently available.
}

class RemoteException extends Exception {
    public RemoteException(String message) {
        super(message);
    }
}
```

**Example Usage (Illustrative):**

```java
TransactionCoordinator coordinator = new TransactionCoordinator();
int transactionId = 123;

DataNode node1 = new MockDataNode("Node1", true); // Available
DataNode node2 = new MockDataNode("Node2", true); // Available
DataNode node3 = new MockDataNode("Node3", false); // Initially unavailable

coordinator.begin_transaction(transactionId);
coordinator.register_data_node(transactionId, node1);
coordinator.register_data_node(transactionId, node2);
coordinator.register_data_node(transactionId, node3);

boolean committed = coordinator.execute_transaction(transactionId);

System.out.println("Transaction " + transactionId + " committed: " + committed);
```

**Evaluation Criteria:**

*   **Correctness:** Does the implementation correctly implement the 2PC protocol, ensuring atomicity and consistency?
*   **Concurrency:** Is the implementation thread-safe?
*   **Failure Handling:** Does the implementation handle timeouts and data node failures gracefully?
*   **Performance:** Is the implementation optimized for speed, especially in the prepare phase?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?

This problem requires a deep understanding of distributed systems concepts, concurrency, and exception handling. It is designed to be challenging and requires careful attention to detail to achieve a robust and efficient solution. Good luck!
