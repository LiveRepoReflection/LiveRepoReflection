Okay, here's a challenging Go coding problem designed with a focus on algorithmic complexity, performance, and real-world relevance.

**Problem Title: Distributed Transaction Consensus**

**Problem Description:**

You are designing a distributed database system.  A critical component of this system is ensuring transactional consistency across multiple nodes.  Your task is to implement a simplified consensus algorithm to determine the outcome (commit or rollback) of a distributed transaction.

The system consists of `N` nodes (numbered 0 to N-1).  Each node independently proposes an outcome for a specific transaction.  The possible outcomes are `Commit` (represented by `true`) or `Rollback` (represented by `false`).

The consensus algorithm works as follows:

1.  **Proposal Phase:** Each node proposes its desired outcome (Commit or Rollback).

2.  **Voting Phase:** Each node examines the proposals from all other nodes.  A node votes `Commit` only if *all* received proposals are also `Commit`. Otherwise, the node votes `Rollback`.

3.  **Decision Phase:** The final decision is determined by the majority vote. If more than half of the nodes (strictly greater than N/2) vote `Commit`, the transaction is committed. Otherwise, the transaction is rolled back.

**Input:**

*   `N`: An integer representing the number of nodes in the system (1 <= N <= 100,000).
*   `proposals`: A slice of booleans of length `N`, where `proposals[i]` represents the proposal of node `i`. `true` indicates a `Commit` proposal, and `false` indicates a `Rollback` proposal.

**Output:**

*   A boolean value representing the final decision of the consensus algorithm. `true` indicates `Commit`, and `false` indicates `Rollback`.

**Constraints and Requirements:**

*   **Performance:**  Your solution must be efficient.  A naive O(N^2) solution will likely time out for larger values of N. Consider using efficient data structures and algorithms to optimize performance.
*   **Error Handling:** Handle edge cases gracefully. For instance, what happens if N is 1?
*   **Concurrency:**  While you don't need to implement actual concurrent communication, consider how your solution *could* be adapted to a concurrent environment.  Think about potential race conditions and how to avoid them if nodes were truly voting concurrently.  (This aspect is primarily for conceptual consideration, not strict implementation).
*   **Optimizations:** Explore potential optimizations beyond simply reducing algorithmic complexity.  For example, can you avoid unnecessary iterations or calculations?

**Example:**

```
N = 3
proposals = [true, true, false]

Output: false  (Rollback)
```

**Explanation:**

*   Node 0 proposes `Commit` (true).
*   Node 1 proposes `Commit` (true).
*   Node 2 proposes `Rollback` (false).

Voting Phase:

*   Node 0 receives `[true, false]`. It votes `Rollback` because not all proposals are `Commit`.
*   Node 1 receives `[true, false]`. It votes `Rollback`.
*   Node 2 receives `[true, true]`. It votes `Rollback`.

Decision Phase:

*   Votes: `[false, false, false]`
*   Majority vote is `Rollback`.

**Challenge Aspects:**

*   The core algorithmic challenge is to determine how to efficiently calculate each node's vote without explicitly iterating through all other nodes' proposals for *every* node.
*   The problem mirrors a simplified version of distributed consensus problems encountered in real-world distributed systems.
*   The performance constraint forces you to think about efficient data structures and algorithms, potentially leading to clever solutions.
*   Thinking about concurrency (even without implementing it) encourages considering the practical aspects of distributed systems.
