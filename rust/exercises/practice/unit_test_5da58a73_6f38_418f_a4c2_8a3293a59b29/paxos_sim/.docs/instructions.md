Okay, here's a challenging Rust coding problem designed to be at a difficulty level comparable to LeetCode Hard.

### Project Name

`Distributed Consensus Simulator`

### Question Description

You are tasked with building a simplified simulator for a distributed consensus algorithm. The system consists of `N` nodes, where `N` can be a large number (up to 10,000). Each node maintains a local state represented by an integer. The goal is to implement a consensus protocol that ensures all nodes eventually agree on the same state, even in the presence of certain failures.

**Specifically, you need to simulate a simplified version of Paxos with the following constraints:**

1.  **Nodes:** Each node is identified by a unique integer ID from 0 to N-1.
2.  **State:** Each node initially has a random integer as its local state.
3.  **Rounds:** The consensus process proceeds in discrete rounds.
4.  **Propose:** In each round, a randomly selected node (the *leader* for that round) proposes its current state as the new consensus value.
5.  **Accept/Reject:** Each other node *independently* decides whether to accept or reject the proposed value.  A node accepts with probability `accept_probability` and rejects otherwise. This probability is a floating-point number between 0.0 and 1.0.
6.  **Update:** If a majority (strictly more than N/2) of nodes accept the proposal, *all* nodes update their local state to the proposed value.
7.  **Termination:** The simulation runs for a maximum of `max_rounds`.  The simulation is considered successful if all nodes have the same state after any round. The simulation can also be considered successful if all nodes have the same state before `max_rounds` has been reached.

**Faults:**  A certain percentage of nodes (`fault_percentage`) can be *Byzantine* (malicious). Byzantine nodes behave unpredictably. Specifically:
   *   A Byzantine node can propose any integer value, regardless of its local state.
   *   A Byzantine node can accept or reject any proposal, regardless of its local state.
   *   Byzantine nodes can even collude to try to prevent the system from reaching consensus.

**Requirements:**

*   Implement the simulation logic in Rust.
*   The simulation must run efficiently, even with a large number of nodes (N=10,000) and a large number of rounds.
*   Your implementation should be deterministic, meaning given the same seed, N, accept probability, fault percentage, max rounds, and initial states, the result should always be the same.
*   The simulation should handle edge cases gracefully, such as:
    *   Zero nodes (N=0).
    *   `accept_probability` of 0.0 or 1.0.
    *   `fault_percentage` of 0.0 or 1.0.
*   Your code must be well-structured, readable, and maintainable.  Use appropriate data structures and algorithms.
*   You are free to use any standard Rust libraries.

**Input:**

*   `N`: The number of nodes (usize).
*   `accept_probability`: The probability that a node will accept a proposal (f64).
*   `fault_percentage`: The percentage of nodes that are Byzantine (f64).  For example, 0.1 represents 10% Byzantine nodes.
*   `max_rounds`: The maximum number of rounds to run the simulation (usize).
*   `seed`: The random seed to use for the simulation (u64).
*   `initial_states`: A vector of `N` integers representing the initial state of each node (Vec\<i64>).

**Output:**

*   A boolean indicating whether the simulation reached consensus (true) or not (false) within `max_rounds`.

**Constraints:**

*   0 <= N <= 10,000
*   0.0 <= `accept_probability` <= 1.0
*   0.0 <= `fault_percentage` <= 1.0
*   1 <= `max_rounds` <= 1,000
*   Initial states can be any i64

**Example:**

If N = 5, `accept_probability` = 0.8, `fault_percentage` = 0.2, `max_rounds` = 10, `seed` = 12345, and `initial_states` = \[1, 2, 1, 2, 1], the simulation might reach consensus (all nodes have the same state) after a few rounds.

**Grading Criteria:**

*   **Correctness:** Your code must produce the correct output for all valid inputs.
*   **Efficiency:** Your code must run efficiently, even with a large number of nodes and rounds.
*   **Robustness:** Your code must handle edge cases gracefully.
*   **Code Quality:** Your code must be well-structured, readable, and maintainable.
*   **Determinism:** Your code must provide deterministic output given the same input parameters

This problem requires careful consideration of algorithm design, data structures, and optimization to achieve a correct and efficient solution. Good luck!
