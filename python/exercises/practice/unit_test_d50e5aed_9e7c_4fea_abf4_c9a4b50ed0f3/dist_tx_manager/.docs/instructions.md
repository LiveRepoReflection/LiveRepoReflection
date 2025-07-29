Okay, I'm ready. Here's a challenging problem for a high-level programming competition.

### Project Name

```
distributed-transaction-manager
```

### Question Description

You are tasked with implementing a simplified, in-memory Distributed Transaction Manager (DTM) for a system handling financial transactions across multiple independent service nodes. Each service node manages its own isolated database. The DTM is responsible for ensuring ACID properties (Atomicity, Consistency, Isolation, Durability) across these distributed transactions.

The system consists of a central DTM node and multiple service nodes. Transactions are initiated by clients, coordinated by the DTM, and executed (potentially) on multiple service nodes.

**Simplified Model:**

*   **Transaction ID (TXID):** Unique identifier for each transaction (represented as a string).
*   **Service Node:** Each service node has a unique ID (represented as a string) and manages its local data. It can perform local operations as instructed by the DTM.
*   **DTM:** The central coordinator that communicates with service nodes.
*   **Transaction States:**
    *   `PENDING`: Transaction has been initiated but not yet committed or aborted.
    *   `PREPARED`: All participating service nodes have successfully prepared the transaction (written intention logs).
    *   `COMMITTED`: Transaction has been successfully committed across all participating nodes.
    *   `ABORTED`: Transaction has been aborted.
*   **Operations:** Each transaction involves operations on one or more service nodes. Each operation is represented as a tuple `(service_node_id, operation_type, data)`.  `operation_type` can be 'debit' or 'credit', and data is an integer representing the amount.

**Your Task:**

Implement the following core functionalities for the DTM:

1.  **`begin_transaction()`:**
    *   Generates a new, unique TXID.
    *   Initializes the transaction state to `PENDING`.

2.  **`add_operation(txid, service_node_id, operation_type, data)`:**
    *   Adds an operation to the specified transaction.
    *   Validates that the operation is valid (e.g., `operation_type` is either 'debit' or 'credit').

3.  **`prepare_transaction(txid)`:**
    *   Initiates the "prepare" phase of the two-phase commit (2PC) protocol.
    *   For each service node involved in the transaction, send a "prepare" command with the list of operations to that node.
    *   Each service node should simulate writing an "intention log" (you don't need to persist anything to disk, just track the intention in memory). If any of the prepare operation fails (e.g., insufficient funds for a debit), that service node should respond with an error.
    *   If all service nodes successfully prepare, the DTM sets the transaction state to `PREPARED`. Otherwise, the DTM sets the transaction state to `ABORTED` and informs all participating service nodes to rollback (undo the intention logs).

4.  **`commit_transaction(txid)`:**
    *   Initiates the "commit" phase of the 2PC protocol.
    *   Only commits if the transaction is in the `PREPARED` state.
    *   Sends a "commit" command to all participating service nodes.
    *   Service nodes execute the operations based on the intention logs.
    *   If all service nodes successfully commit, the DTM sets the transaction state to `COMMITTED`. If a service node fails to commit, the DTM should set the transaction state to `ABORTED`, though the other service nodes may have committed. (This is a known issue with 2PC which is acceptable in this simplified model).

5.  **`abort_transaction(txid)`:**
    *   Aborts the transaction.
    *   Sends an "abort" command to all participating service nodes.
    *   Service nodes rollback (undo) any prepared operations from the intention logs.
    *   Sets the transaction state to `ABORTED`.

6.  **`get_transaction_state(txid)`:**
    *   Returns the current state of the transaction.

**Service Node Interface (Simulated):**

You will interact with service nodes through a simplified interface (you don't implement the service nodes themselves, just simulate their behavior). Assume the existence of the following functions:

*   `prepare(service_node_id, txid, operations)`: Simulates a service node preparing a transaction. Returns `True` if successful, `False` otherwise.
*   `commit(service_node_id, txid)`: Simulates a service node committing a transaction. Returns `True` if successful, `False` otherwise.
*   `abort(service_node_id, txid)`: Simulates a service node aborting a transaction. Returns `True` if successful, `False` otherwise.
*   `get_account_balance(service_node_id)`: Simulates getting account balance from the service node, required to test if the account balance is changed as expected after the transaction.

**Constraints:**

*   **Concurrency:** Your DTM should be thread-safe. Multiple clients might initiate transactions concurrently. Use appropriate locking mechanisms to prevent race conditions.
*   **Error Handling:** Implement proper error handling. For example, handle cases where a transaction with a given TXID does not exist.
*   **Deadlock Prevention:** Strive to minimize the risk of deadlocks. Consider the order in which you acquire locks.
*   **Scalability:** Consider how your design might scale if the number of service nodes and concurrent transactions increases significantly.  While you don't need to implement a fully distributed solution, think about the architectural implications.
*   **Idempotency (Important):** While not strictly enforced, consider how you *could* make the `commit` and `abort` operations idempotent in a real-world system (i.e., executing them multiple times has the same effect as executing them once).  Document your approach in comments. This is important for handling potential network failures.
*   **Optimizations:** Consider how you could optimize the prepare phase.  Could you potentially parallelize prepare calls to service nodes?
*   **Service Nodes Failure:** Add simulation of service nodes failure to test the robustness of the DTM.

This problem requires a solid understanding of distributed systems concepts, concurrency, and error handling. Good luck!
