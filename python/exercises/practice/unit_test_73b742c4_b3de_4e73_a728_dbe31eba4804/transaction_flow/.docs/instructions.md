## Problem: Distributed Transaction Orchestrator

You are tasked with designing and implementing a distributed transaction orchestrator. This orchestrator will manage transactions that span multiple independent services. Each service exposes a simple API for performing and rolling back operations.

**Scenario:**

Imagine an e-commerce platform where placing an order involves several steps:

1.  Reserving inventory in the `InventoryService`.
2.  Charging the customer's credit card via the `PaymentService`.
3.  Creating the order record in the `OrderService`.
4.  Notifying the shipping department via the `ShippingService`.

Each of these services is independent and has its own database. To ensure data consistency, these operations must be performed within a single distributed transaction. If any step fails, all previous steps must be rolled back.

**Input:**

You will receive a list of service operations to execute as part of a transaction. Each operation is represented as a tuple: `(service_name, action, data)`.

*   `service_name`: A string identifying the service (e.g., "InventoryService").
*   `action`: A string representing the action to perform (e.g., "reserve_item", "charge").
*   `data`: A dictionary containing the data required for the operation.

**Service API Abstraction:**

Assume you have access to a dictionary `services` where keys are `service_name` and values are objects representing the services. Each service object has two methods:

*   `perform(action, data)`: Executes the specified action with the given data.  Raises a `ServiceError` exception if the action fails. Returns a unique `transaction_id` for each succesful action.
*   `rollback(action, transaction_id)`: Rolls back the specified action, identified by the `transaction_id`.

**Requirements:**

1.  **Implement a function `orchestrate_transaction(operations, services)` that takes a list of `operations` and a dictionary of `services` as input.**
2.  **Atomicity:** Ensure that all operations either succeed or all are rolled back. If any `perform` operation fails, all previously executed operations must be rolled back in reverse order.
3.  **Idempotency:**  The `rollback` operation must be idempotent. It should be safe to call `rollback` multiple times for the same operation without causing unintended side effects. Each successful `rollback` operation should return a success status.
4.  **Concurrency:** The orchestrator will handle multiple concurrent transactions. You must ensure thread safety to prevent data corruption or race conditions. (Hint: Consider using appropriate locking mechanisms.)
5.  **Error Handling:** Implement robust error handling. Catch any exceptions raised by the services during `perform` or `rollback` and log them appropriately.  The `orchestrate_transaction` function should return `True` if the transaction succeeds completely (all performs succeed) or `False` if a rollback occurred (any perform fails, rollback succeeds).
6.  **Optimization:** The orchestrator should be designed for optimal performance. Minimize the time it takes to complete a transaction, especially under high load.  Consider techniques for batching operations or performing rollbacks in parallel.
7.  **Resilience:** Consider how the orchestrator can handle service failures.  If a service is temporarily unavailable, the orchestrator should retry the operation after a delay (with exponential backoff) before giving up and initiating a rollback. Limit the retries to 3 times.

**Constraints:**

*   You must use Python 3.7 or higher.
*   You can use standard Python libraries and the `threading` module for concurrency. No other external libraries are allowed.
*   Each service is independent and may have its own failure modes.
*   The number of services and operations in a transaction can vary.
*   The data associated with each operation can be arbitrarily complex.
*   Each service may take arbitrary time to complete, including failing completely.

**ServiceError Exception:**

Define a custom exception class `ServiceError` that inherits from `Exception`. This exception should be raised by the services when a `perform` or `rollback` operation fails.

**Example:**

```python
class ServiceError(Exception):
    pass

def orchestrate_transaction(operations, services):
    # Your implementation here
    pass
```

This problem requires a deep understanding of distributed systems, concurrency, error handling, and optimization techniques. It challenges the solver to design a robust and efficient distributed transaction orchestrator that can handle a variety of failure scenarios and concurrency issues.
