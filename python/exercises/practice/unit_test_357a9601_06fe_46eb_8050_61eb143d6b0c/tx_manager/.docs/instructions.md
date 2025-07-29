## Project Name

```
distributed-transaction-manager
```

## Question Description

You are tasked with building a simplified, distributed transaction manager for a microservices architecture. Imagine a system where multiple independent services (databases, message queues, etc.) need to participate in a single, atomic transaction. If any part of the transaction fails, the entire transaction must be rolled back across all services.

**System Overview:**

*   **Services:** A variable number of independent services exist. Each service can perform a local operation (e.g., update a database record, publish a message). Each service is identified by a unique `service_id`.
*   **Transaction Manager:** Your code will implement the core logic of the transaction manager. It receives transaction requests, coordinates with services, and ensures atomicity.
*   **Transaction Protocol:** Use a simplified Two-Phase Commit (2PC) protocol:
    1.  **Prepare Phase:** The transaction manager sends a `PREPARE` message to all participating services. Each service attempts to perform its local operation and responds with either `ACK` (operation successful, service is prepared to commit) or `NACK` (operation failed, service cannot commit).
    2.  **Commit/Rollback Phase:**
        *   If all services respond with `ACK`, the transaction manager sends a `COMMIT` message to all services. Services then permanently apply their changes.
        *   If any service responds with `NACK`, the transaction manager sends a `ROLLBACK` message to all services. Services then undo any changes made during the prepare phase.
*   **Communication:** Assume a reliable message passing mechanism between the transaction manager and the services. You don't need to implement the actual network communication, but you'll interact with a mock service interface.
*   **Concurrency:** Multiple transactions can be initiated concurrently. Your transaction manager must handle concurrent transactions correctly.
*   **Failure Handling:** Services can fail or become temporarily unavailable during the prepare or commit/rollback phases. The transaction manager must handle these failures gracefully and attempt to recover the transaction. Assume that services will eventually recover (no permanent failures).
*   **Idempotency:** Service operations (both commit and rollback) must be idempotent. This means that if a service receives the same commit or rollback message multiple times, it should only perform the operation once.

**Your Task:**

Implement the `TransactionManager` class with the following methods:

*   `__init__(self, service_interface, retry_count, retry_interval)`: Initializes the transaction manager.
    *   `service_interface`: An object that provides a mock interface to interact with the services (described below).
    *   `retry_count`: The number of times to retry a failed operation (PREPARE, COMMIT, ROLLBACK) before giving up.
    *   `retry_interval`: The interval (in seconds) between retries.
*   `begin_transaction(self, transaction_id, participating_services)`: Starts a new transaction.
    *   `transaction_id`: A unique identifier for the transaction.
    *   `participating_services`: A list of `service_id`s that are part of this transaction.
    *   The method should return `True` if the transaction commits successfully, and `False` if it rolls back (or fails after retries).
*   `abort_transaction(self, transaction_id)`: Aborts an ongoing transaction. This function is called externally and should immediately ROLLBACK the transaction.

**Service Interface:**

You will be provided with a `ServiceInterface` class that mimics the interaction with the real services. It has the following methods:

*   `prepare(self, service_id, transaction_id)`: Sends a `PREPARE` message to the service. Returns `True` for `ACK` and `False` for `NACK`. Can raise a `ServiceUnavailableException` if the service is temporarily unavailable.
*   `commit(self, service_id, transaction_id)`: Sends a `COMMIT` message to the service. Returns `True` on success. Can raise a `ServiceUnavailableException`.
*   `rollback(self, service_id, transaction_id)`: Sends a `ROLLBACK` message to the service. Returns `True` on success. Can raise a `ServiceUnavailableException`.

**Constraints:**

*   The transaction manager must ensure atomicity: either all participating services commit, or all rollback.
*   The transaction manager must handle service failures and retries.
*   The transaction manager must handle concurrent transactions correctly.
*   The solution must be thread-safe.
*   Optimize for performance and resource utilization, especially when dealing with a large number of services and concurrent transactions.
*   Assume that `transaction_id` and `service_id` are strings.

**Error Handling:**

*   You can define custom exception classes if needed.
*   Log errors appropriately for debugging.

**Example Usage:**

```python
# Assuming ServiceInterface is already defined (see below)
service_interface = ServiceInterface()
tm = TransactionManager(service_interface, retry_count=3, retry_interval=1)

participating_services = ["service1", "service2", "service3"]
transaction_id = "tx123"

success = tm.begin_transaction(transaction_id, participating_services)

if success:
  print(f"Transaction {transaction_id} committed successfully.")
else:
  print(f"Transaction {transaction_id} rolled back.")

tm.abort_transaction("tx456") # Abort a transaction
```

**Note:** The ServiceInterface below is just an example for clarification; the precise implementation and behavior will be defined by the judge during evaluation. The primary focus of your solution should be the logic within the `TransactionManager` class. You should make suitable assumptions about the underlying `ServiceInterface` to make the problem tractable (e.g., it does not crash the calling thread), but you MUST adhere to its specified API.

```python
import time
import random

class ServiceUnavailableException(Exception):
    pass

class ServiceInterface:
    def __init__(self):
        self.prepared_services = set()
        self.committed_transactions = set()
        self.rolledback_transactions = set()
        self.availability = {}  # Simulate service availability

    def prepare(self, service_id, transaction_id):
        # Simulate potential service unavailability
        if service_id in self.availability and not self.availability[service_id]:
            raise ServiceUnavailableException(f"Service {service_id} is temporarily unavailable.")
        
        # Simulate random failure
        if random.random() < 0.1:
            return False # Simulate NACK
        self.prepared_services.add((service_id, transaction_id))
        return True # Simulate ACK


    def commit(self, service_id, transaction_id):
       if service_id in self.availability and not self.availability[service_id]:
            raise ServiceUnavailableException(f"Service {service_id} is temporarily unavailable.")
        
        self.committed_transactions.add((service_id, transaction_id))
        if (service_id, transaction_id) in self.rolledback_transactions:
            self.rolledback_transactions.remove((service_id, transaction_id))
        return True

    def rollback(self, service_id, transaction_id):
       if service_id in self.availability and not self.availability[service_id]:
            raise ServiceUnavailableException(f"Service {service_id} is temporarily unavailable.")
        
        self.rolledback_transactions.add((service_id, transaction_id))
        if (service_id, transaction_id) in self.committed_transactions:
            self.committed_transactions.remove((service_id, transaction_id))
        return True

class TransactionManager:
    def __init__(self, service_interface, retry_count, retry_interval):
        self.service_interface = service_interface
        self.retry_count = retry_count
        self.retry_interval = retry_interval
        # Add any required data structures here (e.g., to track ongoing transactions)
        # Consider using locks for thread safety

    def begin_transaction(self, transaction_id, participating_services):
        # Implement the 2PC protocol here
        # Handle retries and service failures
        pass

    def abort_transaction(self, transaction_id):
       # Implement the abort transaction logic here
        pass
```
