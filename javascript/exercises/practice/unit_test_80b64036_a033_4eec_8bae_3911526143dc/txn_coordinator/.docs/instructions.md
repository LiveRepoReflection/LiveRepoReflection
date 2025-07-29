## Problem: Distributed Transaction Coordinator

**Description:**

You are tasked with designing and implementing a distributed transaction coordinator in Javascript. This coordinator will manage transactions across multiple independent services. Due to network latency and the potential for service failures, achieving atomicity, consistency, isolation, and durability (ACID) properties is a significant challenge.

Each service is responsible for managing its own data and exposes an API to participate in distributed transactions. The coordinator must ensure that either all services commit their changes or all services roll back, even in the face of failures. You will implement a simplified version of the Two-Phase Commit (2PC) protocol to achieve this.

**Scenario:**

Imagine an e-commerce system where placing an order involves multiple services:

1.  **Inventory Service:** Checks stock availability and reserves items.
2.  **Payment Service:** Processes payment.
3.  **Order Service:** Creates the order record.
4.  **Shipping Service:** Schedules the shipping.

A transaction coordinator is necessary to guarantee that an order is only placed if all the above services successfully complete their respective operations. If any of the services fails (e.g., insufficient stock, payment failure, service unavailable), the entire transaction must be rolled back.

**Requirements:**

1.  **Transaction ID Generation:** Implement a mechanism to generate unique transaction IDs.  These IDs must be globally unique across your distributed system.
2.  **2PC Implementation:** Implement the 2PC protocol with the following phases:

    *   **Phase 1 (Prepare):** The coordinator sends a "prepare" request to each participating service.  Each service attempts to perform its part of the transaction tentatively and responds with either a "vote commit" or "vote abort."  Services must be able to undo any tentative changes made during the prepare phase. Assume each service exposes `prepare(transactionId)` and `rollback(transactionId)` methods.
    *   **Phase 2 (Commit/Rollback):** Based on the responses from the prepare phase, the coordinator decides to either commit or roll back the transaction. If all services voted to commit, the coordinator sends a "commit" request to each service. Otherwise, it sends a "rollback" request. Assume each service exposes `commit(transactionId)` method.
3.  **Failure Handling:** Implement retry mechanisms for failed requests to services. Consider different retry strategies (e.g., exponential backoff) and maximum retry attempts.  If a service fails to respond after the maximum number of retries, the coordinator must assume the worst (abort) and trigger a rollback of the entire transaction.
4.  **Idempotency:** Design the system to be idempotent.  Services might receive commit or rollback requests multiple times due to network issues. Ensure that processing the same request multiple times doesn't lead to unintended side effects.
5.  **Concurrency:** Your coordinator needs to handle multiple concurrent transactions. Ensure that transactions are properly isolated from each other.
6.  **Logging:** Implement logging to persistent storage (e.g., a file or a simple in-memory data structure for testing) to record the transaction state and decisions made by the coordinator. This is crucial for recovery in case the coordinator itself fails.
7.  **Timeout:** Implement a timeout mechanism. If a service does not respond within a reasonable timeframe in either phase, the coordinator should consider it a failure and initiate a rollback.

**Constraints:**

*   You are working in a simulated environment. You do not need to interact with real external services. Simulate service behavior (success, failure, timeout) programmatically.
*   Focus on the core logic of the transaction coordinator and the 2PC protocol. You don't need to implement a full-fledged distributed system with message queues, service discovery, etc.  Simulate service interactions with direct function calls or Promises.
*   Assume that services use a simple key-value store for persistence.  You can simulate this with Javascript objects.
*   Optimization: Optimize the coordinator for minimal latency. Avoid unnecessary blocking calls. Consider using Promises and async/await to handle asynchronous operations efficiently.
*   Scalability: While a full scalable architecture is not required, think about how your design could be extended to handle a large number of concurrent transactions and participating services.  Mention the potential bottlenecks and how they could be addressed in a real-world deployment.

**Input:**

An array of service objects, each exposing `prepare`, `commit`, and `rollback` methods.  Each method accepts a transaction ID as an argument. The transaction coordinator function should also take an optional configuration object containing retry parameters, timeouts, and a logging interface.

**Output:**

The function should return a Promise that resolves to `true` if the transaction committed successfully and `false` if it rolled back. The Promise should reject with an error if the input is invalid or if an unexpected error occurs within the coordinator.

**Example Service Interface (Simulated):**

```javascript
const inventoryService = {
    data: {}, // Simulate a key-value store

    prepare: async (transactionId) => {
        // Simulate checking stock and reserving items.
        // May succeed, fail, or timeout.
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                // Randomly simulate success or failure.
                if (Math.random() > 0.2) {
                    // Simulate a successful reservation.
                    inventoryService.data[transactionId] = { reserved: true };
                    resolve('vote commit');
                } else {
                    reject('vote abort');
                }
            }, Math.random() * 50); // Simulate varying latency.
        });
    },

    commit: async (transactionId) => {
        // Simulate committing the inventory reservation.
        return new Promise((resolve) => {
            setTimeout(() => {
                // Mark the reservation as permanent.
                inventoryService.data[transactionId].committed = true;
                resolve();
            }, Math.random() * 50);
        });
    },

    rollback: async (transactionId) => {
        // Simulate rolling back the inventory reservation.
        return new Promise((resolve) => {
            setTimeout(() => {
                // Remove the reservation.
                delete inventoryService.data[transactionId];
                resolve();
            }, Math.random() * 50);
        });
    }
};
```

This problem challenges you to implement a robust and fault-tolerant distributed transaction coordinator, considering various edge cases and optimization requirements. Good luck!
