Okay, here's a challenging problem designed to be LeetCode Hard level, focusing on graph manipulation, optimization, and handling potentially massive datasets.

### Question: Distributed Transaction Validation

**Problem Description:**

You are building a distributed database system. A crucial part of the system is ensuring the atomicity of transactions, meaning that a transaction either completes fully across all nodes in the system, or it is rolled back entirely. To achieve this, you need to validate whether a set of transactions, distributed across multiple nodes, are consistent and non-conflicting.

The system consists of `N` nodes, numbered from `1` to `N`.  Each node holds a partial view of the transactions.

You are given a list of transactions. Each transaction is represented by a tuple: `(transaction_id, node_id, operation, data)`.

*   `transaction_id`: A unique string identifying the transaction.
*   `node_id`: An integer representing the node where this part of the transaction is being executed.
*   `operation`: A string representing the operation being performed ("READ", "WRITE", "DELETE").
*   `data`: A string representing the data involved in the operation.

A transaction is considered **valid** if and only if all its parts across different nodes are consistent. Two transactions are considered **conflicting** if they access the same data on the same node with conflicting operations.  `WRITE` and `DELETE` are in conflict with `READ`, `WRITE` and `DELETE`.  `READ` operations are not in conflict with each other.

Your task is to determine if the given set of transactions is valid and non-conflicting.

**Input:**

A list of transactions, where each transaction is a tuple `(transaction_id, node_id, operation, data)`.

**Output:**

A boolean value: `True` if all transactions are valid and non-conflicting, `False` otherwise.

**Constraints:**

*   `1 <= N <= 10^5` (Number of nodes)
*   `1 <= len(transactions) <= 10^6` (Number of transactions)
*   `1 <= len(transaction_id) <= 20`
*   `1 <= len(data) <= 50`
*   Transaction IDs are unique.
*   Node IDs are within the range `[1, N]`.

**Edge Cases and Considerations:**

*   A transaction might not have entries on all nodes. It might only exist on a subset of nodes.
*   The input list `transactions` might contain duplicate entries (same `transaction_id`, `node_id`, `operation`, `data`). You should handle these duplicates correctly.
*   The size of the input data can be large, so optimize for memory usage and algorithmic efficiency.
*   Consider the case where there are no transactions.
*   Consider the case where some transactions are incomplete (missing parts). This alone does not make the dataset invalid, but it could lead to conflicts.

**Optimization Requirements:**

*   Aim for a solution with time complexity better than O(M^2), where M is the number of transactions.  Consider algorithms that can leverage efficient data structures for lookups and comparisons.
*   Minimize memory usage, especially if dealing with a large number of transactions. Avoid creating unnecessary copies of the input data.

**Grading Criteria:**

*   Correctness: The solution must correctly identify valid and non-conflicting transaction sets.
*   Efficiency: The solution must be efficient in terms of both time and memory usage, especially for large input datasets.
*   Code Clarity: The code should be well-structured and easy to understand.
*   Handling Edge Cases: The solution must handle all edge cases and constraints correctly.

This problem requires a combination of careful data structure selection, efficient algorithm design, and attention to detail to handle all the constraints and edge cases. Good luck!
