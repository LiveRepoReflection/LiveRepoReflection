## Problem: Distributed Consensus Simulation

**Question Description:**

You are tasked with simulating a distributed consensus algorithm in a network of nodes. The algorithm aims to achieve agreement on a single, immutable log of events. Due to network unreliability and potential Byzantine faults (nodes behaving maliciously or experiencing failures), achieving consensus is challenging.

**Network Model:**

*   The network consists of `n` nodes, where `n` is a positive integer. Each node has a unique ID from `0` to `n-1`.
*   Nodes communicate via asynchronous message passing. Messages can be delayed, duplicated, or lost. Message ordering is not guaranteed.
*   A subset of nodes (up to `f` nodes) may be Byzantine, where `f < n/3` (to ensure the possibility of consensus). Byzantine nodes can arbitrarily deviate from the protocol. Other nodes are considered honest.
*   Nodes are aware of the total number of nodes (`n`) and the maximum number of Byzantine nodes (`f`).

**Consensus Algorithm:**

Implement a simplified version of the Practical Byzantine Fault Tolerance (pBFT) consensus algorithm with the following phases:

1.  **Propose:** A designated *leader* node proposes a new event to be added to the log. The leader broadcasts the proposal to all other nodes.
2.  **Vote:** Upon receiving a proposal, each node (including the leader) *votes* for the proposal. A node can either accept the proposal ("ACCEPT") or reject it ("REJECT"). Honest nodes will vote based on a deterministic rule (described below). Nodes send their votes to all other nodes.
3.  **Commit:** If a node receives votes from at least `2f+1` nodes (including its own vote) that agree, it *commits* the event to its local log. This means appending the event to its log and marking it as committed.

**Honest Node Voting Rule:**

Honest nodes vote based on the following simple rule:

*   If the proposed event's content (a string) has a length that is a prime number, the node votes "ACCEPT".
*   Otherwise, the node votes "REJECT".

**Byzantine Node Behavior:**

Byzantine nodes can behave arbitrarily. They can:

*   Send different proposals to different nodes.
*   Send different votes to different nodes.
*   Not send any messages at all.
*   Send messages with arbitrary content.

**Task:**

Write a function `simulate_consensus(n, f, events)` that simulates the pBFT consensus algorithm for a given network configuration and a sequence of events.

*   `n`: The total number of nodes in the network (integer).
*   `f`: The maximum number of Byzantine nodes in the network (integer).
*   `events`: A list of strings, where each string represents a proposed event.

Your function should return a list of lists, where each inner list represents the final log of a node. The outer list should be ordered by node ID (i.e., the first inner list is node 0's log, the second is node 1's log, etc.). Each inner list should contain strings representing the committed events in the order they were proposed and committed. Only include events that have been committed by the node. You are allowed to make reasonable assumptions in how the network messages are passed around.

**Leader Election:** Node 0 is always the leader.

**Constraints:**

*   `3 <= n <= 10`
*   `0 <= f < n/3`
*   The event strings can have any characters.
*   The simulation should run for a fixed number of rounds (e.g., 10 rounds per event) to allow messages to propagate. You do not need to handle indefinite message delays.
*   Assume that the leader proposes events in the order they appear in the `events` list.
*   You need to implement a simple prime number checker to implement the honest node voting rule.
*   Your solution should attempt to maximize the number of events committed by honest nodes, even in the presence of Byzantine faults. While perfect consensus is not guaranteed, the algorithm should aim for agreement among honest nodes whenever possible.

**Example:**

If `n = 5`, `f = 1`, and `events = ["hello", "world", "python"]`, your function should return a list of 5 lists, where each inner list represents the final log of a node. The content of these lists will depend on the simulated behavior of the honest and Byzantine nodes. An example of an output could be:

```
[
    ["hello", "python"], # Node 0's log
    ["hello"], # Node 1's log
    ["hello", "python"], # Node 2's log
    ["hello", "python"], # Node 3's log
    ["hello", "python"]  # Node 4's log
]
```

In this example, all nodes, except node 1 agreed on "hello" and "python". The string "hello" has length 5, which is prime, so the honest nodes voted "ACCEPT".  The string "world" has length 5, which is prime, so the honest nodes voted "ACCEPT". The string "python" has length 6, which is not prime, so the honest nodes voted "REJECT". Node 1 may be byzantine, so it may have not received the event "python" or didn't agree to commit it.

**Note:** The correctness of your solution will be evaluated based on its ability to achieve consensus among honest nodes in various scenarios, including cases with Byzantine nodes exhibiting different fault patterns. The efficiency of your solution is also considered in terms of its ability to reach consensus within a reasonable number of rounds.
