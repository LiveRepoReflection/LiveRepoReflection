Okay, here's a challenging coding problem designed to be akin to a LeetCode Hard level question, focusing on efficiency, data structures, and real-world applicability.

## Question: Distributed Transaction Ordering

**Problem Description:**

You are tasked with designing a system for ordering transactions in a distributed database system.  Imagine a scenario where multiple clients are sending transactions to a cluster of database nodes.  Each transaction needs to be processed in a globally consistent order to maintain data integrity.

You are given a stream of transactions arriving at a central coordinator node. Each transaction has the following attributes:

*   `transaction_id`: A unique string identifier for the transaction.
*   `dependencies`: A list of `transaction_id` strings representing transactions that *must* be processed before this transaction.  This creates a directed acyclic graph (DAG) of transaction dependencies.
*   `timestamp`: A monotonically increasing integer representing the time the transaction arrived at the coordinator. This timestamp is *not* necessarily globally unique or synchronized across all nodes. It serves only as a tie-breaker when dependencies are met.

Your goal is to write a function `order_transactions(transactions)` that takes a list of transaction dictionaries and returns a list of `transaction_id` strings representing the order in which the transactions should be processed. The order must satisfy the following constraints:

1.  **Dependency Constraint:**  A transaction cannot be added to the ordered list until all of its dependencies are present in the ordered list.

2.  **Timestamp Tie-breaker:** If multiple transactions are ready to be processed (i.e., all dependencies are satisfied), the transaction with the *earliest* timestamp should be processed first.

3.  **Optimized for Throughput:** The ordering algorithm should be optimized for throughput, as the system must handle a high volume of transactions. Minimize latency for each transaction as much as possible.

**Input:**

A list of dictionaries, where each dictionary represents a transaction:

```python
transactions = [
    {"transaction_id": "T1", "dependencies": [], "timestamp": 1678886400},
    {"transaction_id": "T2", "dependencies": ["T1"], "timestamp": 1678886405},
    {"transaction_id": "T3", "dependencies": ["T1"], "timestamp": 1678886402},
    {"transaction_id": "T4", "dependencies": ["T2", "T3"], "timestamp": 1678886410},
    {"transaction_id": "T5", "dependencies": [], "timestamp": 1678886401},
]
```

**Output:**

A list of transaction IDs in the correct processing order:

```python
["T1", "T5", "T3", "T2", "T4"]
```

**Constraints and Considerations:**

*   The input list `transactions` can be very large (up to 100,000 transactions).
*   The dependency graph is guaranteed to be acyclic (a DAG).
*   The timestamps are integers, and while monotonically increasing for a given client, they are not globally synchronized, so they should *only* be used as tie-breakers.
*   The solution should be efficient in terms of both time and space complexity. Aim for an algorithm that performs significantly better than a naive O(n^2) approach, where n is the number of transactions.
*   Consider the choice of data structures carefully to optimize for insertion, lookup, and retrieval operations.
*   Handle edge cases gracefully. For example, what if a dependency is missing from the input? Raise an appropriate exception (e.g., `ValueError`).

This problem requires careful consideration of data structure choices and algorithm design to meet the efficiency requirements. Good luck!
