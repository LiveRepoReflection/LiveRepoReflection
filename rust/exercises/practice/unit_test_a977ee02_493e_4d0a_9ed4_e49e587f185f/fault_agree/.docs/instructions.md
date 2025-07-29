## Problem: Distributed Consensus with Fault Tolerance

**Description:**

You are tasked with implementing a simplified distributed consensus algorithm in Rust, focusing on fault tolerance and message ordering. Imagine a system of `N` nodes, where `N` can be any integer >= 3. Each node needs to agree on a sequence of ordered events. In a real-world system, these events could be database transactions, configuration updates, or any other critical operation.

Your system must handle the following:

1.  **Proposing Events:** Any node can propose a new event to be added to the agreed-upon sequence.

2.  **Consensus:** The nodes must reach a consensus on the order of events, even if some nodes are temporarily unavailable or experience network issues (message loss, delays, duplication).

3.  **Fault Tolerance:** The system should tolerate up to `f` faulty nodes, where `f < N/2` (strict majority is required).  This means that even if `f` nodes crash or become unresponsive, the remaining nodes should still be able to reach a consensus.

4.  **Message Ordering:** Messages can be delivered out of order or duplicated, but the final agreed-upon event sequence must be consistent across all non-faulty nodes and maintain the intended causal order (if A happens before B, A must appear before B in the final sequence).  You do *not* need to handle malicious nodes sending arbitrary or contradictory messages (Byzantine Fault Tolerance).

5.  **Efficiency:**  While correctness is paramount, your solution should also strive for efficiency in terms of message complexity and latency. Consider the trade-offs between different consensus approaches. Strive for efficient data structures.

**Input:**

*   `N`: The number of nodes in the system.  This will be provided as a configuration parameter.
*   A series of "propose" messages to the system. These will be represented as tuples: `(node_id: usize, event_data: String)`. The `node_id` indicates which node originated the proposal.

**Output:**

*   A vector of `String` representing the agreed-upon, ordered sequence of events. This vector should be identical across all non-faulty nodes after consensus is reached.

**Constraints:**

*   `N >= 3`
*   `f < N/2`
*   You can simulate network conditions (message loss, delays, duplication) within your code to test the fault tolerance.
*   You can assume a reliable broadcast channel (if a node sends a message to all other nodes, at least `N - f` nodes will eventually receive it).
*   Event data (`String`) can be any arbitrary string and should be treated as opaque.
*   Node IDs are integers from `0` to `N-1`.

**Example:**

Let's say we have `N = 3` nodes.  The input could be:

```
propose(0, "Event A")
propose(1, "Event B")
propose(2, "Event C")
```

A valid output could be:

```
["Event A", "Event B", "Event C"]
```

However, depending on the timing and network conditions, other valid outputs are possible, as long as the events are ordered consistently across all nodes after consensus. For example:

```
["Event B", "Event A", "Event C"]
```

**Hints (but not required):**

*   Consider using a variant of Paxos or Raft for consensus. These are well-established algorithms for achieving consensus in distributed systems.  You can simplify them significantly for this problem since you don't need full Byzantine fault tolerance.
*   Think carefully about data structures to efficiently store and manage proposed events and their ordering.
*   Implement message passing between nodes using channels or similar mechanisms.
*   Implement a simple simulation of network faults (e.g., randomly dropping messages) to test your fault tolerance.
*   Focus on achieving correctness first, then optimize for efficiency.

This problem requires a good understanding of distributed systems concepts and the ability to translate them into a robust and efficient Rust implementation. Good luck!
