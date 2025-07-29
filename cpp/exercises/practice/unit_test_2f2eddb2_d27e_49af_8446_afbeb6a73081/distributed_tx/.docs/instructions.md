Okay, here's a challenging problem description for a coding competition.

**Problem Title:**  The Distributed Transaction Coordinator

**Problem Description:**

You are tasked with designing and implementing a simplified, yet robust, distributed transaction coordinator (DTC) for a NoSQL database cluster. This cluster consists of `N` nodes (numbered from 1 to N), each holding a shard of data.  The DTC is responsible for ensuring ACID (Atomicity, Consistency, Isolation, Durability) properties for transactions that span multiple nodes.

The database uses a two-phase commit (2PC) protocol.  Your DTC needs to handle transaction requests, coordinate the voting process among nodes, and finalize the transaction outcome (commit or rollback).

**Input:**

The input consists of a series of transaction requests. Each transaction request is defined as follows:

*   `transaction_id`: A unique integer identifying the transaction.
*   `involved_nodes`: A list of integers representing the node IDs (1 to N) involved in the transaction.
*   `operations`: A list of operations to be performed within the transaction. Each operation has the following structure:
    *   `node_id`: The node on which the operation needs to be performed.
    *   `operation_type`: An integer representing the type of operation (e.g., 1 for write, 2 for read, 3 for delete).  The specifics of what these operations *do* are irrelevant for this problem; you only need to track and coordinate them.
    *   `data`:  A string representing the data associated with the operation. (Maximum length 100 characters)

The input will be provided through standard input. The first line will contain `N` (number of nodes, 1 <= N <= 100) and `M` (number of transaction requests, 1 <= M <= 1000). The following M lines will each represent a transaction, formatted as JSON. You can assume that the JSON is correctly formatted.

**Output:**

For each transaction, your DTC should output either "COMMIT" or "ROLLBACK" to standard output, indicating the final decision for that transaction. You also need to output the log of decisions made by each node (explained in the requirements).

**Requirements:**

1.  **Two-Phase Commit (2PC):** Implement the 2PC protocol.  The DTC acts as the coordinator.

    *   **Phase 1 (Prepare Phase):** The DTC sends a "PREPARE" message to all involved nodes. Each node must simulate its local vote (either "VOTE_COMMIT" or "VOTE_ABORT").  For simplicity, assume that each node *always* votes "VOTE_COMMIT" unless specifically instructed otherwise in the constraints.
    *   **Phase 2 (Commit/Rollback Phase):**
        *   If *all* nodes vote "VOTE_COMMIT", the DTC sends a "COMMIT" message to all involved nodes.
        *   If *any* node votes "VOTE_ABORT" or the DTC does not receive a response from a node within a specified timeout (see Constraints), the DTC sends a "ROLLBACK" message to all involved nodes.

2.  **Node Failure Simulation:**  Introduce the possibility of node failures during the 2PC protocol.  For a given transaction, any node can "fail" during either the Prepare Phase or the Commit/Rollback Phase. If a node fails during the Prepare Phase, the DTC should treat it as a "VOTE_ABORT". If a node fails after sending VOTE_COMMIT but before receiving the COMMIT/ROLLBACK message, it must rollback. The failed nodes are provided as input for each transaction.

3.  **Timeout Handling:** The DTC has a timeout period of `T` milliseconds (see Constraints) to receive responses from nodes during the Prepare Phase.  If a node doesn't respond within this timeout, the DTC must assume the node voted "VOTE_ABORT" and proceed with a rollback.

4.  **Transaction Logging:** Each node needs to maintain a simple log of decisions made. If a node votes to commit, it should log "PREPARED [transaction_id]". If a node receives a COMMIT message, it should log "COMMITTED [transaction_id]". If a node receives a ROLLBACK message or aborted due to node failure, it should log "ABORTED [transaction_id]". The output of the transaction log from each node should be shown in the following way:
    `Node <node_id>: [<log_entry_1>, <log_entry_2>, ...]`
    This should be printed *after* the COMMIT/ROLLBACK decision for each transaction.

5.  **Idempotency:** The DTC should be designed to handle repeated transaction requests (same `transaction_id`).  If a transaction with the same `transaction_id` has already been processed, the DTC should return the previously determined outcome (COMMIT or ROLLBACK) without re-executing the 2PC protocol, and print the log of each node as it was at the end of the previous execution.

**Constraints:**

*   `1 <= N <= 100` (Number of nodes)
*   `1 <= M <= 1000` (Number of transaction requests)
*   `1 <= node_id <= N`
*   `1 <= T <= 500` (Timeout in milliseconds) The timeout is simulated. You don't need to actually implement timing mechanisms, but you do need to check for a timeout condition given a list of nodes that timed out.
*   Node failures are provided as a list of integers. If a node `x` is in the `failed_nodes` list for a specific transaction, that node fails during that transaction. The `failed_nodes` list can be empty.
*   The `failed_nodes` list will only contain the node id that are participating in the transaction.

**Example Input:**

```json
2 2
{"transaction_id": 1, "involved_nodes": [1, 2], "operations": [{"node_id": 1, "operation_type": 1, "data": "data1"}, {"node_id": 2, "operation_type": 2, "data": "data2"}], "failed_nodes": []}
{"transaction_id": 2, "involved_nodes": [1, 2], "operations": [{"node_id": 1, "operation_type": 1, "data": "data3"}, {"node_id": 2, "operation_type": 3, "data": "data4"}], "failed_nodes": [2]}
```

**Example Output:**

```
COMMIT
Node 1: [PREPARED 1, COMMITTED 1]
Node 2: [PREPARED 1, COMMITTED 1]
ROLLBACK
Node 1: [PREPARED 2, ABORTED 2]
Node 2: [PREPARED 2, ABORTED 2]
```

**Explanation of the Example:**

*   **Transaction 1:** All nodes voted "VOTE_COMMIT", so the transaction is committed.
*   **Transaction 2:** Node 2 failed, so the transaction is rolled back. Both nodes log the abortion.

**Judging Criteria:**

*   Correctness: Your solution must correctly implement the 2PC protocol, handle node failures, and manage timeouts.
*   Efficiency: Your solution should be reasonably efficient in terms of time complexity. Avoid unnecessary computations.
*   Idempotency: Your solution must correctly handle duplicate transaction requests.
*   Code Quality: Your code should be well-structured, readable, and maintainable.
*   Logging: Your solution must correctly implement the logging mechanism.

This problem requires a good understanding of distributed systems concepts, careful attention to detail, and solid programming skills. Good luck!
