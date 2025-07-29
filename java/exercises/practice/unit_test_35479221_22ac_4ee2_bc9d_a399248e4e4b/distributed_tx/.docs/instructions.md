## Project Name

`distributed-transaction-manager`

## Question Description

You are tasked with designing and implementing a simplified distributed transaction manager for a microservices architecture. Imagine a system where multiple services need to coordinate updates to their respective databases as part of a single logical transaction. If any service fails to commit its changes, the entire transaction must be rolled back across all involved services.

**Scenario:**

Consider an e-commerce system composed of three microservices:

*   **Order Service:** Manages order creation and updates in its own database.
*   **Inventory Service:** Manages product inventory levels in its own database.
*   **Payment Service:** Processes payments and records transactions in its own database.

When a customer places an order, the following steps must occur within a single distributed transaction:

1.  Order Service creates a new order record.
2.  Inventory Service decrements the stock levels for the ordered products.
3.  Payment Service processes the payment.

If any of these steps fail (e.g., insufficient inventory, payment failure), all previous steps must be rolled back to maintain data consistency.

**Requirements:**

1.  **Implement a Distributed Transaction Manager (DTM):** The DTM will be responsible for coordinating the transaction across the involved services. The DTM should follow the 2-Phase Commit (2PC) protocol.

2.  **Implement a Transactional Resource Manager (TRM) interface:** Each service (Order, Inventory, Payment) will implement this interface to interact with the DTM. The TRM should define `prepare()`, `commit()`, and `rollback()` methods.

3.  **Simulate Service Failures:** Implement mechanisms to simulate service failures during the transaction, such as network errors or database exceptions.

4.  **Concurrency Control:** Design the DTM to handle concurrent transactions, ensuring data consistency and isolation. This may involve locking or other concurrency control mechanisms.

5.  **Idempotency:** Ensure that the `prepare()`, `commit()`, and `rollback()` operations are idempotent (i.e., executing them multiple times has the same effect as executing them once). This is crucial for handling potential network issues and retries.

6.  **Optimize for Performance:** While correctness is paramount, consider performance implications. Minimize the number of network round trips required to complete a transaction. Explore techniques like asynchronous communication where appropriate.

7.  **Fault Tolerance:** The DTM should be reasonably resilient to failures. Consider how the system would handle a DTM failure during a transaction.

**Constraints:**

*   **Simplicity:** Keep the implementation as simple as possible while still adhering to the core principles of distributed transactions and the 2PC protocol.
*   **Scalability:** While a full-scale distributed system is not required, consider how the design could be scaled to handle a larger number of services and transactions.
*   **External Libraries:** You are allowed to use common Java libraries for networking, concurrency, and data serialization. However, avoid using heavyweight distributed transaction frameworks like JTA or XA. You need to implement the core logic of the DTM yourself.
*   **Testing:** Provide comprehensive unit tests to demonstrate the correctness and fault tolerance of your implementation. Include tests that simulate various failure scenarios.

**Evaluation Criteria:**

*   Correctness of the 2PC implementation.
*   Handling of service failures and rollbacks.
*   Concurrency control and data consistency.
*   Idempotency of operations.
*   Performance considerations.
*   Code quality, readability, and test coverage.
*   Handling of edge cases and error conditions.
*   Clear documentation of the design and implementation.

This problem requires a deep understanding of distributed systems concepts, concurrency control, and fault tolerance. It challenges the candidate to design and implement a real-world system that addresses the complexities of distributed transactions.
