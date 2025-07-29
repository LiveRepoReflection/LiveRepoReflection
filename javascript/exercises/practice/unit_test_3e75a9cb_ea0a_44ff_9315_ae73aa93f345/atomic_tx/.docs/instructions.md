## Problem: Distributed Transaction Manager

You are tasked with building a simplified distributed transaction manager (DTM) for a microservices architecture. Imagine you have multiple independent services (databases, message queues, etc.) participating in a single logical transaction. The goal is to ensure either all services commit their changes, or all roll back, even in the face of network failures, service crashes, or other unexpected errors.

**Details:**

You will be provided with an array of `operations`. Each `operation` represents an action to be performed on a specific service. Each `operation` is an object with the following structure:

```javascript
{
  serviceId: string, // Unique identifier for the service (e.g., "database-service", "message-queue")
  type: string, // Type of operation ("commit" or "rollback")
  data: any, // Data required for the commit/rollback operation. This is service-specific.
  prepare: (data: any) => Promise<boolean>, // Async function that attempts to prepare the service for the commit/rollback. Returns true if preparation is successful, false otherwise.
  execute: (data: any) => Promise<void>, // Async function that actually commits or rollbacks the operation.
}
```

Your task is to implement a function `coordinateTransaction(operations)` that takes this array of `operations` and ensures atomic execution across all services.

**Requirements:**

1.  **Atomicity:** The transaction must be atomic. Either all commits succeed, or all rollbacks succeed.
2.  **Durability:** Once a commit is successful, it must be durable, even if the DTM crashes afterward. (For the sake of this problem, assume the `execute` function already handles persistence within each service.)
3.  **Isolation:**  We assume each service handles isolation internally. Your DTM does not need to manage concurrent transactions.
4.  **Error Handling:**  The function must handle errors gracefully. If any operation fails during the prepare or execute phase, the DTM must attempt to rollback all previously prepared operations.
5.  **Asynchronous:** All operations are asynchronous (Promises). The DTM must handle them concurrently to minimize latency.
6.  **Idempotency:** The `execute` functions (both commit and rollback) *must* be idempotent.  The DTM might call them multiple times in case of failures and retries.  Assume the underlying services are designed to handle this.
7.  **Optimistic Concurrency Control:** Assume services implement optimistic concurrency control. If preparation fails, it might be due to concurrent modifications on the service. The DTM must handle this gracefully by attempting rollback.
8.  **No External Libraries:** You are restricted to using standard JavaScript features, and you cannot use any external libraries.
9.  **Timeout:** Implement a global timeout for the entire transaction. If the transaction does not complete within a specified time limit (e.g., 30 seconds), the DTM should initiate a rollback.

**Constraints:**

*   The number of services involved in a transaction can be up to 100.
*   Each service might take varying amounts of time to prepare and execute (from milliseconds to several seconds).
*   Network connections between the DTM and services are unreliable.
*   Services might temporarily become unavailable.

**Output:**

The `coordinateTransaction` function should return a Promise that resolves to `true` if the transaction commits successfully, and `false` if the transaction rolls back (either due to an error or a timeout).

**Example:**

```javascript
async function coordinateTransaction(operations) {
  // Your implementation here
}

// Example Usage:
const operations = [
  {
    serviceId: "db1",
    type: "commit",
    data: { recordId: 123, newValue: "updated value" },
    prepare: async (data) => { /* Simulate prepare */ return true; },
    execute: async (data) => { /* Simulate commit */ }
  },
  {
    serviceId: "mq1",
    type: "commit",
    data: { message: "data updated" },
    prepare: async (data) => { /* Simulate prepare */ return true; },
    execute: async (data) => { /* Simulate commit */ }
  }
];

coordinateTransaction(operations)
  .then(result => {
    if (result) {
      console.log("Transaction committed successfully!");
    } else {
      console.log("Transaction rolled back.");
    }
  })
  .catch(error => {
    console.error("Transaction failed:", error);
  });
```
