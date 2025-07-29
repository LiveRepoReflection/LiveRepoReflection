## Question: Concurrent Transaction Processing with Conflict Resolution

**Problem Description:**

You are tasked with designing a concurrent transaction processing system for a simplified banking application. The system manages a set of bank accounts and must support concurrent deposit, withdrawal, and transfer operations. However, due to the concurrent nature of the system, conflicts can arise, leading to incorrect account balances or lost transactions. Your goal is to implement a robust system that handles concurrent transactions, detects and resolves conflicts, and ensures data consistency and atomicity.

**Specific Requirements:**

1.  **Account Representation:** Represent each bank account with an account ID (string) and a balance (integer).

2.  **Transaction Types:** Implement the following transaction types:
    *   `Deposit(accountID string, amount int)`: Adds the specified amount to the account balance.
    *   `Withdrawal(accountID string, amount int)`: Subtracts the specified amount from the account balance.
    *   `Transfer(fromAccountID string, toAccountID string, amount int)`: Transfers the specified amount from one account to another.

3.  **Concurrency:** The system must support concurrent execution of multiple transactions. Use goroutines and channels to achieve concurrency.

4.  **Conflict Detection and Resolution:** Implement a mechanism to detect and resolve conflicts arising from concurrent access to the same account. Consider using techniques like optimistic locking or locking with conflict detection.

5.  **Atomicity:** All transactions must be atomic. If a transaction fails midway, the system must rollback any changes made by the transaction to ensure data consistency.

6.  **Error Handling:** Implement proper error handling for various scenarios, including:
    *   Insufficient funds for withdrawals or transfers.
    *   Invalid account IDs.
    *   Conflicts during concurrent access.
    *   Unexpected system errors.

7.  **Transaction Logging:** Maintain a log of all transactions, including their status (success, failed, or rolled back). The log should include timestamps, transaction types, account IDs involved, amounts, and error messages (if any).

8. **Account snapshot:** Implement a function to save and load account's data from/to disk.

**Constraints:**

*   The system should handle a large number of concurrent transactions without significant performance degradation. (Optimized)
*   The solution should be memory-efficient.
*   The system should be resilient to failures and ensure data consistency even in the event of crashes. (Snapshot)
*   The system should be designed in a modular and maintainable way.
*   No external database or persistence mechanism is allowed except using local files.

**Scoring:**

*   Correctness: The system must correctly process transactions and maintain accurate account balances.
*   Concurrency: The system must efficiently handle concurrent transactions without introducing race conditions or data inconsistencies.
*   Performance: The system should process transactions quickly and efficiently.
*   Error Handling: The system must handle errors gracefully and provide informative error messages.
*   Code Quality: The code should be well-structured, readable, and maintainable.

**Bonus Points:**

*   Implement a deadlock detection mechanism to prevent deadlocks in the transaction processing system.
*   Implement a retry mechanism for failed transactions with exponential backoff.
*   Design a distributed transaction processing system that can handle transactions across multiple nodes.
