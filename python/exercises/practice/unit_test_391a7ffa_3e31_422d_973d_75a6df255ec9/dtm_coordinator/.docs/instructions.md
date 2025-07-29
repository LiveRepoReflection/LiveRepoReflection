## Problem: Distributed Transaction Manager

**Description:**

You are tasked with designing a simplified Distributed Transaction Manager (DTM) for a microservices architecture. This DTM will coordinate transactions spanning multiple services, ensuring atomicity, consistency, isolation, and durability (ACID) properties. Due to network limitations and the scale of the system, eventual consistency is acceptable, but the system must guarantee that transactions *eventually* either fully commit or fully rollback.

The system consists of `n` services, each identified by a unique integer ID from `0` to `n-1`. Each service can perform local operations. A global transaction might involve operations on a subset of these services.

**The Challenge:**

Implement a `TransactionCoordinator` class with the following methods:

*   `__init__(self, num_services)`: Initializes the DTM with the total number of services. Assume service IDs are 0-indexed.

*   `begin_transaction(self, transaction_id, involved_services)`: Starts a new transaction with a unique `transaction_id` (an integer). The `involved_services` is a set of service IDs (integers) that will participate in this transaction.

*   `prepare(self, transaction_id, service_id)`: Simulates a service preparing to commit its part of the transaction.  This method should record that the specified service has prepared for the given transaction. A service can only prepare once for a transaction.  If a service is not part of the transaction or the transaction does not exist, return `False`. Otherwise, return `True`.

*   `commit_transaction(self, transaction_id)`: Attempts to commit the transaction. A transaction can only commit if *all* involved services have successfully prepared. If all services have prepared, the transaction is considered committed. You do **not** need to actually perform any "commit" action on the services themselves.  Instead, this function should simply return `True` if the transaction successfully committed and `False` otherwise. This function can only be called once per `transaction_id`.

*   `rollback_transaction(self, transaction_id)`: Rolls back the transaction. You do **not** need to actually perform any "rollback" action on the services themselves. This function should ensure that no future `commit_transaction` call for the same `transaction_id` can succeed, even if all services subsequently call `prepare`. This function can only be called once per `transaction_id`.

*   `get_transaction_status(self, transaction_id)`: Returns the status of the transaction. Return values are:
    *   `"PENDING"`: The transaction is active, and not all services have prepared.
    *   `"PREPARED"`: All involved services have prepared, but the transaction has not been committed or rolled back.
    *   `"COMMITTED"`: The transaction has been successfully committed.
    *   `"ROLLED_BACK"`: The transaction has been rolled back.
    *   `"NOT_FOUND"`: The transaction does not exist.

**Constraints and Considerations:**

*   **Concurrency:**  Assume that these methods can be called concurrently from different threads.  Your implementation must be thread-safe.
*   **Scalability:** The number of services (`n`) and the number of concurrent transactions can be large (up to 10^5). Optimize your data structures and algorithms accordingly.
*   **Durability:**  The DTM's state (transactions, prepared services, commit/rollback status) should be considered volatile (in-memory only). You do not need to handle persistent storage or recovery from crashes.
*   **Idempotency:** The `prepare`, `commit_transaction`, and `rollback_transaction` operations do *not* need to be idempotent. Subsequent calls to the same function with the same arguments after a successful execution can have unexpected results, unless explicitly specified in the function description.
*   **Deadlock Prevention:** Your implementation should not create deadlocks.
*   **Error Handling:**  You only need to handle the error cases explicitly mentioned in the function descriptions.  You can assume inputs are otherwise valid.

This problem tests your ability to design and implement a concurrent system with specific consistency requirements, optimize for performance under potentially high load, and handle various transaction states. Good luck!
