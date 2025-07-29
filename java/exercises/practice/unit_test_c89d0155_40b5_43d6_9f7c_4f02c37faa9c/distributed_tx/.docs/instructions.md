## Question: Distributed Transaction Coordinator

### Question Description

You are tasked with designing and implementing a distributed transaction coordinator for a simplified banking system. This system involves multiple independent bank services (simulated as Java classes) that need to participate in atomic transactions.  A transaction might involve transferring funds between accounts located in different bank services.

The goal is to ensure that either all operations within a transaction succeed (commit) or all operations are rolled back (abort), even in the face of service failures or network issues.

Each bank service provides the following interface:

```java
interface BankService {
    boolean debit(String accountId, double amount) throws InsufficientFundsException;
    boolean credit(String accountId, double amount);
    boolean prepare(String transactionId, List<Operation> operations);
    boolean commit(String transactionId);
    boolean rollback(String transactionId);
}

class Operation {
    String accountId;
    double amount;
    OperationType type;
}

enum OperationType {
    DEBIT, CREDIT
}

class InsufficientFundsException extends Exception {
    // ...
}
```

Your task is to implement a `TransactionCoordinator` class that manages the execution of distributed transactions across these `BankService` instances.  The coordinator should adhere to the Two-Phase Commit (2PC) protocol.

**Functionality:**

1.  **`begin()`:** Starts a new transaction and returns a unique `transactionId`.
2.  **`enlist(BankService service, List<Operation> operations)`:**  Registers a `BankService` and its associated operations to participate in the current transaction. Each operation consists of account ID, amount and transaction type.
3.  **`commit(String transactionId)`:**  Initiates the 2PC protocol to commit the transaction. This involves:
    *   Sending a `prepare` message to all enlisted `BankService` instances.
    *   If all `BankService` instances successfully prepare, sending a `commit` message to all of them.
    *   If any `BankService` fails to prepare, sending a `rollback` message to all of them.
    *   The `commit` method must handle potential service failures (e.g., network timeouts, exceptions) during the prepare, commit and rollback phases. It should retry a reasonable number of times with an exponential backoff strategy before giving up and marking the transaction as failed.
4.  **`rollback(String transactionId)`:** Rolls back a transaction in case of failure, sending a `rollback` message to all enlisted `BankService` instances.  Similar to `commit`, handle service failures with retries and backoff.
5.  **`getTransactionStatus(String transactionId)`:** Returns the status of a transaction. Status can be `PENDING`, `COMMITTED`, `ABORTED`.

**Constraints and Requirements:**

*   **Atomicity:** The transaction must be atomic; either all operations succeed, or all are rolled back.
*   **Durability:** Once a transaction is committed, the changes must be durable, even if the coordinator crashes.  *Assume the bank services handle their own durability*.
*   **Concurrency:** The coordinator should be thread-safe and able to handle multiple concurrent transactions.
*   **Fault Tolerance:** The coordinator should handle transient service failures gracefully, retrying operations where appropriate.
*   **Idempotency:** The prepare, commit, and rollback operations on the `BankService` should be idempotent.
*   **Optimization:** Minimize the impact on BankService performance.
*   **Logging:**  Implement basic logging to record transaction events (start, prepare, commit, rollback, service failures).
*   **Scalability:** Consider how your design could scale to handle a large number of bank services and transactions. You don't need to implement scaling, but address the considerations in your design.
*   **Deadlock avoidance:** Explain potential deadlock situations and how to avoid it.

**Edge Cases:**

*   Empty transaction (no enlisted services).
*   Bank service failing during the prepare phase.
*   Bank service failing during the commit or rollback phase.
*   Network timeouts between the coordinator and bank services.
*   Concurrent access to the same account from different transactions (bank services should handle this with their own concurrency control mechanisms, *assume this is handled*).

**Bonus (Optional):**

*   Implement a recovery mechanism for the coordinator. After a crash, the coordinator should be able to determine the status of ongoing transactions and complete them.
*   Implement a timeout mechanism for transactions. If a transaction takes too long to complete, it should be automatically rolled back.

This problem requires a solid understanding of distributed systems concepts, concurrency, and exception handling. The solution should be well-structured, robust, and efficient. Good luck!
