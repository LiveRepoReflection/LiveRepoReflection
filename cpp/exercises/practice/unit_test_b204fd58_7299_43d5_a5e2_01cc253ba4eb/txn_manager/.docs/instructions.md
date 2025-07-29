Okay, here's a challenging C++ coding problem designed to be difficult and require efficient algorithms and data structures.

**Problem Title:** Distributed Transaction Manager

**Problem Description:**

You are tasked with implementing a simplified distributed transaction manager for a system of interconnected nodes. These nodes represent independent databases, and the transaction manager is responsible for ensuring ACID (Atomicity, Consistency, Isolation, Durability) properties across transactions that span multiple nodes.

The system consists of *N* nodes, numbered from 0 to *N-1*.  Each node can perform local transactions, and a global transaction might involve operations on multiple nodes.

**Input:**

The input will be provided as a sequence of transaction requests. Each request is one of the following types:

1.  **BEGIN *TID***: Begins a new transaction with transaction ID *TID*. Transaction IDs are unique positive integers.
2.  **WRITE *TID* *NODE* *KEY* *VALUE***:  Writes *VALUE* to *KEY* on *NODE* within transaction *TID*.  *NODE* is the node ID (0 to *N-1*), *KEY* is a string, and *VALUE* is an integer.  A node can only store one value per key.
3.  **READ *TID* *NODE* *KEY***: Reads the value of *KEY* on *NODE* within transaction *TID*. If the key does not exist, return NULL.
4.  **COMMIT *TID***: Commits transaction *TID*. All writes within this transaction should become durable and visible to subsequent transactions.
5.  **ROLLBACK *TID***: Rolls back transaction *TID*. All writes within this transaction should be discarded.

**Output:**

For each **READ** request, output the value read from the specified node and key, or "NULL" if the key does not exist. For **COMMIT** and **ROLLBACK** requests, output "OK".

**Constraints:**

*   1 <= *N* <= 100 (Number of nodes)
*   1 <= Number of Transaction Requests <= 10<sup>6</sup>
*   1 <= *TID* <= 10<sup>6</sup>
*   0 <= *VALUE* <= 10<sup>9</sup>
*   The length of *KEY* will not exceed 10 characters.
*   Multiple transactions can be active concurrently.
*   Implement a Two-Phase Commit (2PC) protocol to ensure atomicity.
*   Implement strict serializability of transactions.  Ensure that the effects of committed transactions are visible in the order they are committed.
*   The system must be resilient to node failures during the commit process.  Assume any node can fail at any time. If a node fails during the commit phase of a transaction, that transaction must be rolled back on the remaining nodes.
*   Optimize for throughput. Minimize the latency of individual operations while ensuring all constraints are met.
*   Memory Usage must be controlled, ensure that memory use is within reasonable limits

**Example Input:**

```
BEGIN 1
WRITE 1 0 "x" 10
READ 1 0 "x"
WRITE 1 1 "y" 20
COMMIT 1
BEGIN 2
READ 2 0 "x"
READ 2 1 "y"
ROLLBACK 2
```

**Example Output:**

```
10
OK
10
20
OK
```

**Judging Criteria:**

The solution will be judged based on the following criteria:

*   **Correctness:** Does the solution produce the correct output for all valid inputs?
*   **Performance:** How quickly does the solution process a large number of requests?
*   **Scalability:** How well does the solution scale as the number of nodes and the number of concurrent transactions increase?
*   **Robustness:** How well does the solution handle node failures and other error conditions?
*   **Code Quality:** Is the code well-structured, well-documented, and easy to understand?

This problem requires careful consideration of data structures, algorithms, concurrency, and fault tolerance. Good luck!
