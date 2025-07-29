## The Distributed Transaction Coordinator

**Problem Description:**

You are tasked with building a simplified, yet robust, distributed transaction coordinator (DTC) for a microservices architecture. This DTC is responsible for ensuring atomicity across multiple services during a single logical transaction. Atomicity, in this context, means that either all participating services successfully commit their changes, or all of them roll back, even in the face of failures.

The system consists of a central DTC and multiple participating services.  Each service exposes two endpoints: `prepare` and `commit/rollback`.

*   `prepare`: When called, the service attempts to perform its part of the transaction and, if successful, "prepares" the changes. It must then respond to the DTC with either an "ACK" (acknowledgement) or a "NACK" (negative acknowledgement). The service must guarantee that after sending an ACK, it *can* commit the transaction if instructed to do so, even if it crashes and restarts. This typically involves writing the prepared changes to stable storage (e.g., disk).

*   `commit/rollback`: The DTC will subsequently call either the `commit` or `rollback` endpoint of each service.  Upon receiving `commit`, the service finalizes the prepared changes.  Upon receiving `rollback`, the service discards the prepared changes and reverts to its original state.

**Your Task:**

Implement the DTC in Rust. The DTC must:

1.  **Initiate Transactions:** Accept a list of participating service URLs (e.g., `["http://service1/prepare", "http://service2/prepare", ...]`).
2.  **Two-Phase Commit (2PC) Protocol:**
    *   In the *prepare phase*, the DTC sends a `prepare` request to each service.
    *   The DTC waits for a response (ACK or NACK) from each service, with a configurable timeout.
    *   If *all* services respond with ACK within the timeout, the DTC enters the *commit phase* and sends a `commit` request to each service.
    *   If *any* service responds with NACK or doesn't respond within the timeout, the DTC enters the *rollback phase* and sends a `rollback` request to each service.
3.  **Logging:**  Maintain a persistent log of all transaction states, including the service URLs involved, the prepare phase responses (ACK/NACK), and the final decision (commit/rollback).  This log is crucial for recovery after a DTC crash.
4.  **Recovery:** Upon restart, the DTC must read the log and resume any incomplete transactions. If a transaction was in the prepare phase, the DTC must re-query the services to determine their state. If any service is unreachable or reports an inconsistent state, the DTC must attempt to rollback the transaction.
5.  **Concurrency:**  The DTC must handle multiple concurrent transaction requests.
6.  **Idempotency:** The `commit` and `rollback` operations on the services should be idempotent. Services might receive commit or rollback requests multiple times.

**Constraints and Requirements:**

*   **Error Handling:** Implement robust error handling for network failures, service unavailability, and inconsistent states.
*   **Timeout Configuration:**  The timeout for the prepare phase must be configurable.
*   **Concurrency:** The DTC must handle concurrent transaction requests efficiently. Use appropriate concurrency mechanisms (e.g., `tokio`, `async/await`, `rayon`).
*   **Durability:** The transaction log must be durable.  Use a suitable storage mechanism (e.g., a file, a database). Consider using append-only writes to the log for performance.
*   **Performance:**  Optimize for throughput and latency. Consider using asynchronous I/O and efficient data structures.
*   **Service Interaction:** Assume the services expose HTTP endpoints for `prepare`, `commit`, and `rollback`. Use a suitable HTTP client library (e.g., `reqwest`).
*   **Idempotency:** Commit and rollback operations on services must be idempotent.
*   **Logging Format:** The logging format needs to be easily parsable for recovery. Consider using a structured format like JSON or Protocol Buffers.
*   **Resource Management:** Ensure proper resource management to avoid memory leaks or excessive resource consumption.

**Bonus Challenges:**

*   **Optimistic Concurrency Control:** Implement a mechanism to detect and handle conflicting transactions.
*   **Scalability:** Design the DTC to be horizontally scalable.
*   **Monitoring:** Add basic monitoring capabilities (e.g., transaction rate, error rate).
*   **Deadlock Detection/Prevention:**  Consider scenarios where services might become deadlocked waiting for each other and implement a mechanism to handle this.

This problem requires a deep understanding of distributed systems concepts, concurrency, error handling, and performance optimization. The various constraints and the need for recovery make this a challenging and sophisticated task. Good luck!
