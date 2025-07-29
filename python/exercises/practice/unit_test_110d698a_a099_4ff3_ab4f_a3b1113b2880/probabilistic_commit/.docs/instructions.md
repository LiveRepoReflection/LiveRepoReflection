## Question: Distributed Transaction Coordinator

### Question Description

You are tasked with designing and implementing a simplified distributed transaction coordinator. In a distributed system, ensuring that a series of operations across multiple services (databases, message queues, etc.) either all succeed or all fail is crucial for maintaining data consistency. This is typically achieved through a transaction coordinator that implements the Two-Phase Commit (2PC) protocol.

However, due to limited resources, you cannot implement the full 2PC protocol. Instead, you will implement a *Probabilistic Commit Protocol (PCP)*, which is a weaker but more scalable alternative.

**The System:**

*   You have `N` independent services (represented by integers from `0` to `N-1`).
*   Each service can perform a single atomic operation (either commit or abort).
*   You are the designated transaction coordinator.
*   Communication between the coordinator and services is reliable but potentially slow.

**The Probabilistic Commit Protocol (PCP):**

1.  **Prepare Phase:** The coordinator sends a "prepare" message to all `N` services.
2.  **Vote Phase:** Each service, upon receiving the "prepare" message, independently and randomly decides whether to vote "commit" or "abort". The probability of voting "commit" is `p` (a floating-point number between 0 and 1, inclusive). This probability is the same for all services. Each service sends its vote back to the coordinator.  Services make their decisions independently of each other.
3.  **Commit/Abort Phase:**
    *   If *all* services vote "commit", the coordinator sends a "commit" message to all services.
    *   If *at least one* service votes "abort", the coordinator sends an "abort" message to all services.
    *   If a service does not receive either a "commit" or "abort" message from the coordinator within a given timeout `T`, it must assume the transaction has been aborted, and it should roll back any tentative changes.

**Your Task:**

Implement the `TransactionCoordinator` class with the following methods:

*   `__init__(self, num_services: int, commit_probability: float, timeout: int)`: Initializes the coordinator with the number of services `N`, the commit probability `p`, and the timeout `T`.
*   `run_transaction(self) -> bool`: Initiates and executes a single transaction. The method should simulate the "prepare", "vote", and "commit/abort" phases of the PCP. It should return `True` if the transaction successfully commits (i.e., all services voted "commit"), and `False` otherwise.

**Constraints and Edge Cases:**

*   `1 <= N <= 1000` (Number of services)
*   `0.0 <= p <= 1.0` (Commit probability)
*   `1 <= T <= 100` (Timeout in arbitrary units)
*   Assume the service behavior is purely based on the given commit probability.  No service can lie or be malicious.
*   The `run_transaction` method should simulate the entire transaction process, including the random voting by services.
*   The simulation should be efficient. Avoid unnecessary delays or computations.

**Optimizations and Considerations:**

*   Think about how to efficiently simulate the random voting process.
*   Consider the impact of the commit probability `p` on the overall success rate of transactions.
*   This is a simplified model.  In a real distributed system, handling network partitions, service failures, and message loss would add significant complexity.  You do *not* need to handle these failure scenarios for this problem.

**Example:**

If `N = 3` and `p = 0.5`, each service has a 50% chance of voting "commit". The transaction will only commit if all three services vote "commit".  The `run_transaction` method should simulate this process and return `True` if all services vote "commit", and `False` otherwise.
