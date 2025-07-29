## Question: Distributed Transaction Orchestration

**Problem Description:**

You are tasked with designing and implementing a distributed transaction orchestrator in Go. This orchestrator is responsible for managing transactions that span multiple independent services. Due to network instability and service failures, transactions can fail midway. The goal is to ensure atomicity (all or nothing) across these services, implementing a Saga pattern with compensating transactions.

**Scenario:**

Imagine an e-commerce platform where placing an order involves the following services:

1.  **Inventory Service:** Reserves the items from stock.
2.  **Payment Service:** Processes the payment.
3.  **Shipping Service:** Schedules the shipment.

Each service has its own database and API. A successful order requires all three services to complete their respective tasks. If any service fails, the orchestrator must trigger compensating transactions in reverse order to undo any changes made by the previously successful services.

**Requirements:**

1.  **Orchestration Logic:** Implement the core logic for orchestrating the distributed transaction using the Saga pattern. The orchestrator should handle the flow of events, service invocations, and error handling.

2.  **Compensating Transactions:** For each service, define and implement a compensating transaction that can undo the changes made by the original transaction. For example:

    *   Inventory Service:  Release the reserved items back to stock.
    *   Payment Service:  Refund the payment.
    *   Shipping Service:  Cancel the scheduled shipment.

3.  **Idempotency:** Ensure that all service invocations (both forward and compensating) are idempotent. This is crucial to handle potential network retries and duplicate messages.  This means that if a service receives the same request multiple times, it should only process it once.

4.  **Concurrency:** The orchestrator should be able to handle multiple concurrent transactions efficiently.

5.  **Failure Handling:** Implement robust failure handling mechanisms. The orchestrator should be able to gracefully handle service failures, network timeouts, and other unexpected errors.  It should retry failed transactions (with a reasonable backoff strategy) and eventually give up after a certain number of attempts, logging the error for manual intervention.

6.  **Transaction Log:** Implement a transaction log to track the state of each transaction. This log should be persistent so that the orchestrator can recover from crashes and resume unfinished transactions. The log should, at minimum, record the transaction ID, the current step, and the status of each step.  Consider using a simple in-memory implementation initially, but discuss the considerations for a persistent storage solution (e.g., database) in a real-world scenario.

7.  **Optimization:** Design your solution to minimize the overall transaction time.  Consider using asynchronous communication (e.g., message queues) to avoid blocking the orchestrator while waiting for service responses.

**Constraints:**

*   **Language:** Go
*   **No external distributed transaction frameworks allowed** (e.g., XA).  You must implement the Saga pattern manually.
*   **Assume eventual consistency.**  It's acceptable for there to be a short delay before the effects of a transaction (or its compensation) are visible across all services.
*   **Services are unreliable.**  Assume that services can fail randomly or be temporarily unavailable.
*   **Network is unreliable.**  Network requests can timeout or be lost.

**Judging Criteria:**

*   **Correctness:** The solution must correctly implement the Saga pattern and ensure atomicity across the services.
*   **Robustness:** The solution must be resilient to failures and handle errors gracefully.
*   **Efficiency:** The solution should be designed to minimize the overall transaction time.
*   **Code Quality:** The code should be well-structured, readable, and maintainable.
*   **Design Considerations:** Clear justification for design choices, particularly around concurrency, failure handling, and transaction log implementation.  Discussion of trade-offs between different approaches.

This problem is designed to test your understanding of distributed systems, concurrency, and error handling in Go. It requires careful consideration of various design trade-offs and optimization strategies. Good luck!
