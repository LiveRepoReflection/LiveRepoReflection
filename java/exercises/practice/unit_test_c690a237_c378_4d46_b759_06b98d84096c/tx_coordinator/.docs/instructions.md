## Problem: Distributed Transaction Coordinator

**Description:**

You are tasked with designing and implementing a distributed transaction coordinator for a simplified banking system. This system involves multiple independent bank servers, each managing a subset of customer accounts. To ensure data consistency, cross-bank transactions (e.g., transferring money from an account in Bank A to an account in Bank B) must be atomic – either all operations succeed, or none do.

Your coordinator must implement the two-phase commit (2PC) protocol to guarantee atomicity across these distributed transactions.

**System Architecture:**

*   **Coordinator:** Your Java program will act as the central coordinator. It receives transaction requests from clients (simulated).
*   **Bank Servers:** Assume you have a set of `n` bank servers (where `n` is configurable). Each server exposes a simple API (which you can also simulate with in-memory data structures in the interest of time) with the following methods:

    *   `prepare(transactionId, operations)`:  Receives a list of operations (e.g., debit account X, credit account Y) to be performed as part of the given transaction. Returns `true` if the server is ready to commit the operations, `false` otherwise (e.g., due to insufficient funds, account does not exist).
    *   `commit(transactionId)`: Permanently applies the operations associated with the transaction.
    *   `rollback(transactionId)`: Reverts any changes made as part of the transaction.

*   **Clients:** Clients send transaction requests to the coordinator. A transaction request consists of a unique transaction ID and a list of operations distributed across multiple banks.

**Requirements:**

1.  **Two-Phase Commit (2PC):** Implement the 2PC protocol correctly.
    *   **Phase 1 (Prepare):** The coordinator sends a `prepare` message to all participating bank servers.
    *   **Phase 2 (Commit/Rollback):**
        *   If all servers reply with `true` (ready to commit), the coordinator sends a `commit` message to all servers.
        *   If any server replies with `false` (cannot commit), or if the coordinator does not receive a response from a server within a reasonable timeout, the coordinator sends a `rollback` message to all servers.
2.  **Concurrency:** Handle concurrent transaction requests efficiently.  Use appropriate synchronization mechanisms to prevent race conditions.
3.  **Timeout Handling:** Implement timeouts for `prepare` messages. If a server doesn't respond within a specified timeout, assume it cannot commit and initiate a rollback. Make sure the timeout is configurable.
4.  **Crash Recovery:**  Design the coordinator to be resilient to crashes. Consider how the coordinator can recover its state after a failure and resume the 2PC protocol.  You can simulate crash recovery by persisting the coordinator's state to disk (e.g., using serialization) before shutting down and loading it upon restart. The bank servers need not recover.
5.  **Deadlock Prevention:** Implement a deadlock prevention mechanism. For example, the coordinator could order the prepare requests in a specific order based on the participating bank server's ID.
6.  **Performance Optimization:** Minimize the latency of transaction processing. Consider techniques like asynchronous message passing (using threads or executors) to improve throughput.

**Constraints:**

*   **Simplicity:** Focus on the core 2PC logic and avoid unnecessary complexity.
*   **Scalability:** While a fully scalable solution is not required, consider how your design could be extended to handle a larger number of bank servers and concurrent transactions.
*   **Realism:** Make sure the simulator is realistic enough to represent a banking environment.

**Evaluation Criteria:**

*   **Correctness:**  Does your implementation correctly implement the 2PC protocol, ensuring atomicity?
*   **Concurrency Handling:** Does your solution handle concurrent transactions efficiently and safely?
*   **Timeout Handling:**  Are timeouts handled correctly, preventing transactions from hanging indefinitely?
*   **Crash Recovery:** Can the coordinator recover from crashes and resume the 2PC protocol?
*   **Deadlock Prevention:** Does the system prevent deadlocks?
*   **Performance:**  Is the transaction processing latency reasonable?
*   **Code Quality:** Is your code well-structured, readable, and maintainable?
*   **Design Justification:** Be prepared to explain your design choices and trade-offs.

**Example Scenario:**

1.  Client requests a transaction to transfer $100 from account A (Bank 1) to account B (Bank 2).
2.  Coordinator initiates 2PC.
3.  Coordinator sends `prepare(transactionId, [debit A])` to Bank 1.
4.  Coordinator sends `prepare(transactionId, [credit B])` to Bank 2.
5.  If both banks respond with `true` (ready to commit), the coordinator sends `commit(transactionId)` to both banks.
6.  If either bank responds with `false` (or times out), the coordinator sends `rollback(transactionId)` to both banks.
7.  The coordinator informs the client of the transaction's success or failure.

This problem requires a solid understanding of distributed systems concepts, concurrency, and error handling.  Good luck!
