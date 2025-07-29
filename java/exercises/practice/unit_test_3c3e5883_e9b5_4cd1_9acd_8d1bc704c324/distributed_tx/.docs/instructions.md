## Question: Distributed Transaction Manager

### Problem Description

You are tasked with designing and implementing a simplified, in-memory distributed transaction manager for a microservices architecture. This transaction manager will coordinate transactions that span multiple services.

Imagine a scenario where an e-commerce platform utilizes several microservices: `OrderService`, `PaymentService`, and `InventoryService`. When a user places an order, a transaction must be initiated that involves:

1.  Reserving inventory in `InventoryService`.
2.  Processing payment in `PaymentService`.
3.  Creating the order in `OrderService`.

All three operations must either succeed together (commit) or fail together (rollback) to maintain data consistency. Your task is to implement the core logic of the distributed transaction manager to ensure atomicity across these services.

**Specific Requirements:**

1.  **Transaction Coordination:** Implement a central coordinator that manages the transaction lifecycle. The coordinator should be able to start a transaction, register participants (services involved in the transaction), and orchestrate the commit or rollback of the transaction.
2.  **Two-Phase Commit (2PC):** Implement the 2PC protocol. The coordinator should first send a "prepare" message to all participants. If all participants respond with "ready", the coordinator sends a "commit" message. Otherwise, it sends a "rollback" message.
3.  **Concurrency:** The transaction manager must handle concurrent transactions safely and efficiently.  Use appropriate synchronization mechanisms to prevent race conditions and ensure data integrity.
4.  **Fault Tolerance (Partial):**  Assume participants are reliable and will respond to prepare, commit, and rollback messages. You do not need to handle participant crashes or network failures.  However, the Coordinator itself can potentially fail. Implement a simple mechanism to recover the Coordinator's state upon restart. You can use a simple file-based persistence for this recovery (e.g., storing transaction logs).
5.  **Idempotency:** Design your system such that messages to services are idempotent. That is, if a service receives the same message multiple times (e.g., due to retries), it should only execute the corresponding action once.  Consider using unique transaction IDs to facilitate this.
6.  **Optimization:**  Minimize the latency involved in the transaction commit process.  Consider optimizing the message passing and synchronization mechanisms used.
7.  **Abstraction:** Define clear interfaces for the participants (`OrderService`, `PaymentService`, `InventoryService`) to interact with the transaction manager.
8.  **Scalability:** While a fully scalable solution is beyond the scope of this exercise, consider the design implications for scaling the transaction manager to handle a large number of concurrent transactions and participants. Think about potential bottlenecks and how they might be addressed in a real-world system.

**Input:**

Your solution will not receive direct input. Instead, you will implement the transaction manager and participant interfaces, and then demonstrate its functionality using a provided simulation. The simulation will define the sequence of operations, including starting transactions, registering participants, and triggering commit/rollback scenarios.

**Output:**

Your solution will not produce direct output. Instead, the provided simulation will verify the correctness of your transaction manager implementation by checking the state of the participants after each transaction (e.g., whether inventory was correctly reserved, payment was processed, and the order was created). The simulation will also check the transaction logs to ensure proper recovery of the Coordinator's state.

**Constraints:**

*   Implement the transaction manager in Java.
*   Use standard Java libraries for concurrency and file I/O.
*   Your solution should be well-documented and easy to understand.
*   Minimize dependencies on external libraries.
*   The provided simulation must pass with your implementation.

**Judging Criteria:**

*   Correctness: The transaction manager must correctly implement the 2PC protocol and ensure atomicity across participants.
*   Concurrency: The transaction manager must handle concurrent transactions safely and efficiently.
*   Fault Tolerance: The transaction manager must be able to recover its state after a restart.
*   Idempotency: The participant services must handle duplicate messages gracefully.
*   Optimization: The transaction commit latency should be minimized.
*   Design: The solution should be well-designed, modular, and easy to maintain.
*   Scalability Considerations: The design should demonstrate awareness of scalability challenges and potential solutions.

This problem requires a deep understanding of distributed systems concepts, concurrency, and fault tolerance. It challenges the solver to design and implement a complex system that meets stringent requirements. The focus is not just on writing code, but on designing a robust and scalable solution. Good luck!
