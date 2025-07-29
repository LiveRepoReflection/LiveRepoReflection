Okay, here's a problem designed to be challenging and sophisticated, suitable for a high-level programming competition in Go.

**Problem Title:** Concurrent Transaction Ordering and Conflict Resolution

**Problem Description:**

You are tasked with designing a system to process a large number of financial transactions concurrently. Each transaction involves transferring funds between two accounts. To ensure data integrity and prevent inconsistencies, you need to implement a mechanism to order these transactions and resolve conflicts.

Specifically, your system must satisfy the following requirements:

1.  **Concurrent Processing:** The system should be able to handle multiple transactions simultaneously to maximize throughput.

2.  **Transaction Definition:** A transaction is defined by a tuple `(account_from, account_to, amount, timestamp)`. `account_from` and `account_to` are unique integer identifiers for the accounts, `amount` is the amount of funds to transfer, and `timestamp` is a Unix timestamp indicating the time the transaction was initiated.

3.  **Total Order:** You must establish a total order of transactions based on the following rules:

    *   **Timestamp Priority:** Transactions with earlier timestamps should be processed before transactions with later timestamps.
    *   **Account ID Tiebreaker:** If two transactions have the same timestamp, the transaction involving the smaller `account_from` should be processed first. If `account_from` is the same, then the transaction involving the smaller `account_to` should be processed first.

4.  **Conflict Detection and Resolution:** A conflict occurs when two or more transactions attempt to modify the same account concurrently. Your system must detect these conflicts and resolve them according to the following rules:

    *   **Account Balance Check:** Before applying a transaction, verify that the `account_from` has sufficient funds. If the balance is insufficient, the transaction must be rejected. The check must be atomic with the balance update.
    *   **Transaction Rejection:** If a transaction is rejected due to insufficient funds, it must be marked as rejected and its effects must not be applied. Rejected transactions should not block the processing of other transactions.

5.  **Deadlock Prevention:** The solution should avoid deadlocks while ensuring atomicity.

6.  **Scalability:** Your solution should be designed to handle a large number of accounts and transactions efficiently. Consider potential bottlenecks and optimize accordingly.

7.  **Error Handling:** Your system should gracefully handle errors such as invalid account IDs, negative amounts, and system failures.

8.  **Observability:** Your system must provide a mechanism to track the number of processed transactions, rejected transactions, and the current balance of each account.

**Input:**

The input will consist of a stream of transaction tuples in the format:

```
account_from,account_to,amount,timestamp
```

Each line represents a single transaction. The transactions are not guaranteed to be in any particular order.

**Output:**

After processing all transactions, your system should output:

1.  A list of rejected transactions, in the order they were received. Each rejected transaction should be formatted as:

```
REJECTED: account_from,account_to,amount,timestamp
```

2.  A summary of the final account balances. For each account with a non-zero balance, output a line in the format:

```
BALANCE: account_id,balance
```

The account balances should be sorted in ascending order by `account_id`.

3.  A summary of the number of transactions processed and rejected.

```
PROCESSED: processed_transaction_count
REJECTED_TOTAL: rejected_transaction_count
```

**Constraints:**

*   Number of accounts: Up to 1,000,000.
*   Number of transactions: Up to 10,000,000.
*   Account IDs: Integers between 1 and 1,000,000.
*   Transaction amounts: Positive integers between 1 and 1,000.
*   Timestamps: Unix timestamps (seconds since epoch).  Timestamps will fit into int64.
*   The system should be able to process transactions at a reasonable rate (e.g., thousands of transactions per second).
*   Memory usage should be optimized to avoid excessive memory consumption.
*   All operations related to balance updates must be atomic.

**Example Input:**

```
1,2,100,1678886400
2,3,50,1678886401
1,2,200,1678886402
3,1,75,1678886401
2,1,50,1678886403
1,2,1000,1678886404
```

**Example Output (Possible):**

```
REJECTED: 1,2,1000,1678886404
BALANCE: 1,-25
BALANCE: 2,100
BALANCE: 3,25
PROCESSED: 5
REJECTED_TOTAL: 1
```

**Grading Criteria:**

*   Correctness: The system must produce the correct output for all test cases.
*   Performance: The system should be able to process a large number of transactions efficiently.
*   Concurrency: The system should handle concurrent transactions correctly and avoid race conditions.
*   Scalability: The system should be designed to scale to a large number of accounts and transactions.
*   Code Quality: The code should be well-structured, readable, and maintainable.

This problem requires a strong understanding of concurrency, data structures, and algorithms. It also tests the ability to design a system that meets specific performance and scalability requirements. Good luck!
