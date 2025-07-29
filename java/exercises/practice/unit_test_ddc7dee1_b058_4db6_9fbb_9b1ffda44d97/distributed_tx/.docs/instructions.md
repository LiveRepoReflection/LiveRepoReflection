## The Distributed Transaction Coordinator

**Problem Description:**

You are tasked with designing and implementing a simplified Distributed Transaction Coordinator (DTC) for a microservices architecture. Imagine a scenario where multiple independent services need to participate in a single, atomic transaction. If any of these services fail to complete their part of the transaction, the entire transaction must be rolled back to maintain data consistency.

Your DTC should orchestrate two-phase commit (2PC) transactions across multiple services. Each service exposes a simple API with two key methods: `prepare()` and `commit()`. The DTC is responsible for initiating the transaction, coordinating the `prepare()` and `commit()` phases, and handling potential failures.

**Specific Requirements:**

1.  **Service Interaction:** You are given a list of `Service` objects. Each `Service` object has `prepare()` and `commit()` methods. The `prepare()` method simulates preparing the service for the transaction and returns `true` if successful, `false` otherwise. The `commit()` method simulates committing the changes and returns `true` if successful, `false` otherwise. Both methods can throw exceptions simulating service failures.

    ```java
    interface Service {
        boolean prepare() throws Exception;
        boolean commit() throws Exception;
    }
    ```

2.  **Transaction Initiation:** The DTC should have a `transact(List<Service> services)` method that initiates and manages the distributed transaction.

3.  **Two-Phase Commit:** Implement the 2PC protocol:

    *   **Phase 1 (Prepare Phase):** The DTC sends a `prepare()` request to each service. If all services successfully prepare (return `true` without throwing an exception), the transaction can proceed to the commit phase. If any service fails to prepare (returns `false` or throws an exception), the transaction must be aborted.

    *   **Phase 2 (Commit Phase):** If all services successfully prepared, the DTC sends a `commit()` request to each service. If all services successfully commit (return `true` without throwing an exception), the transaction is considered successful. If any service fails to commit (returns `false` or throws an exception), the DTC must attempt to compensate by re-trying the commit operation (with a limited number of retries) or logging the failure for manual intervention.

4.  **Rollback (Implicit):** There is no explicit "rollback" method. If any service fails during the prepare phase, the services that successfully prepared do NOT need to be explicitly rolled back. The problem states that each service implements a rollback mechanism within the prepare phase itself to rollback any tentative changes made if the prepare call results in a false result.

5.  **Failure Handling:**

    *   **Prepare Phase Failure:** If any service fails to prepare, the transaction must be aborted.
    *   **Commit Phase Failure:** If any service fails to commit, the DTC should retry the commit operation a maximum of `MAX_COMMIT_RETRIES` times (you define this constant). If the commit still fails after retries, log the failure and mark the transaction as partially committed.

6.  **Concurrency:** The `prepare()` and `commit()` calls to the services can potentially be time-consuming. Implement the DTC to execute these calls concurrently to improve performance. You can use Java's concurrency utilities (e.g., ExecutorService, Futures).

7.  **Logging:** Implement basic logging to track the progress of the transaction, including prepare and commit results for each service, and any failures encountered.

8.  **Idempotency:** Assume the `commit()` operation on each service is idempotent. This means that calling `commit()` multiple times has the same effect as calling it once.

**Constraints:**

*   The number of services participating in a transaction can be large (up to 1000).
*   Network latency between the DTC and the services can be significant.
*   Service failures are possible during both the prepare and commit phases.
*   The DTC should be designed to handle a high volume of transactions concurrently.
*   The solution must be thread-safe.
*   Minimize the overall execution time of the `transact()` method.

**Evaluation Criteria:**

*   Correctness: The DTC correctly implements the 2PC protocol and handles failures as specified.
*   Concurrency: The solution effectively utilizes concurrency to improve performance.
*   Failure Handling: The DTC handles service failures gracefully and retries commit operations as required.
*   Efficiency: The solution minimizes the overall execution time of the `transact()` method, especially with a large number of services.
*   Code Quality: The code is well-structured, readable, and maintainable.
*   Logging: The logging provides sufficient information to track the progress of transactions and diagnose failures.
