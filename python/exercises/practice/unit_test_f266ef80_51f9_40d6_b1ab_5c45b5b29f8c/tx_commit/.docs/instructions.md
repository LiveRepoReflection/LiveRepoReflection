Okay, here's a challenging problem description designed for a high-level programming competition:

**Problem Title:** Distributed Transaction Commit Protocol Simulation

**Problem Description:**

You are tasked with simulating a simplified version of a distributed transaction commit protocol across a cluster of nodes. The goal is to ensure atomicity – either all nodes commit the transaction, or none do.

The system consists of `N` nodes (numbered 1 to N), and a central coordinator. Each node initially holds a 'vote' – either "Commit" or "Abort". The coordinator initiates the transaction and orchestrates the commit process.

The simulation proceeds in rounds. In each round, the coordinator performs the following actions:

1.  **Request Phase:** The coordinator sends a "Prepare" message to a subset of the nodes. A "Prepare" message asks the node to promise to either commit or abort the transaction based on its initial vote.
2.  **Vote Collection:** The coordinator collects the votes from the nodes that received the "Prepare" message. If a node votes "Commit", it enters a "Prepared" state, meaning it is ready to commit if instructed. If a node votes "Abort", or if it doesn't respond to the "Prepare" message within a given timeout (simulated by node not included in the subset), it is considered an "Aborted" state.
3.  **Decision Phase:**  Based on the collected votes, the coordinator makes a global decision:
    *   If *all* responding nodes voted "Commit," the coordinator decides to "Commit."
    *   If *any* responding node voted "Abort," or a timeout occurred, the coordinator decides to "Abort."
4.  **Commit/Abort Phase:** The coordinator sends a "Commit" or "Abort" message to *all* nodes (regardless of whether they participated in the vote collection).
5.  **Node Action:** Upon receiving the coordinator's decision:
    *   Nodes in the "Prepared" state *must* follow the coordinator's decision (commit if the decision is "Commit," abort if the decision is "Abort").
    *   Nodes in the "Aborted" state *must* remain in the aborted state (regardless of the coordinator's decision). The coordinator doesn't know if aborted.
    *   Nodes that never received a "Prepare" message can either commit or abort (they are considered to be in an "Uncertain" state").

**Input:**

*   `N`: The number of nodes (1 <= N <= 100).
*   `initial_votes`: A list of N strings, where each string is either "Commit" or "Abort", representing the initial vote of each node.
*   `rounds`: A list of lists representing the rounds of the simulation. Each inner list contains the indices (1-indexed) of the nodes that receive a "Prepare" message in that round.
*   `coordinator_decision`: A list of strings representing the decisions the coordinator will make in each round of the vote collection phase ("Commit" or "Abort"). These are hypothetical decisions, you should follow the protocol and make the decision yourself based on the votes you collected.

**Output:**

A list of N strings, representing the final state of each node after all rounds are executed. The possible states are: "Commit", "Abort", or "Uncertain".

**Constraints:**

*   The simulation must correctly implement the described commit protocol.
*   The coordinator must make the correct decision based on the received votes in each round.
*   Nodes must follow the protocol rules for transitioning between states.
*   The solution must be efficient enough to handle a large number of rounds (up to 100) and a moderate number of nodes.
*   You should simulate the protocol, not derive a final state based on the input.

**Example:**

Let's say `N = 3`, `initial_votes = ["Commit", "Commit", "Abort"]`, `rounds = [[1, 2], [2, 3]]` and `coordinator_decision = ["Commit", "Commit"]`.

1.  **Round 1:** The coordinator sends "Prepare" to nodes 1 and 2.  Both vote "Commit". The coordinator's decision in this hypothetical case is "Commit". The coordinator sends "Commit" to all nodes. Nodes 1 and 2 commit. Node 3 remains "Abort".
2.  **Round 2:** The coordinator sends "Prepare" to nodes 2 and 3. Node 2 votes "Commit", Node 3 is already in "Abort" state and remains in "Abort" state. The coordinator's decision in this hypothetical case is "Abort". The coordinator sends "Abort" to all nodes. Node 2 is in "Prepared" state and must abort. Node 3 remains in "Abort" state. Node 1 has already committed.

The final output would be: `["Commit", "Abort", "Abort"]`.

**Judging Criteria:**

The solution will be judged based on correctness (passing all test cases) and efficiency.  Test cases will include scenarios with different numbers of nodes, various initial votes, complex round patterns, and edge cases.

This problem requires careful attention to detail, correct implementation of the protocol logic, and efficient handling of node states.  It combines aspects of distributed systems and algorithm design. Good luck!
