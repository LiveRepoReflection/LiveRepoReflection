## Problem: Distributed Transaction Coordinator

**Description:**

You are tasked with building a simplified, in-memory distributed transaction coordinator for a microservices architecture. Imagine a scenario where multiple services need to atomically update their local data based on a single, coordinated transaction.

**The System:**

*   You have `N` microservices, each represented by a unique integer ID from `0` to `N-1`.
*   Each microservice maintains its own local state (a simple integer value).
*   A transaction involves all `N` microservices.
*   The coordinator receives transaction requests, orchestrates the transaction across all services, and ensures atomicity (all services commit or all services rollback).

**The Transaction Flow:**

1.  **Initiation:** The coordinator receives a transaction request. This request includes a slice of `N` integers. The `i`-th integer represents the proposed *delta* (change) to be applied to the local state of microservice `i`.
2.  **Prepare Phase:** The coordinator sends a "prepare" message to each microservice, along with its proposed delta.  Each microservice checks if applying the delta would violate its internal constraints (see below). If a microservice *can* apply the delta without violation, it tentatively applies the delta *locally* and responds with `true` ("vote to commit") to the coordinator. If a microservice *cannot* apply the delta, it rejects the transaction and responds with `false` ("vote to abort").
3.  **Commit/Rollback Phase:**
    *   If *all* microservices voted to commit, the coordinator sends a "commit" message to each microservice. Each microservice then *permanently* applies the delta.
    *   If *any* microservice voted to abort, the coordinator sends a "rollback" message to each microservice. Each microservice reverts its tentatively applied delta, restoring its original state.

**Constraints:**

*   **Atomicity:**  All microservices must either commit the transaction or rollback, even in the face of simulated network issues (see error handling below).
*   **Isolation:**  While a transaction is in progress (prepare phase), no other transaction should be allowed to modify the local state of *any* microservice. You must ensure proper synchronization to prevent race conditions.
*   **Microservice Constraints:**  Each microservice has a lower bound (`minValue`) and an upper bound (`maxValue`) for its local state.  A microservice *cannot* commit a delta that would cause its state to fall below `minValue` or exceed `maxValue`.
*   **Concurrency:** The coordinator can receive multiple transaction requests concurrently. You must handle concurrent transactions efficiently and safely.
*   **Error Handling:**  Simulate unreliable network connections.  Introduce a configurable probability that a message (prepare, commit, rollback) will be "lost" (dropped). The coordinator and microservices must implement timeouts and retry mechanisms to handle lost messages and guarantee atomicity.

**Implementation Requirements:**

1.  Implement the `Coordinator` and `Microservice` structs.
2.  Implement the necessary methods for transaction coordination: `InitiateTransaction`, `Prepare`, `Commit`, `Rollback`.
3.  Implement timeout and retry mechanisms for message delivery.
4.  Implement proper synchronization to ensure atomicity and isolation under concurrency.
5.  Ensure that microservice constraints are always respected.
6.  Provide a function to set the "message loss probability" to simulate unreliable networks.

**Input:**

*   `N`: The number of microservices.
*   `minValue`, `maxValue`: The lower and upper bounds for the local state of each microservice. All microservices share the same bounds for simplicity.
*   A sequence of transaction requests. Each request is a slice of `N` integers representing the deltas for each microservice.
*   `messageLossProbability`: A float between 0 and 1 representing the probability that a message will be lost.

**Output:**

The final local state of each microservice after processing all transaction requests.
