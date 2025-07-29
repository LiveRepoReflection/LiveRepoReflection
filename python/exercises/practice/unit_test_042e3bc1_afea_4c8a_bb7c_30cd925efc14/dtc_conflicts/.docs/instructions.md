## Question: Distributed Transaction Coordinator with Conflict Resolution

**Problem Description:**

You are tasked with designing and implementing a simplified, in-memory distributed transaction coordinator (DTC) for a microservices architecture. The system manages transactions spanning multiple services, ensuring atomicity, consistency, isolation, and durability (ACID) principles. Due to network partitions and concurrent operations, conflicts can arise. Your solution should efficiently detect and resolve these conflicts, prioritizing data consistency and minimizing transaction rollback.

**System Architecture:**

Imagine a system with `n` services (where `1 <= n <= 100`). Each service manages its own data and participates in distributed transactions coordinated by the DTC. A transaction involves operations across multiple services.

**Transaction Model:**

Each transaction has a unique transaction ID (UUID). A transaction consists of a series of operations, each targeted at a specific service. An operation involves a read and/or write to a data item within the target service.

**Conflict Scenario:**

Two transactions, T1 and T2, can conflict if they both attempt to write to the same data item in the same service and their operations are interleaved. For example:

*   T1 writes to data item 'A' in Service 1.
*   T2 writes to data item 'A' in Service 1.

The DTC must detect these conflicts and determine which transaction should proceed, and which should be rolled back or retried.

**Requirements:**

1.  **Transaction Coordination:** Implement the core logic for coordinating distributed transactions across multiple services. The DTC receives requests to begin, commit, and rollback transactions.

2.  **Conflict Detection:** Design and implement a mechanism to detect conflicts between concurrent transactions. This mechanism should be efficient and scalable.

3.  **Conflict Resolution:** Implement a conflict resolution strategy. Your strategy should prioritize minimizing the number of transactions that need to be rolled back. Implement a "optimistic concurrency control" approach using versioning. Each data item in each service has a version number. When a transaction reads a data item, it records the version number. Before writing to a data item, the transaction must check if the version number is still the same. If it is, the write proceeds and the version number is incremented. If it is not, a conflict is detected.

4.  **Durability:** Ensure transaction logs and state are persisted in memory and are recoverable in case of DTC failure (assume a simplified in-memory representation for this exercise).

5.  **Concurrency Control:** Handle concurrent transaction requests efficiently. The DTC should be able to process multiple transactions simultaneously.

6.  **Optimization:** The solution should be optimized for minimizing latency and maximizing throughput. Consider data structures and algorithms that provide efficient conflict detection and resolution.

**Input:**

The input will consist of a series of transaction requests. Each request will be one of the following types:

*   `BEGIN <transaction_id>`: Starts a new transaction with the given ID.
*   `READ <transaction_id> <service_id> <data_item>`: Reads the specified data item from the specified service within the specified transaction.
*   `WRITE <transaction_id> <service_id> <data_item> <new_value>`: Writes the specified new value to the specified data item in the specified service within the specified transaction.
*   `COMMIT <transaction_id>`: Attempts to commit the specified transaction.
*   `ROLLBACK <transaction_id>`: Rolls back the specified transaction.

Service and Data Item IDs are integers. Data Items are strings. New Values are strings.

**Output:**

For each `COMMIT` or `ROLLBACK` request, output a message indicating the outcome:

*   `COMMIT <transaction_id> SUCCESS`: If the transaction was successfully committed.
*   `COMMIT <transaction_id> ABORTED`: If the transaction was aborted due to a conflict or other error.
*   `ROLLBACK <transaction_id> SUCCESS`: If the transaction was successfully rolled back.

For `READ` and `WRITE` requests, there is no output unless an error occurs (e.g., service not found, transaction not found). In such cases, output an error message.

**Constraints:**

*   The number of services `n` is between 1 and 100.
*   The number of concurrent transactions can be up to 1000.
*   The size of data items and new values is limited to 256 characters.
*   The total number of transaction requests can be up to 100,000.
*   All service and data item operations must be performed in memory (no external database).

**Evaluation Criteria:**

*   Correctness: The solution must correctly implement ACID properties and handle conflicts appropriately.
*   Efficiency: The solution must be efficient in terms of time and space complexity.
*   Scalability: The solution should be able to handle a large number of concurrent transactions.
*   Code Quality: The code should be well-structured, readable, and maintainable.
*   Error Handling: The solution should handle errors gracefully and provide informative error messages.
