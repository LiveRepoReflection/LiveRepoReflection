## Problem: Distributed Consensus Simulation with Byzantine Fault Tolerance

**Description:**

You are tasked with simulating a distributed system attempting to achieve consensus in the presence of Byzantine faults.  The system consists of `N` nodes, where `F` of these nodes are potentially malicious (Byzantine).  The goal is for all non-faulty nodes to agree on a single value (0 or 1) despite the potentially misleading or arbitrary behavior of the faulty nodes.

You will implement a simplified version of a practical Byzantine Fault Tolerance (pBFT) consensus algorithm.  The simulation will run in a series of rounds. In each round, a leader node is selected (round-robin fashion). The leader proposes a value.  Then, the nodes communicate to decide on a final value for that round.

**Details:**

1.  **Nodes:** Each node is identified by a unique integer from 0 to `N-1`. Node 0 is the first leader, node 1 is the leader in the second round, and so on, wrapping around after node `N-1`.

2.  **Byzantine Nodes:** You are given a list of node IDs that are Byzantine.  Byzantine nodes can do *anything* to disrupt the consensus process: they can send different messages to different nodes, send incorrect values, not send messages at all, collude, etc.

3.  **Rounds:** The simulation consists of `R` rounds.

4.  **Communication:**  Nodes communicate by sending messages to each other.  You will implement a simplified messaging system. The messages are simple integers representing either votes for 0, votes for 1, or a proposed initial value.

5.  **Consensus Mechanism:** Implement the following simplified pBFT-like mechanism:
    *   **Proposal:** The leader for the current round proposes a value (0 or 1).
    *   **Pre-prepare:** The leader sends the proposed value to all other nodes (including Byzantine nodes).
    *   **Prepare:**  Each node (that receives a proposal) sends a "prepare" message to all other nodes, indicating their acceptance of the proposal.  A Byzantine node *can* choose to send different "prepare" messages to different nodes or not send any.
    *   **Commit:** Each node (that receives enough "prepare" messages) sends a "commit" message to all other nodes, indicating their commitment to the proposal. A Byzantine node can behave arbitrarily.
    *   **Decision:**  A non-faulty node decides on a value if it receives "commit" messages from more than `2F` nodes, where `F` is the number of faulty nodes. The value decided is the value that was initially proposed.

6.  **Fault Tolerance:** The system should tolerate up to `F` Byzantine faults, where `N > 3F`.

7.  **Input:**

    *   `N`: The total number of nodes in the system.
    *   `F`: The maximum number of Byzantine nodes.
    *   `byzantine_nodes`: A list of integers representing the IDs of the Byzantine nodes.
    *   `R`: The number of rounds to simulate.
    *   `initial_values`: A list of length `N`, where each element represents the initial value (0 or 1) that each *non-faulty* node will vote for if it doesn't receive a proposal from the leader. Byzantine nodes' initial values do not matter.

8.  **Output:**

    *   A list of length `N`, where each element represents the final decision of each node after `R` rounds. If a node fails to reach a decision in a round, it defaults to its initial value for that round.

**Constraints:**

*   `3 * F < N <= 100`
*   `0 <= F < N`
*   `1 <= R <= 100`
*   `initial_values` contains only 0 or 1.
*   Byzantine nodes can behave arbitrarily.  You do *not* know how they will behave beforehand. You must design your algorithm to be resilient to any possible behavior of the Byzantine nodes.
*   The core logic around sending and receiving messages must be efficient enough to handle the given constraints. Avoid unnecessary loops or complex data structures.

**Challenge:**

The main challenge is to implement the consensus mechanism in a way that ensures correctness and resilience to arbitrary Byzantine behavior.  You must carefully consider how to handle potentially conflicting messages, missing messages, and malicious attempts to disrupt the consensus process. Optimizing your message processing to avoid exceeding time limits will also be crucial.
