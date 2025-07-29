## The Byzantine Broadcast Bonanza

**Problem Description:**

You are tasked with building a highly reliable broadcast system in a distributed Byzantine network. Imagine a scenario where a single source node needs to reliably transmit a message to all other nodes in the network, even when some nodes might be malicious and actively trying to disrupt the communication. This is a variation of the classic Byzantine Generals Problem.

**Network Setup:**

*   You are given a directed graph representing the network topology. Each node in the graph is a computer, and each directed edge represents a communication channel. The graph can have cycles and self-loops.
*   One node is designated as the "source" node. This node is assumed to be honest and wants to broadcast a message (a single integer) to all other nodes.
*   A subset of the nodes are "Byzantine" (malicious). These nodes can behave arbitrarily. They can lie about the message they received, refuse to forward messages, collude with each other, or even send contradictory messages to different nodes.
*   You are given `n` (number of nodes), `e` (number of edges), `source` (source node index, 0-indexed), `byzantine` (a `HashSet` of byzantine node indices), and a `message` (the integer to be broadcasted).

**Requirements:**

Implement a broadcast protocol that guarantees the following:

1.  **Agreement:** All honest (non-Byzantine) nodes eventually agree on the same message.
2.  **Validity:** If the source node is honest, then all honest nodes eventually agree on the message that the source node sent.

**Constraints and Considerations:**

*   **Message Integrity:** The system must be able to detect and reject potentially corrupted messages from Byzantine nodes.
*   **Limited Communication Rounds:** The protocol should converge within a reasonable number of communication rounds. Aim for a solution that converges in `O(k)` rounds, where `k` is a constant or a function of the graph's diameter, but independent of `n`.
*   **Byzantine Node Ratio:** The protocol should tolerate a reasonable fraction of Byzantine nodes. It should provably guarantee agreement and validity if the number of Byzantine nodes is strictly less than one-third of the total number of nodes (`f < n/3`).
*   **Asynchronous Communication:** You cannot assume a global clock or synchronized communication. Messages can arrive at different times and in different orders.
*   **Performance:** For a large graph (n > 1000), the protocol's execution time should be reasonable (e.g., under 10 seconds). Focus on efficient data structures and algorithms.
*   **Scalability:** The protocol should be designed with scalability in mind. Consider how the communication overhead and memory usage grow as the network size increases.
*   **Edge Cases:** Handle cases where the graph is disconnected, the source node is Byzantine, or there are no Byzantine nodes.
*   **Rust Features:** Leverage Rust's features such as ownership, borrowing, and concurrency to ensure memory safety and efficient parallelism.  Consider using `rayon` or similar for parallel message processing.
*   **Data Structure Choice:** The choice of data structures (e.g., for message storage, routing information) significantly affects performance. Carefully consider the trade-offs.
*   **Memory Usage:** Be mindful of memory consumption, especially when dealing with a large number of nodes and messages. Use techniques like message aggregation or pruning to reduce memory footprint.

**Input:**

*   `n`: The number of nodes in the network.
*   `e`: The number of edges in the network.
*   `edges`: A vector of tuples, where each tuple `(u, v)` represents a directed edge from node `u` to node `v`.
*   `source`: The index of the source node.
*   `byzantine`: A `HashSet` containing the indices of the Byzantine nodes.
*   `message`: The initial message to be broadcasted by the source.

**Output:**

*   A `HashMap<usize, i32>` where the key is the node index (0-indexed) and the value is the agreed-upon message by that node. For Byzantine nodes, the value can be arbitrary.

**Judging Criteria:**

Your solution will be judged based on:

1.  **Correctness:** Does your protocol guarantee agreement and validity under the specified conditions?
2.  **Efficiency:** How quickly does your protocol converge, especially for large networks?
3.  **Robustness:** How well does your protocol handle edge cases and varying network topologies?
4.  **Code Quality:** Is your code well-structured, readable, and maintainable? Does it adhere to Rust's best practices?
5.  **Resource Usage:** Is your protocol memory efficient?

**Hint:** Consider using a multi-round protocol like Practical Byzantine Fault Tolerance (PBFT) or a simplified variant. You might need to implement message signing, voting, or other mechanisms to detect and tolerate Byzantine behavior. Focus on a clear and efficient implementation, even if it's a simplified version of a more complex protocol.
