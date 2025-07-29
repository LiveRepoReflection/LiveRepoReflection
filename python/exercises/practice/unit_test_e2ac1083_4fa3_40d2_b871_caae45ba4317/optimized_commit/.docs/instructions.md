## Problem: Optimizing Distributed Transaction Commit

**Description:**

You are designing a distributed database system. A crucial component is ensuring the atomicity of transactions that span multiple nodes. You've implemented a two-phase commit (2PC) protocol, but it's experiencing performance bottlenecks due to network latency and contention, especially under high transaction load.

Your task is to implement a more efficient and resilient transaction commit protocol.  You are given a system with `N` nodes. Each transaction involves a subset of these nodes. The transaction coordinator initiates the 2PC protocol.

**Input:**

*   `N`: The number of nodes in the system (1 <= N <= 1000). Nodes are identified by integers 0 to N-1.
*   `transactions`: A list of transactions. Each transaction is a tuple/list containing:

    *   `coordinator_id`: The ID of the node acting as the coordinator for this transaction (0 <= coordinator\_id < N).
    *   `participants`: A set of node IDs involved in the transaction (each ID is between 0 and N-1, inclusive).  A node can be the coordinator and a participant in the same transaction. Participants always include the coordinator.
    *   `commit_probability`: The probability that the transaction will commit (0.0 <= commit\_probability <= 1.0). This is precomputed based on factors irrelevant to the commit protocol itself.

**Requirements:**

Implement a function `optimize_commit_protocol(N, transactions)` that returns the optimized total latency.

1.  **Protocol Selection:** For each transaction, you can choose between two commit protocols:
    *   **Standard 2PC:** The coordinator sends a PREPARE message to all participants. Each participant responds with a VOTE\_COMMIT or VOTE\_ABORT message. If all participants vote to commit, the coordinator sends a COMMIT message to all participants; otherwise, it sends an ABORT message.
    *   **Probabilistic Commit (PC):**  The coordinator sends a PREPARE message only to a randomly selected subset of participants, such that the expected number of participants is equal to the commit_probability times the total number of participants. Each participant responds as in standard 2PC. If all selected participants vote to commit, the coordinator sends a COMMIT message to *all* participants; otherwise, it sends an ABORT message. If the transaction aborts, all nodes involved discard the transaction.

2.  **Latency Model:** The latency between any two nodes is 1 unit. The latency of sending a message to multiple nodes is the maximum of the individual latencies. Sending a message back is assumed to have the same latency as sending the message.

3.  **Optimization Goal:** Minimize the *expected total latency* across all transactions. The expected latency of a single transaction is the sum of the products of the probabilities of each outcome (commit or abort) and the latency of that outcome.

4.  **Constraints:**
    *   Your solution must be efficient. Naive solutions with high time complexity will time out. Consider dynamic programming or other optimization techniques.
    *   The choice of protocol (2PC or PC) for each transaction must be made independently.

**Example:**

```python
N = 3
transactions = [
    (0, {0, 1, 2}, 0.9),  # Coordinator 0, participants 0, 1, 2, commit probability 0.9
    (1, {1, 2}, 0.5),      # Coordinator 1, participants 1, 2, commit probability 0.5
]

optimized_latency = optimize_commit_protocol(N, transactions)
print(optimized_latency) # Expected output should be close to 9.45 (but could vary slightly due to the probabilistic nature).
```

**Explanation of Example:**

For the first transaction:
*   **Standard 2PC:** Latency = PREPARE (1) + VOTE (1) + COMMIT/ABORT (1) = 3.
*   **Probabilistic Commit:** Expected number of PREPARE messages = 0.9 * 3 = 2.7. Let us approximate this by sending PREPARE messages to two participants.
    *   Commit (probability 0.9): Latency = PREPARE (1) + VOTE (1) + COMMIT (1) = 3.
    *   Abort (probability 0.1): Latency = PREPARE (1) + VOTE (1) + ABORT (1) = 3.
    So the transaction latency is 3.

For the second transaction:
*   **Standard 2PC:** Latency = PREPARE (1) + VOTE (1) + COMMIT/ABORT (1) = 3.
*   **Probabilistic Commit:** Expected number of PREPARE messages = 0.5 * 2 = 1. Let us approximate this by sending PREPARE messages to one participant.
    *   Commit (probability 0.5): Latency = PREPARE (1) + VOTE (1) + COMMIT (1) = 3.
    *   Abort (probability 0.5): Latency = PREPARE (1) + VOTE (1) + ABORT (1) = 3.
    So the transaction latency is 3.

Total latency = 3 + 3 = 6. However, since PC has a probabilistic nature, the number of participants and hence the latency can change. With standard 2PC, latency is 3+3 = 6.
With PC, expected latency will reduce since the latency is multiplied by the probability of commit/abort.

**Note:**  This problem requires careful calculation of expected latencies and a strategy to choose the optimal protocol for each transaction to minimize the overall expected latency. The probabilistic nature of the PC protocol and the need for efficient computation make it challenging.
