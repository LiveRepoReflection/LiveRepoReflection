## Problem Title: Distributed Transaction Orchestration

### Problem Description:

You are tasked with designing and implementing a system for orchestrating distributed transactions across multiple independent microservices. Imagine a scenario where an e-commerce platform needs to process an order. This order processing involves several steps, each handled by a separate microservice:

1.  **Inventory Service:** Checks and reserves the required quantity of items in stock.
2.  **Payment Service:** Processes the payment from the customer.
3.  **Shipping Service:** Schedules the shipment of the order.
4.  **Notification Service:** Sends confirmation emails/SMS to the customer.

A successful order requires all these services to complete their tasks successfully. If any of the services fail, the entire transaction must be rolled back to maintain data consistency.

**Specifically, you need to implement a `TransactionOrchestrator` that can handle these distributed transactions.**

Your orchestrator should:

*   Accept a list of `Transaction` objects. Each `Transaction` object encapsulates the logic for a single microservice call (both the `commit` operation and the `rollback` operation).
*   Execute the `commit` operations of each transaction in the given order.
*   If any `commit` operation fails, the orchestrator must execute the `rollback` operations of all previously committed transactions in the *reverse* order of their commit.
*   Handle potential failures during the rollback process gracefully.  If a rollback operation fails, the orchestrator should log the error and continue rolling back the remaining transactions.
*   Provide a mechanism to track the status of each transaction (committed, rolled back, failed to commit, failed to rollback).
*   Be designed to be resilient to network issues and service unavailability. You are free to assume a reasonable retry mechanism exists for individual service calls, but your orchestrator should still handle cases where retries are exhausted and a service is permanently unavailable.

**Constraints:**

*   You are working with independent microservices.  You cannot directly access the databases of these services.  All interactions must be through the provided `Transaction` interface.
*   The system should be designed for high concurrency.  Multiple orders can be processed simultaneously.
*   The solution should be as efficient as possible in terms of resource usage. Avoid unnecessary data copying or redundant operations.
*   Assume that transaction commit and rollback operations are idempotent (i.e., they can be safely executed multiple times without causing unintended side effects).
*   The order of transactions matters.  You must execute the commit operations in the order they are provided and the rollback operations in the reverse order.
*   You are free to use any appropriate Java libraries and data structures.

**Input:**

*   A list of `Transaction` objects representing the steps in the distributed transaction.

**Output:**

*   A `TransactionResult` object that summarizes the outcome of the transaction, including:
    *   Overall status (SUCCESS or FAILURE).
    *   A list of `TransactionStatus` objects, one for each transaction, indicating its individual status (COMMITTED, ROLLED_BACK, COMMIT_FAILED, ROLLBACK_FAILED).
    *   Any error messages encountered during the commit or rollback process.

**Bonus (Optional):**

*   Implement a timeout mechanism for individual transaction operations. If a commit or rollback operation takes longer than a specified timeout, it should be considered a failure.
*   Design the `TransactionOrchestrator` to be easily extensible to support different transaction models (e.g., Saga pattern with compensation transactions).
*   Consider how you would handle long-running transactions that might span multiple days.  How would you ensure that the state of the transaction is persisted and can be recovered in case of system failures?

This problem challenges your understanding of distributed systems, transaction management, concurrency, and error handling. It requires you to design a robust and efficient solution that can handle complex scenarios and potential failures. Good luck!
