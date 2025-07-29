## Question: Distributed Transaction Orchestrator

**Problem Description:**

You are tasked with building a simplified distributed transaction orchestrator. Imagine a microservices architecture where multiple services need to participate in a single transaction. If any service fails, the entire transaction must be rolled back across all participants.

Your orchestrator will manage transactions across a set of *fictional* services.  Each service exposes two operations: `prepare` and `commit`.  The `prepare` operation attempts to tentatively reserve resources required for the transaction. The `commit` operation finalizes the transaction by permanently allocating resources.  A failed `prepare` indicates a service cannot participate in the transaction, and all previously prepared services must be rolled back (via a hypothetical `rollback` operation, which you'll simulate).

**Specifics:**

1.  **Services:** Assume you have a list of `n` services. Each service is represented by a unique identifier (a `String`).
2.  **Transaction ID:** Each transaction is identified by a unique ID (a `String`).
3.  **Prepare Phase:** The orchestrator first attempts to `prepare` each service in a given order. The `prepare` operation can either succeed or fail.
    *   **Success:** If a service successfully prepares, it remains in a "prepared" state.
    *   **Failure:** If a service fails to prepare, the orchestrator must:
        *   Rollback all services that have already successfully prepared (in reverse order of preparation). Assume that `rollback` operation always succeeds.
        *   Mark the entire transaction as failed.
4.  **Commit Phase:** If all services successfully prepare, the orchestrator then attempts to `commit` each service in the original preparation order.
    *   **Success:** The transaction completes successfully.
    *   **Failure:** If any service fails to commit, this represents a critical failure. In a *real* system, complex recovery mechanisms are needed. For this problem, simply log the failure and mark the transaction as failed. Do *not* attempt to rollback already committed services. (This simplifies the problem considerably, focusing on the preparation phase and overall orchestration).

**Input:**

*   `services`: A `Vec<String>` representing the list of participating services.
*   `transaction_id`: A `String` representing the unique ID of the transaction.
*   `prepare_order`: A `Vec<String>` representing the order in which services should be prepared. This must be a permutation of the `services` vector.
*   `prepare_successes`: A `HashMap<String, bool>` indicating whether the `prepare` operation will succeed for each service.  `true` means success, `false` means failure.
*   `commit_successes`: A `HashMap<String, bool>` indicating whether the `commit` operation will succeed for each service.  `true` means success, `false` means failure.

**Output:**

Return a `Result<(), String>` indicating the outcome of the transaction.

*   `Ok(())`: The transaction completed successfully (all services prepared and committed).
*   `Err(String)`: The transaction failed. The `String` should contain a descriptive error message, including the transaction ID and the service that caused the failure (either during prepare or commit).

**Constraints:**

*   The order of services in `prepare_order` must be a valid permutation of services in `services`.
*   The `prepare_successes` and `commit_successes` maps will contain entries for all services in the `services` vector.
*   Optimize for readability and maintainability. While efficiency is important, clear, well-structured code is preferred.
*   Error messages should be informative.

**Simulated Service Operations:**

You do **not** need to implement actual network calls to external services. Instead, *simulate* the `prepare`, `commit`, and `rollback` operations using the provided `prepare_successes` and `commit_successes` maps.  Simply log each simulated operation (prepare, commit, rollback) to the console including the service ID and transaction ID.

**Example:**

```rust
// Example Scenario:
let services = vec!["serviceA".to_string(), "serviceB".to_string(), "serviceC".to_string()];
let transaction_id = "tx123".to_string();
let prepare_order = vec!["serviceA".to_string(), "serviceB".to_string(), "serviceC".to_string()];
let prepare_successes = HashMap::from([
    ("serviceA".to_string(), true),
    ("serviceB".to_string(), false), // Service B fails to prepare
    ("serviceC".to_string(), true),
]);
let commit_successes = HashMap::from([
    ("serviceA".to_string(), true),
    ("serviceB".to_string(), true),
    ("serviceC".to_string(), true),
]);

// Expected behavior:
// 1. Service A prepares successfully. (Log: "Prepared serviceA for tx123")
// 2. Service B fails to prepare. (Log: "Prepare failed for serviceB for tx123")
// 3. Service A is rolled back. (Log: "Rolled back serviceA for tx123")
// 4. The function returns Err("Transaction tx123 failed: Prepare failed for serviceB")

```

This problem challenges you to orchestrate a complex, multi-step process with failure handling, demanding careful consideration of state management, error handling, and rollback procedures within the constraints of a distributed system simulation. Good luck!
