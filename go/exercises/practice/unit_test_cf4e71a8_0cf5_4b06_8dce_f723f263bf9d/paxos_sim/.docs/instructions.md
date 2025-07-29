## Project Name:

`Distributed Consensus Simulator`

## Question Description:

You are tasked with building a simplified simulator for a distributed consensus algorithm, specifically Paxos. The goal is to simulate the core steps of Paxos: Proposal, Acceptance, and Learning, within a network of nodes that may experience failures and message delays.

**System Setup:**

*   **Nodes:** The system consists of *N* nodes, each uniquely identified by an integer from 0 to *N*-1. These nodes can act as Proposers, Acceptors, and Learners.
*   **Network:** The network is unreliable. Messages between nodes can be delayed or lost. You do not need to simulate message corruption.
*   **Value:** Nodes are trying to agree on a single value. This value can be represented as an integer.
*   **Rounds:** The consensus process happens in multiple rounds. Each round has a unique proposal number.

**Core Paxos Steps (Simplified):**

1.  **Proposal:**
    *   A Proposer generates a new proposal number higher than any it has seen before.  A simple way to achieve this is to increment a counter.
    *   The Proposer sends a "Prepare" message to a quorum of Acceptors (more than half of the nodes). The "Prepare" message includes the proposal number.

2.  **Acceptance:**
    *   When an Acceptor receives a "Prepare" message with a proposal number higher than any it has previously seen, it promises not to accept any proposals with lower numbers. It also sends a "Promise" message back to the Proposer, including the highest-numbered proposal it *has* accepted so far (if any) and the corresponding accepted value. If the Acceptor has not accepted any value before, it should return null value.
    *   If an Acceptor receives a "Prepare" message with a proposal number *lower* than or equal to any it has previously seen, it rejects the proposal and sends a "Reject" message back to the Proposer.

3.  **Value Selection & Acceptance Request:**
    *   If the Proposer receives "Promise" messages from a quorum of Acceptors, it selects a value to propose:
        *   If any "Promise" messages included a previously accepted value, the Proposer chooses the value from the "Promise" with the highest proposal number. This ensures that the chosen value reflects the most recent accepted value.
        *   If none of the "Promise" messages included a previously accepted value, the Proposer chooses its own initial value.
    *   The Proposer sends an "Accept" message to a quorum of Acceptors, including the proposal number and the chosen value.

4.  **Acceptance Confirmation:**
    *   When an Acceptor receives an "Accept" message with a proposal number higher than or equal to any it has previously seen, it accepts the value and sends an "Accepted" message to all Learners. It also updates its highest seen proposal number.
    *   If an Acceptor receives an "Accept" message with a proposal number *lower* than any it has previously seen, it ignores the message.

5.  **Learning:**
    *   Learners listen for "Accepted" messages from Acceptors. Once a Learner has received "Accepted" messages from a quorum of Acceptors for the same value, it considers that value to be the consensus value.

**Requirements:**

*   Implement the node behavior as a state machine that reacts to incoming messages.
*   Simulate network unreliability: Introduce random message delays and message loss. The probability of message loss and the maximum message delay should be configurable.
*   Simulate node failures: Nodes can crash and recover. A crashed node stops processing messages and loses its in-memory state (e.g., current proposal number, promised proposal number, accepted value). Upon recovery, it restarts with no prior knowledge.
*   Implement a mechanism for nodes to determine when consensus has been reached (at least locally).
*   Provide a method to inject a new value into a node acting as a Proposer.

**Constraints:**

*   The number of nodes *N* will be between 3 and 9 inclusive.
*   Implement a timeout mechanism to prevent indefinite blocking due to message loss or node failures.  Proposers should give up on a proposal if they don't receive a quorum of promises or acceptances within a reasonable time.
*   The system should eventually reach consensus even with message loss, delays, and node failures.
*   Optimize for fault tolerance. The system should remain functional as long as a majority of Acceptors are alive and responsive.
*   The simulator should log important events (e.g., message sent, message received, value accepted, node crash, node recovery) for debugging and analysis.
*   The solution should be concurrent and utilize Go's concurrency primitives (goroutines, channels, mutexes) effectively.

**Evaluation Criteria:**

*   Correctness: Does the system eventually reach consensus on a single value?
*   Fault Tolerance: How well does the system handle message loss, delays, and node failures?
*   Efficiency: Is the system responsive and efficient in reaching consensus?
*   Code Quality: Is the code well-structured, readable, and maintainable?  Is concurrency handled safely?
*   Completeness: Has all the specified functionality been implemented?
*   Scalability: While not the primary focus, consider how the design might scale to a larger number of nodes.

This problem requires a strong understanding of distributed systems concepts, concurrency, and Go's programming language features. Successful solutions will demonstrate a robust and well-designed implementation of a distributed consensus simulator.
