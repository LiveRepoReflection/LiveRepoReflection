Okay, here's a challenging Go coding problem designed to test a candidate's skills with graph algorithms, concurrency, and optimization.

**Problem: Distributed Transaction Commit Protocol Simulator**

**Description:**

You are tasked with implementing a simplified simulator for a distributed transaction commit protocol.  Imagine a system where multiple independent services (nodes) participate in a single transaction.  For the transaction to succeed, *all* participating nodes must agree to commit.  If even a single node fails, the entire transaction must be rolled back.

Your simulator should model a simplified version of the Two-Phase Commit (2PC) protocol.

**Here's how the simulation works:**

1.  **Nodes:** You are given a network of `N` nodes, numbered from `0` to `N-1`. Each node has a certain probability of failure (`failureProbability`) during the voting phase and during the commit/rollback phase. This is a float between 0.0 and 1.0. If a node fails during the voting phase, the transaction is aborted. If a node fails during the commit/rollback phase, its state is left in an inconsistent state, potentially leading to data corruption.

2.  **Coordinator:** Node `0` acts as the coordinator.

3.  **Transaction:** A transaction is initiated.

4.  **Voting Phase:**
    *   The coordinator sends a "prepare to commit" message to all other nodes.
    *   Each node, upon receiving the message, decides whether to vote "commit" or "abort." A node votes "abort" if it encounters a simulated error (based on its `failureProbability` for the voting phase). Otherwise, it votes "commit."
    *   Each node sends its vote back to the coordinator. These votes are sent concurrently through channels.
    *   If a node fails during the voting phase (simulated by a random event based on `failureProbability`), it does not send any message.

5.  **Decision Phase (Coordinator):**
    *   The coordinator waits to receive votes from all participating nodes (excluding itself).
    *   If *any* node votes "abort" or if the coordinator does not receive a vote from a node after a specified `timeoutDuration` (in milliseconds), the coordinator decides to "abort" the transaction.
    *   If all nodes vote "commit" and the coordinator receives all votes within the timeout, the coordinator decides to "commit" the transaction.

6.  **Commit/Rollback Phase:**
    *   The coordinator sends either a "commit" or "rollback" message to all other nodes, based on its decision.
    *   Each node, upon receiving the message, performs the corresponding action (commit or rollback). Each node has its own `failureProbability` for the commit/rollback phase.
    *   If a node fails during this phase (simulated by a random event based on `failureProbability`), it does *not* complete the commit or rollback, resulting in an inconsistent state.

**Input:**

*   `N`:  The number of nodes in the network (an integer, e.g., 5, 10, 100).
*   `failureProbabilities`: A slice of floats, where `failureProbabilities[i]` represents the failure probability of node `i` during both the voting and commit/rollback phases. The length of the slice must be equal to `N`.
*   `timeoutDuration`: The timeout duration (in milliseconds) that the coordinator will wait for votes before aborting the transaction (an integer, e.g., 100, 500, 1000).

**Output:**

*   A string representing the final state of the system after the transaction simulation.  The string should be formatted as follows:
    ```
    "Node 0: Committed|Aborted|Undecided, Node 1: Committed|Aborted|Undecided, ..., Node N-1: Committed|Aborted|Undecided"
    ```

    *   `Committed`: The node successfully committed the transaction.
    *   `Aborted`: The node successfully rolled back the transaction.
    *   `Undecided`:  The node failed during the commit/rollback phase and is in an inconsistent state. It neither committed nor rolled back.  A node can also be in the Undecided state if the coordinator never sent it a commit/rollback message.

**Constraints:**

*   `1 <= N <= 1000`
*   `0.0 <= failureProbabilities[i] <= 1.0` for all `i`.
*   `1 <= timeoutDuration <= 5000` (milliseconds)
*   You *must* use goroutines and channels to simulate the concurrent behavior of the nodes.
*   The simulation must be realistic, meaning the failure probabilities should be properly respected.
*   The solution should be efficient. Avoid unnecessary locking or blocking operations. Aim for good concurrency.

**Challenge:**

This problem requires careful consideration of concurrency, error handling, and edge cases. Simulating failures reliably and handling timeouts gracefully are crucial.  The optimization aspect lies in ensuring the simulation runs efficiently, even with a large number of nodes. The difficulty comes from correctly managing concurrency, simulating failures and correctly determining the final state of each node.
