Okay, here's a challenging Javascript coding problem designed to be LeetCode Hard level.

## Problem: Distributed Transaction Orchestrator

### Question Description

You are tasked with designing and implementing a simplified, in-memory distributed transaction orchestrator in Javascript. This orchestrator will manage transactions across multiple independent "services".  Each service can perform a single atomic operation. A transaction consists of a sequence of operations across these services.  The goal is to ensure all operations in a transaction either complete successfully (commit) or, if any operation fails, all operations are rolled back (abort).

**Core Concepts:**

*   **Services:** Represented as objects with `commit(data)` and `rollback(data)` methods. These methods simulate performing an action and undoing it, respectively.  They can either resolve (success) or reject (failure). The `data` parameter passed to these methods is a transaction-specific payload.

*   **Transactions:** Defined as an array of operations. Each operation is an object with `service` (a reference to a service object) and `data` (the data to pass to the service's commit and rollback methods).

*   **Orchestrator:**  The central component responsible for executing transactions, handling failures, and ensuring atomicity.

**Requirements:**

1.  **`executeTransaction(transaction)`:** This function is the core of your solution. It takes a `transaction` (array of operations) as input and returns a Promise. The Promise should resolve when the transaction commits successfully and reject when the transaction aborts.

2.  **Atomicity:** Ensure that all operations in the transaction either succeed or all are rolled back. If any service's `commit()` method rejects, the orchestrator must initiate a rollback of all previously committed operations.

3.  **Idempotency:** Services might fail during the rollback phase.  The orchestrator should be resilient to these failures and ensure that rollback operations are attempted repeatedly until they eventually succeed (within a reasonable retry limit). Assume that rollback functions are eventually consistent.

4.  **Concurrency:**  The orchestrator must handle concurrent transactions.  Avoid race conditions and ensure that transactions are executed in isolation.  You can assume a single-threaded Javascript environment (Node.js event loop).

5.  **Error Handling:** Provide informative error messages when a transaction fails, including the reason for the failure and the service that caused the failure.

6.  **Optimization:** Minimize the time it takes to execute a transaction, especially in the face of failures.  Avoid unnecessary delays or retries.

7.  **Ordering:** The commit phase should execute the operations in the order they are defined within the transaction array. The rollback phase should execute the operations in reverse order of commit.

**Constraints:**

*   You cannot modify the service objects themselves.  You can only interact with them through their `commit()` and `rollback()` methods.
*   The `commit()` and `rollback()` methods of the services may be asynchronous (return Promises).
*   The number of services and operations in a transaction can be large.
*   Resource contention should be avoided.

**Example Service:**

```javascript
const serviceA = {
  async commit(data) {
    return new Promise((resolve, reject) => {
      // Simulate success or failure
      const success = Math.random() > 0.1; // 90% success rate
      setTimeout(() => {
        if (success) {
          console.log(`Service A committed with data: ${data}`);
          resolve();
        } else {
          console.error(`Service A failed to commit with data: ${data}`);
          reject(new Error("Service A commit failed"));
        }
      }, 50); // Simulate some latency
    });
  },
  async rollback(data) {
    return new Promise((resolve, reject) => {
      // Simulate success or failure
      const success = Math.random() > 0.05; // 95% success rate
      setTimeout(() => {
        if (success) {
          console.log(`Service A rolled back with data: ${data}`);
          resolve();
        } else {
          console.error(`Service A failed to rollback with data: ${data}`);
          reject(new Error("Service A rollback failed"));
        }
      }, 50); // Simulate some latency
    });
  },
};
```

**Deliverable:**

Implement the `executeTransaction(transaction)` function.  Provide clear and concise code, along with comments explaining your approach.  Consider different architectural patterns and trade-offs when designing your solution. Focus on the atomicity and idempotency requirements. Good luck!
