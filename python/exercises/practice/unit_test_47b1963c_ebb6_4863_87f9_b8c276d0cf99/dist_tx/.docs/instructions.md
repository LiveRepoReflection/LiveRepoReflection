## The Distributed Transaction Coordinator

### Question Description

You are tasked with designing and implementing a simplified distributed transaction coordinator (DTC). In a distributed system, ensuring atomicity (all or nothing) across multiple services is crucial. Your DTC will manage transactions spanning several independent services.

Specifically, you are given a set of microservices and a series of transactions that need to be executed. Each transaction involves calls to a subset of these microservices. Each microservice exposes two key functions for transaction management: `prepare(transaction_id, data)` and `commit(transaction_id)`.  `prepare` attempts to tentatively apply the changes associated with the transaction. If all participating microservices successfully prepare, the DTC then instructs them to `commit`, making the changes permanent. If any microservice fails during the prepare phase, the DTC aborts the transaction, signaling all services involved.

The challenge lies in handling failures, optimizing resource usage, and ensuring ACID (Atomicity, Consistency, Isolation, Durability) properties, given the following constraints:

**Microservice Constraints:**

*   Each microservice has a limited number of concurrent transactions it can handle (defined individually for each service). If this limit is reached, the `prepare` call should immediately return failure.
*   Microservices can fail during the `prepare` or `commit` phase. Failures are represented by exceptions.
*   Microservices are independent of each other, and the DTC has no direct access to their internal state.

**DTC Constraints:**

*   The DTC must handle transactions concurrently, maximizing throughput.
*   The DTC must recover gracefully from its own failures. You don't need to implement full persistence, but consider how you would design for it.
*   The DTC needs to make sure the number of calls to microservices are efficient and only necessary calls are made.

**Input:**

*   A list of microservices, each with its own `prepare` and `commit` functions and a maximum concurrency limit. Each microservice is represented as a dictionary: `{'name': str, 'prepare': function, 'commit': function, 'max_concurrency': int}`. The `prepare` function receives the `transaction_id` and `data` as input, and returns a boolean indicating success or failure. The `commit` function receives the `transaction_id` as input.
*   A list of transactions. Each transaction is a dictionary: `{'id': str, 'involved_services': list[str], 'data': dict}`. The `involved_services` list contains the names of the microservices participating in the transaction.

**Output:**

*   A list of transaction statuses, where each status is a dictionary: `{'id': str, 'status': str}`. The `status` can be either "COMMITTED" or "ABORTED".

**Requirements:**

1.  **Atomicity:** Ensure that a transaction is either fully committed across all participating services or fully aborted.
2.  **Concurrency:** Process transactions concurrently to improve throughput.
3.  **Failure Handling:** Handle microservice failures during `prepare` and `commit` phases gracefully. If a microservice fails to prepare, abort the transaction. If a microservice fails to commit, retry a reasonable number of times (e.g., 3). If it still fails, log the error and proceed with committing the other services (partial failure is acceptable in the commit phase if retries are exhausted).
4.  **Resource Management:** Respect the concurrency limits of each microservice. Prevent overloading any single microservice.
5.  **Efficiency:** The DTC should not introduce excessive overhead. Minimize the number of calls to microservices where possible.
6.  **Scalability:** Consider the design implications for scaling the DTC horizontally.

**Example:**

```python
microservices = [
    {'name': 'ServiceA', 'prepare': lambda transaction_id, data: True, 'commit': lambda transaction_id: True, 'max_concurrency': 2},
    {'name': 'ServiceB', 'prepare': lambda transaction_id, data: True, 'commit': lambda transaction_id: True, 'max_concurrency': 1},
]

transactions = [
    {'id': 'TX1', 'involved_services': ['ServiceA', 'ServiceB'], 'data': {'amount': 100}},
    {'id': 'TX2', 'involved_services': ['ServiceA'], 'data': {'item': 'Widget'}},
]

# Expected Output (order may vary):
# [
#     {'id': 'TX1', 'status': 'COMMITTED'},
#     {'id': 'TX2', 'status': 'COMMITTED'},
# ]
```

**Note:** You don't need to implement the actual microservices. You can simulate their behavior using simple functions. The focus is on the DTC's logic.
