## Question: Distributed Transaction Manager with Consensus

### Problem Description

You are tasked with designing and implementing a simplified, yet robust, distributed transaction manager (DTM) for a system handling financial transactions across multiple independent banking services. These services (let's call them "Banks") operate independently and manage their own accounts and balances. Your DTM must ensure ACID properties (Atomicity, Consistency, Isolation, Durability) for transactions that span multiple Banks.

Due to network unreliability and potential service failures, you must implement a consensus algorithm to ensure all participating Banks agree on the outcome (commit or rollback) of a distributed transaction. You will use a simplified version of the Raft consensus algorithm for agreement.

**Simplified Raft Consensus:**

1.  **Leader Election:** Banks elect a leader. In case of leader failure, a new election should be initiated.
2.  **Log Replication:** The leader proposes a transaction log entry (containing the transaction details and participating Banks) to all other banks (followers).
3.  **Agreement:** Followers acknowledge the log entry. Once a majority of followers have acknowledged the entry, the leader marks the entry as "committed."
4.  **Commit/Rollback:** The leader sends a "commit" or "rollback" command to all participating banks based on the transaction result. All banks must execute the command consistently.

**Banks:** Each bank maintains its own account data and implements the following operations:

*   `prepare(transactionId, accountId, amount)`: Reserves the specified amount from the account. Returns `true` if successful, `false` otherwise (e.g., insufficient funds).
*   `commit(transactionId, accountId, amount)`: Finalizes the transaction, permanently deducting the reserved amount.
*   `rollback(transactionId, accountId, amount)`: Releases the reserved amount, reverting the account to its original state.

**Your Task:**

Implement the core components of the DTM, focusing on transaction coordination and consensus:

1.  **Transaction Coordinator:** This component receives transaction requests, identifies participating Banks, and initiates the distributed transaction protocol.
2.  **Raft Implementation:** Implement the core Raft leader election, log replication, and agreement mechanisms.
3.  **Transaction Protocol:** Design and implement the distributed transaction protocol using the simplified Raft consensus algorithm to ensure atomicity and consistency across participating Banks.

**Constraints and Requirements:**

*   **Concurrency:** The DTM must handle concurrent transaction requests efficiently.
*   **Fault Tolerance:** The system must tolerate failures of individual Banks and leader failures.  A new leader should be elected automatically.
*   **Durability:** Once a transaction is committed, the state must be persisted (e.g., using in-memory storage or file-based storage) to survive restarts. You can assume that the transaction logs will not be lost with the bank nodes.
*   **Isolation:** While full ACID-level isolation might be challenging to achieve perfectly, strive for a reasonable level of isolation to prevent data corruption.  Minimize race conditions.
*   **Optimization:** Consider potential optimizations to improve throughput and reduce latency. For example, explore batching of log entries or pipelining of operations.
*   **Efficiency:** The implementation must be reasonably efficient in terms of memory usage and processing time. Avoid unnecessary overhead.
*   **Error Handling:** Implement robust error handling to gracefully handle unexpected situations, such as network errors, service failures, and invalid transaction requests.
*   **Scalability:** Design the system with scalability in mind. Although you don't need to implement a fully scalable solution, consider how your design could be extended to handle a large number of Banks and transactions.
*   **Simplicity:** Strive for a clean, understandable, and well-documented code.

**Edge Cases and Considerations:**

*   **Network Partitions:**  Handle network partitions gracefully.  The system should remain consistent within each partition.
*   **Split Brain:** Prevent split-brain scenarios in the Raft implementation.
*   **Transaction Timeout:** Implement a timeout mechanism to handle long-running or stalled transactions.
*   **Duplicated Messages:** Handle duplicated messages (e.g., due to network retries) idempotently.
*   **Asynchronous Operations:**  Carefully manage asynchronous operations to avoid race conditions and ensure correct execution order.

This problem requires a deep understanding of distributed systems concepts, consensus algorithms, and transaction management. The solution will be evaluated based on its correctness, robustness, efficiency, and design principles. Good luck!
