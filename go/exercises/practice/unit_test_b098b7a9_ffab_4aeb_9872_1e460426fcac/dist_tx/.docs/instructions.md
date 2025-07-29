## Problem: Distributed Transaction Manager

**Description:**

You are tasked with building a simplified, in-memory Distributed Transaction Manager (DTM).  This DTM is responsible for coordinating transactions across multiple independent services.  Each service can perform operations, and a transaction ensures that either all operations across all services succeed (commit) or all operations are rolled back (abort).

**Core Concepts:**

*   **Transaction ID (TXID):** A unique identifier for each transaction.
*   **Services:** Independent components that can perform operations. Represented by their unique string ID.
*   **Operations:**  A unit of work performed by a service. Each operation is represented by a function, which takes the system's internal state as input and modifies it.
*   **Two-Phase Commit (2PC):** The protocol used to ensure atomicity.

**Specific Requirements:**

1.  **Transaction Registration:**
    *   Implement a function to start a new transaction, assigning it a unique TXID and recording the participating services.
    *   The DTM must ensure that each service can only participate in one active transaction at any given time. Attempting to register a service in a new transaction when it's already in another active transaction should raise an error.

2.  **Operation Submission:**
    *   Implement a function for services to submit operations to the DTM under a specific TXID.
    *   The operation should be a function that takes the *current global state* as an argument and returns a *modified copy of the global state*.
    *   The DTM should store these operations, associated with their TXID and service ID.

3.  **Two-Phase Commit (2PC) Implementation:**
    *   **Phase 1 (Prepare):**
        *   When a transaction is ready to commit, the DTM initiates the prepare phase.
        *   The DTM *sequentially* executes each service's operations in the order they were submitted.
        *   If an operation fails, the entire transaction is aborted. Implement a mechanism for operations to signal failure (e.g., by returning an error or panicking).
        *   If all operations succeed, the DTM marks the transaction as "prepared".
    *   **Phase 2 (Commit/Abort):**
        *   If the transaction is "prepared", the DTM commits the transaction, making the prepared state the new global state.
        *   If any operation failed during the prepare phase, or if any other issue arises, the DTM aborts the transaction, discarding the prepared state.

4.  **Concurrency:**
    *   The DTM should be able to handle multiple concurrent transactions. You will need to use appropriate synchronization mechanisms (e.g., mutexes, channels) to ensure data consistency and prevent race conditions.

5.  **Rollback:**
    *   Although the operations are expected to be idempotent, implement a rollback mechanism. In case of failure during the prepare phase, all the changes from the successfully executed operations should be reverted. If the operation functions are not reversible, maintain a shadow state to allow the system to return to the previous state.
    *   This mechanism should be robust and efficient.

6.  **Error Handling:**
    *   Implement comprehensive error handling.  The DTM should return meaningful errors to the caller in case of failures (e.g., service already in transaction, invalid TXID, operation failure).

7.  **Global State:**
    *   The global state is a `map[string]interface{}` that stores the system's data.

**Constraints:**

*   Assume that the network is reliable and that services will always respond.
*   Services are stateless; all data is managed by the DTM's global state.
*   The order of operation execution within a service must be preserved. Operations from different services can be executed in any order.
*   The global state should be protected using mutexes to avoid race conditions.

**Input:**

*   Functions to register transactions, submit operations, and initiate the commit/abort process.
*   A global state that is a `map[string]interface{}`.
*   A list of services that can participate in transactions.

**Output:**

*   The DTM should either successfully commit the transaction, updating the global state, or abort the transaction, leaving the global state unchanged.
*   The DTM should return appropriate error messages to indicate success or failure.

**Example:**

(Illustrative, not actual code)

```go
// registerTransaction(txID string, serviceIDs []string) error
// submitOperation(txID string, serviceID string, operation func(map[string]interface{}) (map[string]interface{}, error)) error
// commitTransaction(txID string) error
```

**Challenge:**

This problem requires a solid understanding of concurrency, distributed systems, and the Two-Phase Commit protocol.  Implementing the rollback mechanism efficiently and handling concurrency safely will be the most challenging aspects.  Consider using channels and mutexes appropriately to prevent race conditions and ensure data consistency. The design should be robust enough to handle multiple concurrent transactions and potential failures during the prepare phase.
