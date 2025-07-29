## Question: Distributed Transaction Coordinator

**Problem Description:**

You are tasked with designing and implementing a distributed transaction coordinator for a simplified banking system. This system involves multiple independent bank servers, each responsible for managing a subset of customer accounts. A single transaction might involve transferring funds between accounts residing on different bank servers. Your coordinator must ensure the ACID properties (Atomicity, Consistency, Isolation, Durability) are maintained across these distributed transactions.

**System Architecture:**

*   **Bank Servers:** Each bank server holds a set of accounts and can perform local operations (deposit, withdraw, getBalance) on those accounts. They expose a simple API for these operations. You can assume this API is already implemented and reliable within a single server. The server exposes endpoint using `serverID`.
*   **Transaction Coordinator:** Your core task is to implement the transaction coordinator. It receives transaction requests from clients, coordinates the actions across the relevant bank servers, and ensures that the transaction either commits successfully on all servers or rolls back on all servers, maintaining data consistency.

**Transaction Request:**

A transaction request consists of a list of operations. Each operation specifies:

*   `serverID`: The ID of the bank server involved.
*   `accountID`: The ID of the account to be modified.
*   `operationType`: (Deposit, Withdraw)
*   `amount`: The amount to be deposited or withdrawn.

**Constraints and Requirements:**

1.  **Atomicity:** All operations within a transaction must either succeed on all involved bank servers or fail on all of them.
2.  **Consistency:** Transactions must leave the system in a valid state. The total amount of money in the system should remain consistent.
3.  **Isolation:** Concurrent transactions must not interfere with each other. The result of executing concurrent transactions should be the same as executing them in some serial order.
4.  **Durability:** Once a transaction is committed, the changes must be permanent, even in the face of server crashes or network failures.
5.  **Concurrency:** The coordinator must handle multiple concurrent transaction requests efficiently.
6.  **Fault Tolerance:** The coordinator should be reasonably resilient to temporary network failures and server outages.  Implement a retry mechanism for communication with bank servers.
7.  **Deadlock Avoidance:** Design your protocol to avoid deadlocks between transactions.
8.  **Optimization:** Minimize the number of network round trips between the coordinator and the bank servers.
9.  **Logging:** Implement a robust logging mechanism to record transaction states and operations. This log should be sufficient to recover from a coordinator crash. Consider the trade-offs between log size and recovery speed.
10. **Scalability:** Although you don't need to simulate a massive number of servers, consider the scalability implications of your design. How would your solution adapt to a significantly larger number of bank servers and concurrent transactions?
11. **Server API Assumption:** Assume the bank servers provide the following (simplified) API, which you can access via network calls (e.g., using HTTP or gRPC - you can choose your communication protocol):

    *   `prepare(transactionID, operations)`:  Bank server attempts to tentatively apply the operations for the given transaction. Returns `true` if successful (server is ready to commit), `false` otherwise (server cannot commit due to insufficient funds, account locked, etc.).  The bank server **must** hold the state of the transaction until a commit or rollback command is received.
    *   `commit(transactionID)`: Bank server permanently applies the changes for the given transaction.
    *   `rollback(transactionID)`: Bank server discards the tentative changes for the given transaction.

**Deliverables:**

Implement the transaction coordinator logic in Java. Your solution should include:

*   The core coordinator class.
*   A description of the chosen transaction protocol (e.g., 2PC with optimizations).
*   Implementation of any necessary logging mechanisms.
*   Clear documentation outlining the design choices, trade-offs, and limitations of your solution.
*   A brief explanation of how your design addresses the ACID properties, concurrency, fault tolerance, deadlock avoidance, and scalability requirements.

This problem emphasizes a solid understanding of distributed systems concepts, concurrency control, and fault tolerance techniques. The complexity lies in designing a robust and efficient coordinator that can handle concurrent transactions across multiple independent servers while guaranteeing data consistency in the face of failures.
