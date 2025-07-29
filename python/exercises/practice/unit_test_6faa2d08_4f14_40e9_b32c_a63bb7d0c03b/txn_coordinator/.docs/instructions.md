Okay, here's a challenging Python coding problem designed to be on par with LeetCode Hard difficulty, incorporating the requested elements.

## Problem: Distributed Transaction Coordinator

### Description

You are tasked with designing and implementing a simplified distributed transaction coordinator. In a distributed system, multiple services (nodes) may need to perform operations that must either all succeed or all fail together – a transaction. Your coordinator will ensure this "all or nothing" guarantee using the two-phase commit (2PC) protocol.

Imagine a scenario where you have a payment service and an inventory service. A customer places an order, which requires the payment service to deduct funds and the inventory service to reduce stock. Both operations must succeed to complete the order. If either fails, the entire order should be cancelled (rollback).

**Your Goal:**

Implement a `TransactionCoordinator` class that orchestrates distributed transactions across multiple participating `Node` instances.  The coordinator should handle the following:

1.  **Registration:** Nodes register with the coordinator, indicating their willingness to participate in transactions.

2.  **Prepare Phase:** Upon receiving a transaction request (a list of operations to be performed by different nodes), the coordinator initiates the prepare phase.  It sends a "prepare" message to each participating node, asking them to tentatively execute their operation and indicate whether they are ready to commit.

3.  **Commit/Rollback Phase:**
    *   If all nodes respond positively ("ready to commit") during the prepare phase, the coordinator sends a "commit" message to all nodes, instructing them to make their changes permanent.
    *   If any node responds negatively ("abort") or fails to respond within a specified timeout during the prepare phase, the coordinator sends a "rollback" message to all nodes, instructing them to undo their tentative changes.

**Classes:**

*   **`Node(node_id)`:** Represents a participating service in the distributed transaction.
    *   `node_id`: A unique identifier for the node (string).
    *   `prepare(operation)`:  Simulates the tentative execution of an operation.  It should return `True` if the operation can be prepared successfully, and `False` if it must abort. The operation itself is a string describing an action to be taken by the node. The prepare method should also store the 'operation' for possible later use by commit or rollback.
    *   `commit()`:  Makes the prepared operation permanent.  This method should clear any stored operations.
    *   `rollback()`:  Undoes the prepared operation. This method should clear any stored operations.
*   **`TransactionCoordinator(timeout)`:** Manages the distributed transaction.
    *   `timeout`: Maximum time (in seconds) to wait for a node to respond during the prepare phase (integer).
    *   `register_node(node)`:  Registers a `Node` instance with the coordinator.
    *   `execute_transaction(operations)`: Executes a distributed transaction.
        *   `operations`: A list of tuples, where each tuple contains `(node_id, operation)`. `node_id` identifies the node that should execute the `operation`.
        *   The function should return `True` if the transaction commits successfully, and `False` if it rolls back.

**Constraints and Considerations:**

*   **Atomicity:**  The transaction must be atomic. All operations must either succeed (commit) or all operations must fail (rollback).
*   **Timeout:**  Implement a timeout mechanism during the prepare phase. If a node doesn't respond within the specified timeout, the transaction should be rolled back.
*   **Concurrency:** Although you don't need to implement actual multi-threading/asyncio for this exercise, your code structure should be able to handle concurrent calls to the prepare, commit, and rollback methods from the coordinator. Think about thread safety.
*   **Error Handling:**  Consider potential error conditions (e.g., node not registered, invalid operation) and handle them gracefully.
*   **Idempotency:** (Bonus points):  Consider how to make the commit and rollback operations idempotent (i.e., safe to execute multiple times without unintended side effects). You don't have to implement full idempotency, but describe your approach.
*   **Optimization:** While a fully optimized solution isn't required, consider the algorithmic efficiency of your implementation. Aim for reasonable performance (e.g., avoid unnecessary nested loops).

**Example:**

```python
node1 = Node("payment_service")
node2 = Node("inventory_service")

coordinator = TransactionCoordinator(timeout=5)
coordinator.register_node(node1)
coordinator.register_node(node2)

operations = [
    ("payment_service", "deduct $10 from account"),
    ("inventory_service", "reduce stock of item X by 1"),
]

success = coordinator.execute_transaction(operations)

if success:
    print("Transaction committed successfully!")
else:
    print("Transaction rolled back.")
```

This problem requires a solid understanding of distributed systems concepts, careful handling of edge cases, and a focus on robust error handling. Good luck!
