Okay, here's a challenging C++ coding problem designed to test a wide range of skills.

**Problem Title: Distributed Transaction Coordinator**

**Problem Description:**

You are tasked with designing and implementing a distributed transaction coordinator for a simplified database system. This system consists of `N` nodes (where `1 <= N <= 1000`), each holding a portion of the overall database.  The goal is to ensure ACID (Atomicity, Consistency, Isolation, Durability) properties for transactions that span multiple nodes.

Each transaction involves operations on a subset of the `N` nodes.  The coordinator is responsible for orchestrating these transactions using a variant of the two-phase commit (2PC) protocol.  However, due to unreliable network conditions, nodes can fail unexpectedly, and messages can be lost or delayed.

**Specific Requirements:**

1.  **Node Identification:** Each node is identified by a unique integer ID from 1 to `N`.

2.  **Transaction Structure:** A transaction is represented as a list of node IDs on which the transaction needs to perform an operation (e.g., update a record). The coordinator receives a transaction request as a list of node IDs.  Each node in the list must participate in the transaction.

3.  **Two-Phase Commit (2PC) Protocol (Simplified):**
    *   **Phase 1 (Prepare):** The coordinator sends a "prepare" message to all involved nodes. Each node, upon receiving the "prepare" message, attempts to prepare the transaction locally (e.g., write to a redo log).  The node then sends either a "vote-commit" or "vote-abort" message back to the coordinator. A node might vote to abort if it encounters any issues (e.g., resource contention, data validation failure).
    *   **Phase 2 (Commit/Abort):**
        *   If the coordinator receives "vote-commit" messages from *all* participating nodes, it sends a "commit" message to all involved nodes. Upon receiving the "commit" message, each node permanently applies the transaction.
        *   If the coordinator receives at least one "vote-abort" message, or if it doesn't receive a response from a node within a specified timeout (see below), it sends an "abort" message to all involved nodes. Upon receiving the "abort" message, each node rolls back the transaction.
        *   If a node does not receive a commit or abort message, it will retry the last known state until it is resolved.

4.  **Failure Handling and Timeouts:**
    *   **Node Failures:** Nodes can fail at any point during the transaction. If a node fails before responding to the "prepare" message, the coordinator should consider the node as having voted to abort (after a timeout period). If a node fails after voting to commit but before receiving the "commit" message, it must recover its state upon restart and eventually complete the transaction (either commit or abort) based on the coordinator's eventual decision.
    *   **Message Loss/Delay:** Messages between the coordinator and nodes can be lost or delayed. Implement timeouts for receiving responses from nodes. If a timeout occurs during the prepare phase, treat it as a "vote-abort." If a timeout occurs during the commit/abort phase, resend the commit/abort message.
    *   **Timeout:** A global timeout value `T` (in milliseconds) is provided.  If the coordinator doesn't receive a response from a node within `T` milliseconds, it considers the node unresponsive.

5.  **Durability:**  Nodes must ensure durability of their votes (commit or abort decision) and the final transaction outcome (commit or rollback) by using logging (e.g., writing to a file). Upon restart, a node should recover its state by reading the log and continue from where it left off.

6.  **Concurrency:** Multiple transactions can be initiated concurrently.  The coordinator must handle concurrent transactions correctly, ensuring isolation between them. Implement appropriate locking mechanisms to prevent data corruption.

7.  **Optimization:**  Minimize the latency of transaction completion.  Consider techniques such as asynchronous message handling and optimized logging.  The system should be able to handle a reasonable number of concurrent transactions (e.g., up to 100) without significant performance degradation.

**Input:**

The input will be provided through standard input.

*   The first line contains two integers: `N` (the number of nodes) and `T` (the timeout value in milliseconds).
*   Subsequent lines represent transaction requests. Each line starts with the transaction ID (a unique integer) followed by a space-separated list of node IDs involved in the transaction.
*   The input ends with a line containing "END".

**Output:**

For each transaction, the coordinator should print a message to standard output indicating the outcome of the transaction (either "COMMIT" or "ABORT"). The output should be prefixed with the transaction ID.  Example:

```
Transaction 123: COMMIT
Transaction 456: ABORT
```

Additionally, each node, upon receiving a prepare, commit or abort message, should log the message with a timestamp to its own log file. The log file for node `i` is named `node_i.log`.

**Example Input:**

```
3 100
123 1 2 3
456 1 2
END
```

**Constraints:**

*   1 <= N <= 1000
*   1 <= T <= 5000 (milliseconds)
*   Transaction IDs are unique integers.
*   Node IDs in a transaction are valid (between 1 and N).
*   The number of nodes involved in a transaction can vary.

**Judging Criteria:**

The solution will be judged based on:

*   **Correctness:**  Ensuring ACID properties for all transactions, even in the presence of node failures and message loss/delay.
*   **Robustness:**  Handling various failure scenarios gracefully.
*   **Performance:**  Minimizing transaction latency and maximizing throughput.
*   **Code Quality:**  Clarity, maintainability, and adherence to good coding practices.

This problem requires a deep understanding of distributed systems concepts, concurrency, and error handling. Good luck!
