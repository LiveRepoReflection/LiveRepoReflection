## Project Name: Distributed Transaction Coordinator

### Question Description

You are tasked with designing and implementing a distributed transaction coordinator for a simplified banking system. This system involves multiple independent bank services (simulated as Java classes), each responsible for managing accounts in their respective regions. A transaction involves transferring funds between accounts potentially residing in different bank services.

Your coordinator needs to ensure ACID (Atomicity, Consistency, Isolation, Durability) properties across these distributed transactions. Due to network unreliability and potential service failures, this is a challenging task.

Specifically, you need to implement the following:

1.  **Bank Service Interface:** Define an interface `BankService` with methods for:
    *   `boolean debit(String accountId, double amount)`: Debits the specified amount from the account. Returns `true` if successful, `false` otherwise (e.g., insufficient funds).
    *   `boolean credit(String accountId, double amount)`: Credits the specified amount to the account. Returns `true` if successful, `false` otherwise.
    *   `boolean prepareDebit(String accountId, double amount)`: Reserves the funds for debit. Returns `true` if successful, `false` otherwise.
    *   `boolean prepareCredit(String accountId, double amount)`: Reserves the capacity for credit. Returns `true` if successful, `false` otherwise.
    *   `boolean commitDebit(String accountId, double amount)`: Commits the debit operation. Returns `true` if successful, `false` otherwise.
    *   `boolean commitCredit(String accountId, double amount)`: Commits the credit operation. Returns `true` if successful, `false` otherwise.
    *   `boolean rollbackDebit(String accountId, double amount)`: Rollbacks the debit operation. Returns `true` if successful, `false` otherwise.
    *   `boolean rollbackCredit(String accountId, double amount)`: Rollbacks the credit operation. Returns `true` if successful, `false` otherwise.
    *   `boolean isAlive()`:  Check if the bank service is alive. Returns `true` if the bank is available, `false` otherwise.

2.  **Transaction Coordinator:** Implement a class `TransactionCoordinator` with a method:
    *   `boolean transfer(String fromAccountId, String toAccountId, double amount, List<BankService> bankServices)`:  Initiates a distributed transaction to transfer `amount` from `fromAccountId` to `toAccountId` across the provided `bankServices`.

3.  **Two-Phase Commit (2PC) Protocol:** Your `transfer` method *must* implement the 2PC protocol to guarantee atomicity. This involves:
    *   **Phase 1 (Prepare):** The coordinator sends a "prepare" message to all involved bank services (`prepareDebit` and `prepareCredit`). Each service attempts to tentatively perform its part of the transaction and replies with a "vote" (yes/no).
    *   **Phase 2 (Commit/Rollback):** If all services vote "yes," the coordinator sends a "commit" message to all services (`commitDebit` and `commitCredit`). If any service votes "no," the coordinator sends a "rollback" message to all services (`rollbackDebit` and `rollbackCredit`).

4.  **Fault Tolerance:** Your coordinator must be resilient to service failures. Implement the following fault-tolerance mechanisms:
    *   **Timeout:** If a service doesn't respond to a "prepare" message within a reasonable timeout (e.g., 5 seconds), the coordinator should consider the service failed and initiate a rollback.
    *   **Retry:**  If a service fails during the commit or rollback phase, the coordinator should retry the operation multiple times (e.g., 3 retries) with exponential backoff.
    *   **Idempotency:** Ensure that all operations on the `BankService` are idempotent. This means that repeating the same operation multiple times has the same effect as performing it once. This is crucial for handling retries.

5.  **Logging:** Implement basic logging to track the progress of transactions, including prepare votes, commit/rollback decisions, and any retries due to failures.

**Constraints:**

*   You can assume a simplified network model where messages are eventually delivered, but can be delayed or lost.
*   You do not need to implement persistence of transaction state. The coordinator only needs to manage transactions in memory during the lifetime of the program.
*   Focus on the core 2PC protocol and fault-tolerance aspects. You do not need to implement a full-fledged banking system.
*   The `BankService` implementations are unreliable. They can randomly fail and recover. Simulate this in your test cases.

**Evaluation Criteria:**

*   Correctness: Does the solution correctly implement the 2PC protocol and ensure ACID properties?
*   Fault Tolerance: Does the solution handle service failures gracefully?
*   Efficiency: Is the solution reasonably efficient in terms of resource usage?
*   Code Quality: Is the code well-structured, readable, and maintainable?
*   Logging: Is the logging informative and helpful for debugging?

This problem requires a solid understanding of distributed systems concepts, concurrency, and exception handling. It's designed to test the candidate's ability to design and implement a complex system with real-world constraints. Good luck!
