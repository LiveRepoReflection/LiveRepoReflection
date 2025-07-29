## Project Name

`Distributed Consensus Simulator`

## Question Description

You are tasked with building a simplified distributed consensus simulator in Rust. The simulator will model a network of nodes attempting to agree on a single value (e.g., a transaction, a configuration change). The core of the problem lies in implementing a simplified version of the Raft consensus algorithm.

**Simplified Raft Assumptions:**

*   **Single Term:** The simulation will run for a single "term." There will be an election, and a leader will be chosen.
*   **No Log Replication:** The leader only needs to commit one single value. Log replication, heartbeats, and complex leader election scenarios (e.g., split votes, pre-votes) are not required.
*   **Basic Safety:** Ensure that once a value is committed by a majority of the nodes, no other value can be committed.
*   **Asynchronous Network:** Communication between nodes is asynchronous and unreliable. Messages can be lost or delayed.
*   **Fixed Number of Nodes:** The number of nodes in the cluster is fixed at the beginning of the simulation.
*   **No Node Failure:** Nodes do not fail during the simulation.

**Your Task:**

1.  **Node Structure:** Define a `Node` struct that represents a single node in the cluster. It should include:
    *   A unique ID.
    *   The current state of the node (Leader, Follower, Candidate).
    *   The value it has voted for (initially `None`).
    *   The term it is in.
    *   A channel for receiving messages.
    *   A channel for sending messages.
    *   A committed value option.
2.  **Message Types:** Define the message types that nodes will exchange:
    *   `RequestVote`: Sent by candidates to request votes. Contains the candidate's ID and term.
    *   `GrantVote`: Sent by followers to grant or deny a vote. Contains the follower's ID, term, and whether the vote was granted.
    *   `ProposeValue`: Sent by the leader to propose a value to be committed. Contains the value and term.
    *   `AcknowledgeValue`: Sent by followers to acknowledge the proposed value. Contains the follower's ID, term, and value.
3.  **Simulation Driver:** Implement a function `simulate(num_nodes: usize, network_delay_ms: u64) -> Option<u64>` that simulates the consensus process.
    *   `num_nodes`: The number of nodes in the cluster.
    *   `network_delay_ms`: A simulated network delay (in milliseconds). Use `thread::sleep` to simulate network latency. This delay should be randomized to add to the difficulty.
    *   The function should return `Some(value)` if a value is successfully committed by a majority of nodes, and `None` otherwise (e.g., no leader elected in the single term).
4.  **Raft Logic:** Implement the core Raft logic within each node:
    *   **Election:** Nodes start as Followers. If a Follower doesn't receive a message within a timeout (randomized), it becomes a Candidate and starts an election by sending `RequestVote` messages to all other nodes.
    *   **Voting:** Followers vote for the first Candidate they hear from in a term.  They only vote once per term.
    *   **Leader Election:** If a Candidate receives votes from a majority of nodes, it becomes the Leader.
    *   **Value Proposal:** The Leader proposes a value (e.g., a random number) by sending `ProposeValue` messages to all Followers.
    *   **Commitment:** A value is considered committed when the Leader receives `AcknowledgeValue` messages from a majority of nodes.
5.  **Concurrency:** Use Rust's concurrency features (e.g., `tokio`, `async/await`, `mpsc` channels) to simulate the asynchronous communication between nodes. Nodes should run in separate tasks.

**Constraints:**

*   The simulation must complete within a reasonable time (e.g., 10 seconds).
*   The solution must handle message loss and delays.
*   The solution must be data-race-free.
*   The solution should demonstrate that a majority of nodes agree on a single value and that this value is returned by the `simulate` function.
*   Implement collision/retry logic.
*   Implement random backoff logic.

**Optimization (for extra challenge):**

*   Minimize the number of messages exchanged to reach consensus.
*   Reduce the simulation time.
*   Make the simulation robust to different network conditions (e.g., varying delays, higher message loss rates).

This problem requires a strong understanding of distributed systems concepts, concurrency, and Rust's asynchronous programming model. It will challenge candidates to design and implement a robust and efficient consensus algorithm simulation.
