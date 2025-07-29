## Problem: Distributed Transaction Orchestrator

### Question Description

You are tasked with designing and implementing a simplified distributed transaction orchestrator.  Imagine a microservices architecture where multiple services need to participate in a single logical transaction.  If any service fails to commit its part of the transaction, the entire transaction must be rolled back.

Your orchestrator will receive requests to execute distributed transactions. Each transaction involves a series of operations across different services. Each service operation is idempotent and has a corresponding compensation operation (rollback).

**Input:**

The orchestrator receives a list of transactions. Each transaction is described as a list of operations. Each operation contains:

*   `service_id`: A unique identifier for the service involved (e.g., "inventory", "payment", "shipping").
*   `operation_data`: A string representing the data needed to perform the operation (e.g., "item_id:123,quantity:2").
*   `compensation_data`: A string representing the data needed to perform the compensation operation (rollback) for the corresponding operation.

**Constraints:**

*   **Idempotency:**  Each service operation and its compensation operation are guaranteed to be idempotent. This means that executing them multiple times with the same input has the same effect as executing them once.
*   **Atomicity:** The entire transaction must be atomic. Either all operations succeed, or all operations are rolled back.
*   **Concurrency:**  The orchestrator must handle multiple transactions concurrently.
*   **Service Communication:**  The orchestrator communicates with services using a simple synchronous `execute(service_id, operation_data)` and `compensate(service_id, compensation_data)` interface. You can assume these methods exist and are reliable (no network errors). They return a boolean indicating success or failure.
*   **Resource Limits:** The orchestrator has limited memory. You cannot store the entire history of all transactions. Specifically, you can only store the *current* state of transactions being processed.  You are allowed to use external persistent storage (e.g., a database) only for durable transaction logs and metadata, but access to it should be minimized due to performance concerns.
*   **Deadlock Prevention:**  The order in which services are involved in transactions is not guaranteed to be consistent. Your orchestrator must prevent deadlocks.
*   **Performance:** The orchestrator should strive to minimize the overall execution time of transactions.
*   **Scalability:** The number of services and concurrent transactions can be high.

**Output:**

For each transaction, the orchestrator should return `true` if the transaction committed successfully, and `false` if the transaction was rolled back.

**Example:**

```
Transaction 1:
  - service_id: "inventory", operation_data: "item_id:123,quantity:2", compensation_data: "item_id:123,quantity:2"
  - service_id: "payment", operation_data: "amount:20", compensation_data: "amount:20"
  - service_id: "shipping", operation_data: "address:..." , compensation_data: "address:..."

Transaction 2:
  - service_id: "inventory", operation_data: "item_id:456,quantity:1", compensation_data: "item_id:456,quantity:1"
  - service_id: "shipping", operation_data: "address:...", compensation_data: "address:..."
  - service_id: "payment", operation_data: "amount:10", compensation_data: "amount:10"
```

**Requirements:**

1.  Implement the core logic of the distributed transaction orchestrator.
2.  Demonstrate deadlock prevention.
3.  Address concurrency and resource constraints.
4.  Optimize for performance, considering the need to minimize external storage access.
5.  Consider different transaction execution strategies (e.g., sequential vs. parallel execution of operations within a transaction) and justify your choice. Discuss the trade-offs.
6.  Clearly document your design choices and the rationale behind them.

This problem requires careful consideration of various aspects of distributed system design, including concurrency control, fault tolerance, and performance optimization. It's expected that a successful solution would involve a sophisticated understanding of these concepts and the ability to apply them in a practical context. Good luck!
