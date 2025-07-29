## The Byzantine Resilient Multi-Paxos Simulator

### Question Description

You are tasked with building a simulator for a simplified, Byzantine-fault-tolerant version of Multi-Paxos, a distributed consensus algorithm. This simulator will model a system with `n` nodes, where up to `f` nodes can be Byzantine (i.e., behave arbitrarily, including sending incorrect or malicious messages).  Your goal is to implement the core logic that allows the honest nodes to reach consensus on a sequence of values, even in the presence of these faulty nodes.

**System Model:**

*   There are `n` nodes in the system, identified by integers from `0` to `n-1`.
*   Up to `f` nodes can be Byzantine, where `n = 3f + 1`. This ensures the system can tolerate Byzantine faults.
*   Time is divided into discrete slots. Each slot represents an opportunity for a node to propose a value and for the system to attempt to reach consensus on that value.
*   Nodes communicate via a broadcast channel.  Any node can send a message to all other nodes, and honest nodes will receive every message sent. Byzantine nodes can selectively drop or alter messages.
*   Messages can be lost or delayed, but not corrupted (unless sent by a Byzantine node).
*   The simulator needs to handle a potentially infinite stream of proposals, meaning the consensus algorithm needs to make decisions for each slot in a sequence.

**Simplified Multi-Paxos:**

The algorithm you'll simulate is a simplified version of Multi-Paxos, focusing on a single slot at a time.  For each slot, the algorithm proceeds as follows:

1.  **Propose:** Each node (honest or Byzantine) proposes a value for the current slot. Honest nodes propose their intended value. Byzantine nodes can propose any value, including different values to different nodes.
2.  **Prepare:** Each node sends a "Prepare" message containing its proposed value and the slot number to all other nodes.
3.  **Accept:** Upon receiving Prepare messages from a majority of nodes (at least `n-f` nodes), a node chooses one of the proposed values. A simple strategy is to select the value from the Prepare message with the lowest node ID. The node then sends an "Accept" message containing the chosen value and the slot number to all other nodes.
4.  **Commit:** Upon receiving Accept messages with the same value for the same slot from a majority of nodes (at least `n-f` nodes), a node commits the value for that slot.

**Your Task:**

Implement a simulator that takes as input:

*   `n`: The number of nodes in the system.
*   `f`: The maximum number of Byzantine nodes.
*   `proposals`: A list of lists. `proposals[i][j]` is the value that node `i` proposes for slot `j`. Honest nodes will have the same value for all nodes in slot `j`. Byzantine nodes can have different values.
*   `byzantine_nodes`: A set containing the IDs of the Byzantine nodes.

Your simulator should output a list of lists, `commitments`.  `commitments[i][j]` represents the value that node `i` commits for slot `j`. If a node does not commit a value for a particular slot, the value should be `None`.

**Constraints:**

*   `n = 3f + 1`
*   The number of slots is determined by the length of the inner lists in `proposals`. You can assume all inner lists have the same length.
*   Nodes must make decisions based *only* on messages they have received.
*   The simulator must accurately model the simplified Multi-Paxos algorithm described above, including the majority requirements and value selection strategy.
*   Your solution should be efficient enough to handle a large number of nodes (e.g., `n = 100`) and slots (e.g., `1000`).

**Success Criteria:**

*   **Safety:**  For each slot, all honest nodes that commit a value must commit the same value.
*   **Liveness:** If all honest nodes propose the same value for a slot, all honest nodes should eventually commit that value for that slot. (Note: this does not guarantee that *every* honest node will *always* commit a value for *every* slot if Byzantine nodes are active, only when all honest nodes propose the same value.)

This problem requires careful attention to detail, especially regarding the message passing logic, majority calculations, and Byzantine fault tolerance.  Consider the different ways Byzantine nodes can behave and ensure your simulator can handle them correctly. Optimize your solution to efficiently simulate a large number of nodes and slots.
