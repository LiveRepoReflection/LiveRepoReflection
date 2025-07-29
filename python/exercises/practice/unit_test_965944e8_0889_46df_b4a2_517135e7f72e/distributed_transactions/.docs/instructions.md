## Question: Distributed Transaction Coordinator

### Question Description

You are tasked with designing and implementing a simplified distributed transaction coordinator. This system is responsible for ensuring the Atomicity, Consistency, Isolation, and Durability (ACID) properties of transactions that span multiple independent services (nodes).

**Scenario:**

Imagine a microservices architecture where an e-commerce application needs to update inventory and process payment during a purchase. The inventory service manages product stock levels, while the payment service handles financial transactions. These services are independent and communicate over a network.

To ensure a reliable purchase process, both the inventory update and payment processing must either succeed together (commit) or fail together (rollback). This requires a distributed transaction.

**Task:**

Implement a `TransactionCoordinator` class that facilitates two-phase commit (2PC) protocol for distributed transactions. The coordinator will manage participant nodes, orchestrate the prepare phase, and decide on a global commit or rollback based on the participants' votes.

**Specific Requirements:**

1.  **Node Interface:** Define an abstract base class `Node` with the following methods:
    *   `prepare(transaction_id: int) -> bool`: Called by the coordinator to ask the node if it's ready to commit the transaction. Returns `True` if ready, `False` otherwise. The node should perform necessary checks and acquire any locks during this phase, but *not* actually commit any changes.
    *   `commit(transaction_id: int) -> None`: Called by the coordinator to instruct the node to commit the transaction. The node should persist the changes.
    *   `rollback(transaction_id: int) -> None`: Called by the coordinator to instruct the node to rollback the transaction. The node should undo any changes made during the prepare phase and release any locks.
    *   `__init__(node_id: int)`: Each node needs a unique ID.

2.  **Transaction Coordinator Class:** Implement a `TransactionCoordinator` class with the following methods:
    *   `__init__()`: Initialize the coordinator.
    *   `register_node(node: Node) -> None`: Registers a participant node with the coordinator.
    *   `begin_transaction() -> int`: Starts a new transaction and returns a unique transaction ID.
    *   `end_transaction(transaction_id: int) -> bool`: Initiates the 2PC protocol for the given transaction. This method should:
        *   Enter the PREPARE phase: Send `prepare(transaction_id)` to all registered nodes.
        *   Collect votes: If all nodes vote `True`, proceed to COMMIT phase. If any node votes `False`, proceed to ROLLBACK phase.
        *   Enter the COMMIT or ROLLBACK phase: Send `commit(transaction_id)` or `rollback(transaction_id)` to all nodes, respectively.
        *   Return `True` if the transaction committed successfully, `False` otherwise.
    *   `get_node_count() -> int`: Returns the number of registered nodes (for testing purposes).

3.  **Concurrency Considerations:**
    *   The system should handle concurrent transaction requests.
    *   Nodes can fail during any phase. Simulate node failures by having each node randomly fail (return False from `prepare`, or raise an exception from `commit` or `rollback`) with a probability of `failure_rate`. This `failure_rate` should be a parameter to the `Node` constructor (defaulting to 0.0).
    *   Implement appropriate locking mechanisms to ensure data consistency at each node, even if transactions overlap. You are free to choose any suitable locking strategy (e.g., pessimistic locking).  Consider how long locks are held for, and avoid deadlocks.
    *   The coordinator itself should be resilient to node failures. It should retry failed operations (e.g., prepare, commit, rollback) a configurable number of times (`retry_count`) before giving up. Add `retry_count` as a parameter to the `TransactionCoordinator` constructor (defaulting to 3). Use exponential backoff for retries (e.g., wait 1 second, then 2 seconds, then 4 seconds).

4.  **Optimization:**
    *   Implement the `prepare` phase concurrently using threads or asynchronous programming to reduce the overall transaction completion time.

**Constraints:**

*   The number of nodes participating in a transaction can be large.
*   Network latency between the coordinator and nodes can be significant.
*   Nodes can fail unpredictably.
*   Transactions must be processed within a reasonable time frame, even under high load and node failures.
*   The solution must prevent data corruption and ensure data consistency across all nodes.
*   Assume all node operations are idempotent (safe to retry).

**Evaluation Criteria:**

*   Correctness: The solution must correctly implement the 2PC protocol and ensure ACID properties.
*   Performance: The solution should minimize transaction completion time, especially under concurrent load.
*   Fault Tolerance: The solution should handle node failures gracefully and ensure transaction completion or rollback.
*   Scalability: The solution should be able to handle a large number of nodes and transactions.
*   Code Quality: The code should be well-structured, readable, and maintainable.

This problem requires a deep understanding of distributed systems concepts, concurrency, and fault tolerance. It challenges the solver to design and implement a robust and efficient distributed transaction coordinator. Good luck!
