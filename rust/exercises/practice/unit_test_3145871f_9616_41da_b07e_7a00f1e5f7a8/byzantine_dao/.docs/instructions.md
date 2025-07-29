## Problem: Decentralized Autonomous Organization (DAO) Simulation with Byzantine Fault Tolerance

**Description:**

You are tasked with building a simplified simulation of a Decentralized Autonomous Organization (DAO) operating in a network that may experience Byzantine faults.  A Byzantine fault occurs when a node in the network acts maliciously or experiences a failure, sending incorrect or conflicting information to other nodes. Your DAO needs to reach consensus on proposals despite the presence of potentially faulty nodes.

**System Architecture:**

*   **Nodes:** The DAO consists of `N` nodes, where `N` is a configurable parameter. Each node has a unique ID from `0` to `N-1`.
*   **Proposals:** Proposals are submitted to the DAO for a vote. A proposal is represented as a string.
*   **Rounds:** The consensus process proceeds in rounds. Each round involves several phases.
*   **Message Passing:** Nodes communicate by sending messages to each other.  Message delivery is assumed to be reliable (no message loss), but message content can be corrupted by faulty nodes.
*   **Byzantine Faults:** Up to `f` nodes may be Byzantine faulty, where `f < N/3`.  Faulty nodes can do anything to disrupt the consensus process, including sending incorrect votes, colluding with other faulty nodes, or refusing to participate.

**Consensus Protocol (Simplified Byzantine Fault Tolerance - pBFT):**

Implement a simplified version of pBFT with the following phases in each round:

1.  **Propose:** One node is designated as the "leader" for the round. The leader proposes a new proposal. The leader is determined by the formula `leader = round_number % N`. The leader sends the proposal to all other nodes.
2.  **Pre-prepare:**  Upon receiving a proposal from the leader, a node checks if it has already seen a proposal for this round. If not, it accepts the proposal and sends a PRE-PREPARE message containing the proposal and the round number to all other nodes.
3.  **Prepare:** Upon receiving a PRE-PREPARE message, a node checks the validity of the message (correct format, round number). If valid, it sends a PREPARE message to all other nodes. A node is considered to be in a "prepared" state for the proposal if it has:
    *   Received a valid PRE-PREPARE message for the proposal from the leader.
    *   Received `2f` valid PREPARE messages from different nodes (including itself) for the same proposal and round.
4.  **Commit:** If a node is in the "prepared" state for a proposal, it sends a COMMIT message to all other nodes.
5.  **Decide:** A node "decides" on a proposal if it has:
    *   Been in the "prepared" state for the proposal.
    *   Received `2f + 1` valid COMMIT messages from different nodes (including itself) for the same proposal and round.

**Requirements:**

1.  **Correctness:**  Non-faulty nodes must eventually reach a consensus on a proposal. If no proposal can achieve consensus within a maximum number of rounds (`MAX_ROUNDS`), the nodes should decide on a null proposal ("").
2.  **Safety:**  Non-faulty nodes must not decide on different proposals in the same round.
3.  **Liveness:**  Non-faulty nodes should eventually decide on a proposal or the null proposal.
4.  **Fault Tolerance:**  The system must be able to tolerate up to `f < N/3` Byzantine faulty nodes.
5.  **Optimization:** Minimize communication overhead and computational complexity. Prioritize message processing efficiency.

**Input:**

*   `N`: The number of nodes in the DAO (e.g., `N = 10`).
*   `f`: The number of potentially faulty nodes (e.g., `f = 2`).  Ensure `f < N/3`.
*   A stream of proposals (strings).

**Output:**

For each proposal in the stream, your program should output the proposal that the non-faulty nodes decide on. If no consensus is reached within `MAX_ROUNDS` rounds, output "".

**Constraints:**

*   `3 <= N <= 100`
*   `0 <= f < N/3`
*   The maximum length of a proposal string is 100 characters.
*   `MAX_ROUNDS` is a constant defined as 10.
*   Message passing is reliable, but message content can be corrupted by faulty nodes. You do not need to implement message retransmission or ordering. You *do* need to validate message content.
*   You are free to simulate the Byzantine behavior to prove your BFT implementation is working.

**Challenge:**

Implement the DAO simulation with the pBFT consensus protocol in Rust, adhering to the specified requirements and constraints.  Pay close attention to message validation, state management, and handling potential Byzantine behavior to ensure the correctness, safety, and liveness of the system. Consider the trade-offs between different data structures and algorithms to optimize performance. The primary challenge lies in effectively handling potentially malicious nodes without knowing *which* nodes are faulty. Good luck!
