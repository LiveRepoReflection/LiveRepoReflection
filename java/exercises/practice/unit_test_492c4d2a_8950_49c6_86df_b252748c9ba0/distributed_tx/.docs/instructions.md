## Problem: Distributed Transaction Coordinator

**Description:**

You are tasked with designing and implementing a simplified distributed transaction coordinator (DTC) for a system that manages financial transactions across multiple independent bank services.

**Scenario:**

Imagine a scenario where users can transfer money between accounts held at different banks. Each bank manages its own account data and exposes an API for depositing and withdrawing funds. A single money transfer transaction might involve withdrawing from an account at Bank A and depositing into an account at Bank B. The system must ensure that such cross-bank transfers are atomic; either both the withdrawal and deposit succeed, or neither occurs. This requires a distributed transaction.

**Requirements:**

1.  **Transaction Definition:** A transaction is defined as a list of operations. Each operation involves a bank identifier, an account identifier, and an amount (positive for deposit, negative for withdrawal).

2.  **Two-Phase Commit (2PC):** Implement a simplified version of the 2PC protocol to ensure atomicity across the participating banks. The coordinator is responsible for driving the 2PC protocol.

3.  **Bank Service Simulation:** While you don't need to implement actual bank services, simulate their behavior with a `BankService` interface (described below). Assume that each bank has its own local transaction manager.

4.  **Concurrency:** The coordinator must be able to handle multiple concurrent transactions.

5.  **Failure Handling:** Your coordinator should be resilient to failures. Specifically, consider the following failure scenarios:

    *   A bank service fails during the prepare phase.
    *   The coordinator fails after sending prepare requests but before receiving all responses.
    *   The coordinator fails after sending commit/rollback requests but before receiving all responses.
    *   A bank service fails after receiving a commit/rollback request but before acknowledging it.

    Your solution should provide mechanisms (e.g., logging, recovery mechanisms) to ensure eventual consistency in the face of these failures.  Do not just let the transactions fail without a trace.

6.  **Optimizations (Important):**
    *   **Read-Only Optimization:**  If a bank service is only involved in *read-only* operations (e.g., checking balances before a transfer but not participating in the actual transfer), it should be excluded from the prepare and commit phases, reducing overhead.
    *   **Parallel Prepare Phase:** The prepare phase should be executed in parallel to minimize latency.
    *   **Idempotency:**  Bank services should ideally implement idempotent commit and rollback operations (though this is not strictly required for your solution, it's a good design consideration).

**BankService Interface (Simulation):**

```java
interface BankService {
    boolean prepare(String transactionId, String accountId, double amount); // Returns true if prepared successfully, false if failed
    boolean commit(String transactionId, String accountId, double amount); // Returns true if committed successfully, false if failed
    boolean rollback(String transactionId, String accountId, double amount); // Returns true if rolled back successfully, false if failed

    //For this problem, assume you can also query the current balance of an account. This could be helpful when simulating failures.
    double getBalance(String accountId);
}
```

**Constraints:**

*   **Scalability:** While you don't need to *demonstrate* extreme scalability, your design should *consider* scalability best practices (e.g., avoiding single points of failure, using asynchronous communication where appropriate).
*   **Error Handling:**  Provide robust error handling and logging.  Log all critical events (prepare requests, prepare responses, commit requests, commit responses, rollback requests, rollback responses, failures, recovery actions).
*   **Transaction Id Generation:**  Ensure transaction IDs are unique and consistent across all participating services.
*   **Simplicity:** Aim for a reasonably clean and maintainable code structure, considering the complexity of the problem.

**Judging Criteria:**

*   Correctness: Does the solution correctly implement the 2PC protocol and guarantee atomicity?
*   Failure Handling: How well does the solution handle various failure scenarios? Is data eventually consistent?
*   Concurrency: Can the coordinator handle multiple concurrent transactions without race conditions or deadlocks?
*   Optimizations: Does the solution implement the read-only optimization and parallel prepare phase?
*   Code Quality: Is the code well-structured, documented, and maintainable?
*   Efficiency: Is the solution reasonably efficient in terms of resource usage (CPU, memory)?

This problem requires a solid understanding of distributed systems concepts, concurrency, and error handling. Good luck!
