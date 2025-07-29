## Problem: Scalable Transaction Dependency Graph Analysis

**Problem Description:**

You are building a distributed ledger system that processes a high volume of transactions.  Each transaction may depend on the successful completion of other transactions. To ensure data consistency and prevent cascading failures, you need to efficiently analyze the dependency graph of these transactions.

Specifically, you are given a stream of transactions. Each transaction is represented by a unique ID (a positive integer) and a list of transaction IDs it depends on (its dependencies).  A transaction can only be considered "ready" for processing if all its dependencies have been successfully processed.

Your task is to implement a system that can:

1.  **Accept a stream of transactions:**  The system should be able to efficiently ingest transaction data, even when the stream is very large. The transactions are not guaranteed to arrive in any particular order (e.g., a transaction might arrive before its dependencies).
2.  **Detect circular dependencies:** The system must detect circular dependencies within the transaction graph. If a circular dependency is detected, the system should raise an exception and halt further transaction processing.
3.  **Determine the order of transaction processing:**  Given the dependency graph, determine a valid order in which transactions can be processed such that all dependencies are met before a transaction is processed. If multiple valid orders exist, any one of them is acceptable.
4.  **Handle transaction failures:**  Simulate transaction failures. If a transaction fails, all transactions that depend on it (directly or indirectly) should be marked as "blocked" and not processed. The system should report the IDs of all blocked transactions.
5.  **Provide a query to return the 'ready' transactions:** Provide a query to return a list of transaction IDs that are ready to be processed. These transactions have all their dependencies met and are not blocked.

**Constraints:**

*   The number of transactions can be very large (up to 10<sup>7</sup>).
*   The dependency graph can be complex, with deeply nested dependencies and potential for cycles.
*   Transaction IDs are positive integers and can be up to 10<sup>9</sup>.
*   Efficiency is critical. The system should be able to process a large stream of transactions with minimal latency.
*   Memory usage should be optimized. Avoid storing the entire transaction graph in memory if possible, especially for extremely large datasets. However, a reasonable amount of caching is allowed to improve performance.
*   The system should be thread-safe to handle concurrent transaction submissions and queries.
*   The system should be designed to be resilient to failures. If a component of the system fails, it should be able to recover gracefully without losing data.
*   You are allowed to use standard Python libraries and data structures. However, you may need to explore specialized data structures or algorithms to meet the efficiency requirements.

**Input:**

The input consists of a stream of transactions. Each transaction is represented as a tuple: `(transaction_id, dependencies)`, where `transaction_id` is the unique ID of the transaction, and `dependencies` is a list of transaction IDs that this transaction depends on.

**Output:**

The system should provide the following functionalities:

1.  `add_transaction(transaction_id, dependencies)`: Adds a transaction to the system. Raises an exception if a circular dependency is detected.
2.  `mark_transaction_failed(transaction_id)`: Marks a transaction as failed. Updates the status of dependent transactions.
3.  `get_ready_transactions()`: Returns a list of transaction IDs that are ready to be processed.
4.  `get_blocked_transactions()`: Returns a list of transaction IDs that are blocked.

**Example:**

```python
# Assume you have implemented a class called TransactionSystem
system = TransactionSystem()

system.add_transaction(1, [])
system.add_transaction(2, [1])
system.add_transaction(3, [1, 2])
system.add_transaction(4, [3])

print(system.get_ready_transactions())  # Output: [1]

system.mark_transaction_failed(1)

print(system.get_blocked_transactions()) # Output: [2, 3, 4]

system.add_transaction(5, [])
print(system.get_ready_transactions())  # Output: [5]
```

**Scoring:**

The solution will be evaluated based on:

*   Correctness: The system should correctly detect circular dependencies, determine the correct processing order, handle transaction failures, and provide accurate results for the queries.
*   Efficiency: The system should be able to process a large stream of transactions with minimal latency and memory usage.
*   Code quality: The code should be well-structured, readable, and maintainable.
*   Thread safety: The system should be thread-safe to handle concurrent requests.
*   Resilience: The system should be designed to be resilient to failures.
