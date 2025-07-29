## The Byzantine Fault Tolerance Network

### Question Description

You are tasked with designing and implementing a Byzantine Fault Tolerance (BFT) network in a distributed system. This network comprises `n` nodes, where `n = 3f + 1`, and `f` represents the maximum number of faulty nodes the system can tolerate. The nodes communicate with each other to reach a consensus on a sequence of operations.

The system operates in discrete rounds. In each round, a designated "leader" proposes a new operation to be added to the sequence. The other nodes, called "replicas", must then agree on whether to accept or reject this proposal. Faulty nodes may exhibit arbitrary behavior, including sending incorrect messages, refusing to send messages, or colluding to disrupt the consensus process.

Your goal is to implement a simplified version of the Practical Byzantine Fault Tolerance (PBFT) protocol, focusing on the core message exchange and consensus logic. The protocol will consist of three phases: **Pre-prepare, Prepare, and Commit**.

**Simplified PBFT Protocol:**

1.  **Pre-prepare:** The leader proposes an operation to all replicas. The leader's proposal includes:

    *   A sequence number (`seqNo`) that is incremented for each new operation.
    *   A view number (`viewNo`) representing the current leader election term.
    *   The operation itself (`operation`).
    *   A message digest (`digest`) of the operation.

    The leader sends a `PRE-PREPARE` message containing these fields to all replicas.

2.  **Prepare:** Upon receiving a valid `PRE-PREPARE` message from the leader, a replica broadcasts a `PREPARE` message to all other nodes (including the leader). The `PREPARE` message includes the same `seqNo`, `viewNo`, and `digest` as the `PRE-PREPARE` message. A replica only sends `PREPARE` message if the `PRE-PREPARE` message is valid (correct digest).

3.  **Commit:** If a replica receives `2f` valid `PREPARE` messages (including its own) for the same `seqNo`, `viewNo`, and `digest`, it broadcasts a `COMMIT` message to all other nodes.

4.  **Consensus:** A replica considers the operation committed when it receives `2f + 1` valid `COMMIT` messages (including its own) for the same `seqNo`, `viewNo`, and `digest`.

**Constraints:**

*   **Fault Tolerance:** Your solution must tolerate up to `f` faulty nodes.
*   **Sequence Number:** The sequence number must increment for each operation proposed by the leader.
*   **View Number:** The view number represents the current leader election term and should start from 0.
*   **Message Integrity:** Each node should verify the message digest before accepting a proposal.
*   **Efficiency:** Minimize the number of messages required for each consensus round. Specifically, the number of network messages should be limited.
*   **Leader Election:** Assume a static leader for simplicity. Node 0 is always the leader.
*   **Network Simulation:** You will be provided with a basic network simulation framework. You need to correctly implement the BFT protocol logic within this framework.
*   **Byzantine Behavior:** Do not attempt to detect or isolate faulty nodes. Your goal is to ensure the network reaches consensus despite their presence. The test cases will simulate the actions of the faulty nodes.
*   **No External Libraries:** You are not allowed to use any external libraries beyond the standard Go library.
*   **Single Proposal per Round:** Only consider one proposal per round. Once a proposal is committed or discarded due to timeout, a new round starts with a new proposal.

**Input:**

Your code will be executed within a simulated network environment. The input will consist of a series of operations proposed by the leader.

**Output:**

Your code should output the sequence of committed operations in the order they were agreed upon.
Each node should independently arrive at the same committed sequence.

**Challenge:**

The primary challenge lies in implementing the PBFT protocol correctly and efficiently, handling potential message delays, and ensuring consensus even in the presence of Byzantine faults. Consider the edge cases and potential race conditions that may arise in a distributed environment. Pay close attention to message validation, sequence number management, and the threshold conditions for the Prepare and Commit phases. Optimization is crucial for achieving the best performance within the constraints of the simulated network.
