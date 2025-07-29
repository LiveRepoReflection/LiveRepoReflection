## Question: Distributed Transaction Coordinator

**Description:**

You are tasked with building a simplified distributed transaction coordinator in a simulated environment. Imagine a system where multiple independent services (nodes) need to perform operations that must either *all* succeed or *all* fail, adhering to the ACID properties (Atomicity, Consistency, Isolation, Durability).  This is achieved using a two-phase commit (2PC) protocol.

**System Components:**

*   **Coordinator:** Your code will act as the coordinator. It's responsible for initiating and orchestrating the transaction across the nodes.
*   **Nodes (Participants):** These are simulated services that perform the actual work.  They will receive instructions from the coordinator. For simplicity, each node will have a unique ID (usize) and maintain a single integer value representing its "state".

**Transaction Lifecycle:**

1.  **Initiation:** The coordinator receives a transaction request. The request specifies a list of nodes involved and an operation (increment or decrement) to be performed on each node's state by a specified amount.
2.  **Prepare Phase:** The coordinator sends a "prepare" message to each node, asking if it's ready to commit the transaction. Each node checks if it *can* perform the operation (e.g., sufficient balance for decrement).  The node responds with either "ready" (true) or "abort" (false).
3.  **Commit/Abort Phase:**
    *   If *all* nodes respond with "ready", the coordinator sends a "commit" message to all nodes. Each node then performs the operation and persists its updated state.
    *   If *any* node responds with "abort", or if the coordinator times out waiting for a response from any node, the coordinator sends an "abort" message to all nodes. Each node then rolls back any changes (if any) and returns to its original state.
4.  **Completion:** The coordinator records the outcome of the transaction (committed or aborted).

**Requirements:**

1.  **Implement the Coordinator:**  Implement the logic for the coordinator, including sending messages, handling responses, and making commit/abort decisions based on the 2PC protocol.

2.  **Simulate Nodes:** You don't need to implement actual network communication. Instead, simulate the nodes' behavior using functions that take messages from the coordinator, process them, and return responses.

3.  **Concurrency:** The coordinator and nodes should handle concurrent transaction requests.  Use appropriate synchronization primitives (e.g., Mutexes, RwLocks, Channels) to prevent race conditions and ensure data consistency. The coordinator should be able to handle multiple transactions in parallel.

4.  **Timeouts:** Implement timeouts for the prepare phase. If a node doesn't respond within a specified timeout, the coordinator should treat it as an "abort" and abort the entire transaction.

5.  **Error Handling:** Implement robust error handling.  The system should gracefully handle node failures (simulated by a node occasionally returning an error), invalid transaction requests, and other unexpected situations.

6.  **Logging:** Implement basic logging to track transaction progress, node responses, and any errors that occur.

7.  **Optimizations:** Consider ways to optimize the performance of the coordinator, such as minimizing lock contention or using asynchronous message passing.

**Constraints:**

*   The number of nodes in the system can be up to 100.
*   The timeout for the prepare phase should be configurable.
*   The system should be able to handle up to 1000 concurrent transaction requests.
*   The state of each node should be an integer within the range of i64.
*   Node failures should occur randomly with a probability of 5% during the prepare phase and 2% during the commit phase.

**Evaluation Criteria:**

*   Correctness: Does the system correctly implement the 2PC protocol and ensure atomicity?
*   Concurrency: Does the system handle concurrent transactions correctly and efficiently?
*   Error Handling: Does the system gracefully handle errors and node failures?
*   Performance: Does the system perform well under load?
*   Code Quality: Is the code well-structured, readable, and maintainable?
*   Resource Usage: Are resources properly managed and released to avoid memory leaks or excessive CPU usage?

This problem requires a strong understanding of concurrency, distributed systems principles, and Rust's concurrency primitives. It also encourages you to think about optimization and error handling in a practical scenario. Good luck!
