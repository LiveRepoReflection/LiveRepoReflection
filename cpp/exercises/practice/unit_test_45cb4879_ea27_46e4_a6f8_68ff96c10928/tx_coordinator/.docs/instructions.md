## Question: Distributed Transaction Coordinator

### Question Description

You are tasked with designing and implementing a simplified distributed transaction coordinator (DTC) for a microservices architecture.  Imagine a system where multiple independent services need to participate in a single, atomic transaction.  If any service fails to complete its part of the transaction, the entire transaction must be rolled back across all participating services.

Each service exposes an API with two endpoints: `Prepare` and `Commit/Rollback`.

*   `Prepare`:  The DTC calls this endpoint on each service to ask if it is ready to commit its part of the transaction. The service performs any necessary checks (e.g., resource availability, data validation) and returns `true` if it's ready or `false` if it cannot commit. The service must also *tentatively* reserve any resources it needs to complete its part of the transaction. This tentative reservation is crucial for ensuring atomicity, but must not block other unrelated operations.

*   `Commit/Rollback`: If all services return `true` in the `Prepare` phase, the DTC calls `Commit` on each service.  If any service returns `false` in the `Prepare` phase, the DTC calls `Rollback` on each service.  `Commit` finalizes the transaction within the service, while `Rollback` releases any reserved resources and reverts any tentative changes made during the `Prepare` phase.  Both `Commit` and `Rollback` are guaranteed to eventually succeed, even with retries.

Your task is to implement the `TransactionCoordinator` class with the following methods:

*   `bool BeginTransaction(vector<Service*> services)`:  Initiates a new distributed transaction involving the given list of `Service` objects.  It should return `true` if the transaction was successfully committed and `false` if it was rolled back.
*   `void RegisterService(Service* service)`: Registers a new service with the transaction coordinator.
*   `void UnregisterService(Service* service)`: Unregisters a service. This might be necessary if a service is temporarily unavailable.

**Constraints and Considerations:**

*   **Atomicity:** All services must either commit or rollback as a single unit.
*   **Durability:** Once a transaction is committed, the changes must be permanent, even if the DTC crashes. (Simulate durability with in-memory data structures -- no actual disk writes required for this problem).
*   **Isolation:**  The `Prepare` phase should not block other unrelated operations in the services. Tentative resource reservations should be as non-intrusive as possible.
*   **Concurrency:** Multiple transactions can be initiated concurrently. The DTC must handle concurrent transactions correctly.
*   **Idempotency:** The `Commit` and `Rollback` operations in each service must be idempotent.  The DTC might retry these operations multiple times if failures occur.
*   **Error Handling:** The DTC must handle service failures gracefully.  If a service becomes unavailable during the `Prepare` or `Commit/Rollback` phases, the DTC should retry the operation until it succeeds or a timeout occurs (you need to implement timeout mechanism).  If the timeout is reached the coordinator should rollback all other services.
*   **Optimization:**  Minimize the time it takes to complete a transaction.  Consider how you can parallelize operations.
*   **Deadlock Prevention:** Your implementation should avoid deadlocks.  Consider the order in which you acquire resources or the use of timeouts.
*   **Scalability:** While you don't need to implement distributed communication between DTCs, consider how your design would scale if you had multiple DTCs managing transactions across a large number of services.
*   **Service Implementation**: You are **not** responsible for implementing the individual `Service` classes. Assume these exist and provide the `Prepare`, `Commit`, and `Rollback` methods.  The focus is on the DTC logic.  Service are registered with the DTC using `RegisterService` and can be unregistered using `UnregisterService`.

**Assumptions:**

*   The `Service` class has the following methods:

    *   `bool Prepare()`: Returns `true` if the service is ready to commit, `false` otherwise.
    *   `bool Commit()`: Commits the transaction. Returns `true` on success, `false` on failure.
    *   `bool Rollback()`: Rolls back the transaction. Returns `true` on success, `false` on failure.
    *   `int GetId()`: Returns a unique integer ID of the service.

*   You can use standard C++ libraries and data structures.

**Example:**

```cpp
class Service {
public:
    virtual bool Prepare() = 0;
    virtual bool Commit() = 0;
    virtual bool Rollback() = 0;
    virtual int GetId() = 0;
};

class TransactionCoordinator {
public:
    bool BeginTransaction(vector<Service*> services);
    void RegisterService(Service* service);
    void UnregisterService(Service* service);
};
```

**Scoring:**

*   Correctness (passing all test cases): 70%
*   Efficiency (transaction completion time): 20%
*   Code quality and design: 10%

This problem requires a strong understanding of distributed systems concepts, concurrency, error handling, and optimization techniques. Good luck!
