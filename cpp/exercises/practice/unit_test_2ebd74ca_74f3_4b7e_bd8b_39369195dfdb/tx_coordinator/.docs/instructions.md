Okay, here's a problem designed to be challenging and require careful consideration of data structures, algorithms, and optimization.

**Problem Title:** Distributed Transaction Coordinator

**Problem Description:**

You are tasked with building a simplified, in-memory transaction coordinator for a distributed system.  Imagine a scenario where multiple services (nodes) need to perform operations that must either all succeed or all fail, guaranteeing atomicity.

Your transaction coordinator will manage transactions across these nodes.  Each transaction involves a series of *operations* on different nodes. Each node will have a unique `node_id` (positive integer) and each operation will have a unique `operation_id` (positive integer).

**Your task is to implement the following functionalities:**

1.  **Transaction Creation:**  The coordinator should be able to initiate new transactions. Each transaction will have a unique `transaction_id` (positive integer).

2.  **Operation Registration:** Nodes can register operations with a transaction.  For each operation, they provide the `transaction_id`, their `node_id`, the `operation_id`, and an estimated *cost* (positive integer) representing the resources required to perform the operation.  The coordinator must track which operations belong to which transaction and on which node.

3.  **Two-Phase Commit (2PC) Protocol:** Implement a simplified version of the 2PC protocol:

    *   **Prepare Phase:** Once a transaction is ready to commit (explicitly signaled by a `Prepare` call), the coordinator must iterate through all nodes involved in the transaction.  For each node, it simulates sending a "prepare" message.  Assume that each node *always* responds positively (i.e., it's prepared to commit).
    *   **Commit Phase:** After the prepare phase (which always succeeds in this simplified version), the coordinator initiates the commit phase.  It simulates sending a "commit" message to each node involved in the transaction.  Nodes are assumed to *always* successfully commit.
    *   **Rollback (Abort) Phase:** If, at any point during the prepare phase (in a more robust real world implementation, but not in our simplified version), a node signals a failure to prepare, the coordinator must initiate a rollback phase.  It simulates sending a "rollback" message to all nodes involved in the transaction. Nodes are assumed to *always* successfully rollback. *However, in THIS simplified problem, the prepare phase NEVER fails, so the rollback phase is never actually entered.*

4.  **Transaction Status Tracking:** Track the status of each transaction. The status can be one of the following: `PENDING`, `PREPARING`, `COMMITTED`, `ABORTED`.

5.  **Resource Optimization**:  Before a `Prepare` call is made, the coordinator should identify and track the *critical node* of each transaction. The critical node is the node with the *highest total cost* of operations associated with a given transaction.  If multiple nodes have the same highest total cost, the node with the lowest `node_id` is selected as the critical node.

6.  **Atomicity Guarantee (in simulation):**  Although the nodes are assumed to always succeed in this simplified model, the coordinator must still track the operations and their associated transactions to ensure that, in a real system, the coordinator *would* have the information needed to guarantee atomicity.

**Constraints and Edge Cases:**

*   **Large Number of Nodes and Operations:** Your solution must be efficient enough to handle a large number of nodes (up to 10<sup>5</sup>), transactions (up to 10<sup>5</sup>), and operations (up to 10<sup>6</sup>).
*   **Concurrency (Implicit):**  While you don't need to implement actual multi-threading, your data structures and logic should be designed in a way that would allow for concurrent access from multiple threads (think about thread-safety if you were to actually implement concurrency).  Avoid global state and use appropriate synchronization primitives (even if they are just placeholders in this in-memory simulation).
*   **Memory Management:** Optimize memory usage.  Avoid unnecessary copying of data.
*   **Error Handling:**  Implement robust error handling for invalid inputs (e.g., registering an operation with a non-existent transaction).  Return appropriate error codes or exceptions (depending on the language) in these cases.
*   **Idempotency:**  Think about the idempotency of operations (e.g., what happens if `Prepare` is called multiple times for the same transaction?).  Document your assumptions about idempotency.

**Input:**

The input consists of a series of commands to the transaction coordinator.  You need to parse these commands and perform the corresponding actions.

**Output:**

The output consists of responses to the commands.  The format of the output should be clearly defined and consistent.  For example, successful operations could return "OK", while errors could return "ERROR: ".  Specific output requirements will be provided with specific input examples.

**Example Commands (and expected behavior explained further in detailed test cases - not provided yet):**

*   `CREATE_TRANSACTION <transaction_id>`
*   `REGISTER_OPERATION <transaction_id> <node_id> <operation_id> <cost>`
*   `PREPARE <transaction_id>`
*   `GET_STATUS <transaction_id>`
*   `GET_CRITICAL_NODE <transaction_id>`

**Judging Criteria:**

*   **Correctness:**  Your solution must correctly implement the transaction coordinator logic and the 2PC protocol (even in its simplified form).
*   **Efficiency:**  Your solution must be efficient in terms of both time and memory usage.
*   **Code Quality:**  Your code must be well-structured, readable, and maintainable.  Use appropriate data structures and algorithms.
*   **Error Handling:**  Your solution must handle errors gracefully and provide informative error messages.

This problem requires a good understanding of distributed systems concepts, data structures, and algorithms. It challenges you to design a solution that is both correct and efficient. Good luck!
