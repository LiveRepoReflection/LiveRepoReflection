## Question: Distributed Transaction Coordinator

**Description:**

You are tasked with implementing a simplified distributed transaction coordinator for a microservices architecture. Imagine a system where multiple services need to perform operations atomically. For example, booking a flight might require reserving seats in the `FlightService`, reserving a hotel room in the `HotelService`, and charging the customer's credit card in the `PaymentService`.  If any of these operations fail, all others must be rolled back to maintain consistency.

Your coordinator will manage the lifecycle of distributed transactions across these services. The services expose simple `Prepare`, `Commit`, and `Rollback` endpoints.

**Specifics:**

1.  **Transaction ID Generation:** The coordinator must generate unique transaction IDs for each transaction.
2.  **Transaction Initiation:**  The coordinator receives a request containing a list of service endpoints (URLs) that need to participate in the transaction, and a timeout value.
3.  **Two-Phase Commit (2PC) Protocol:**
    *   **Prepare Phase:** The coordinator sends a `Prepare` request to each participating service. Each service attempts to perform its operation tentatively. If successful, it responds with an `ACK`. If it fails, it responds with a `NACK` and a reason for the failure.  Services must hold all the resources until `Commit` or `Rollback` commands.
    *   **Commit/Rollback Decision:**
        *   If all services respond with `ACK` within the given timeout, the coordinator sends a `Commit` request to all services.
        *   If any service responds with `NACK` or the timeout expires before receiving a response from all services, the coordinator sends a `Rollback` request to all services.
    *   **Commit/Rollback Phase:**  Services execute the `Commit` or `Rollback` operation as instructed by the coordinator and respond with an `ACK` or `NACK`.
4.  **Timeout Handling:** The coordinator must handle timeouts gracefully. If a service does not respond within the specified timeout, the coordinator must initiate a rollback.
5.  **Logging:** The coordinator must maintain a persistent log of all transactions, including their status (preparing, committing, rolling back, committed, rolled back, failed), the participating services, and any errors encountered.  This log should be append-only.
6.  **Recovery:** If the coordinator crashes and restarts, it must be able to recover its state from the log and complete any pending transactions (those that are still in the preparing, committing, or rolling back states). Assume a simple file-based log storage.
7. **Concurrency:** The coordinator must handle multiple concurrent transaction requests safely, without data races or deadlocks.

**Constraints:**

*   **Scalability:** While this is a simplified version, consider how your design could scale to handle a large number of concurrent transactions and services.  Focus on thread safety and efficient data structures.
*   **Durability:** The transaction log must be durable.  Data loss is unacceptable.
*   **Service Interactions:** You can simulate service interactions (Prepare, Commit, Rollback) with stub functions or a simple mock server. The focus is on the coordinator logic.
*   **Error Handling:** The coordinator must handle various error scenarios, such as network failures, service unavailability, and invalid responses from services.
*   **Performance:** Minimize latency. The coordinator's decision-making process should be as efficient as possible.
*   **Log size:** Minimize the size of transaction logs to ensure it doesn't grow to a huge amount.

**Input:**

The coordinator's API will receive a JSON payload with the following structure:

```json
{
  "services": ["http://service1/prepare", "http://service2/prepare", "http://service3/prepare"],
  "timeout": 1000 // Timeout in milliseconds
}
```

**Output:**

The coordinator should return a JSON payload indicating the final status of the transaction:

```json
{
  "transactionId": "unique-transaction-id",
  "status": "committed" or "rolled_back" or "failed",
  "errors": ["error message 1", "error message 2", ...] // Optional: list of errors encountered
}
```

**Bonus:**

*   Implement a mechanism to handle idempotent service operations (i.e., services can safely retry `Commit` or `Rollback` requests without causing unintended side effects).
*   Consider using a more robust logging mechanism than a simple file (e.g., a database).
*   Implement a monitoring system to track the performance and health of the coordinator.
