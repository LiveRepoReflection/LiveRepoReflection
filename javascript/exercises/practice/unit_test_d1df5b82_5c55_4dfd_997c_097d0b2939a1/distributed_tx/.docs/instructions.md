## Problem: Distributed Transaction Coordinator

### Question Description

You are tasked with building a simplified distributed transaction coordinator (DTC) in a microservices environment.  Imagine a system where multiple independent services need to perform operations that must be ACID (Atomicity, Consistency, Isolation, Durability). If one service's operation fails, all other services must roll back their changes to maintain data consistency.

Your DTC will manage transactions spanning multiple services, each exposing a simple `commit` and `rollback` endpoint.

**Core Requirements:**

1.  **Transaction ID Generation:**  The DTC should generate unique transaction IDs (UUIDs) for each new transaction.

2.  **Participant Registration:** Services participating in a transaction register with the DTC, providing their `commit` and `rollback` endpoint URLs.  The DTC stores these participants and their corresponding URLs for each transaction.  A service can register multiple times under different role names within the same transaction.

3.  **Two-Phase Commit (2PC):** Implement a 2PC protocol:
    *   **Phase 1 (Prepare):**  When a transaction needs to be committed, the DTC sends a "prepare" request to each registered service's `commit` endpoint (using HTTP).  The service attempts to perform its operation and responds with either:
        *   `200 OK`:  The service successfully prepared and is ready to commit.
        *   `409 Conflict`: The service *cannot* prepare and will need to rollback if other services commit. This can happen due to business logic constraints (e.g., insufficient funds, stock).
        *   `500 Internal Server Error`: A technical error occurred.
    *   **Phase 2 (Commit/Rollback):**
        *   If **all** services respond with `200 OK` in the prepare phase, the DTC sends a "commit" request to each service's `commit` endpoint.
        *   If **any** service responds with `409 Conflict` or `500 Internal Server Error` in the prepare phase, the DTC sends a "rollback" request to each service's `rollback` endpoint.

4.  **Idempotency:** The `commit` and `rollback` endpoints on each service *must* be idempotent.  The DTC might retry these requests in case of network issues or service unavailability.

5.  **Timeout Handling:** If a service does not respond to a "prepare", "commit", or "rollback" request within a configured timeout (e.g., 5 seconds), the DTC should consider the request failed. For prepare, a timeout is considered a `500 Internal Server Error`. For commit/rollback, the DTC retries a limited number of times (e.g., 3 retries) with exponential backoff before considering the transaction a failure.

6.  **Concurrent Transactions:**  The DTC must handle concurrent transactions correctly.

7.  **Logging/Auditing:** The DTC should log key events: transaction start, participant registration, prepare results, commit/rollback decisions, and any errors encountered.  This is crucial for debugging and auditing purposes.

**Constraints:**

*   You can use any HTTP client library for making requests to the services.
*   Assume the `commit` and `rollback` endpoints only accept `POST` requests.
*   Service URL registration can happen at any time before the commit is triggered.
*   Focus on the core DTC logic; you don't need to implement the actual microservices with `commit` and `rollback` endpoints. You can simulate them for testing.
*   Optimize for correctness, then for performance.  Consider the trade-offs between different data structures for storing transaction participants.
*   Error handling and logging are critical.
*   Assume a relatively small number of participants per transaction (e.g., less than 10).
*   Implement a function `coordinateTransaction(participants)` that takes in an array of `participants` objects of the form `{serviceName: string, commitUrl: string, rollbackUrl: string, roleName: string}` and returns a Promise that resolves to `true` if transaction commits succesfully, `false` otherwise.
*   You must implement a retry mechanism with exponential backoff for commit/rollback phases.

**Example:**

```javascript
const participants = [
    { serviceName: 'InventoryService', commitUrl: 'http://inventory/commit', rollbackUrl: 'http://inventory/rollback', roleName: 'inventory' },
    { serviceName: 'PaymentService', commitUrl: 'http://payment/commit', rollbackUrl: 'http://payment/rollback', roleName: 'payment' },
    { serviceName: 'ShippingService', commitUrl: 'http://shipping/commit', rollbackUrl: 'http://shipping/rollback', roleName: 'shipping' }
];

coordinateTransaction(participants)
    .then(success => {
        if (success) {
            console.log('Transaction committed successfully!');
        } else {
            console.log('Transaction rolled back.');
        }
    })
    .catch(error => {
        console.error('Transaction failed:', error);
    });

```

This problem is designed to test your understanding of distributed systems concepts, asynchronous programming, error handling, and algorithm design. Good luck!
