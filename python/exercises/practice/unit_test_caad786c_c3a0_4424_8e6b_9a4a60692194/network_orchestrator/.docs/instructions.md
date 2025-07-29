## The Network Orchestrator

### Question Description

You are tasked with designing a network orchestrator for a large-scale distributed system. The system consists of `N` nodes, each identified by a unique integer ID from `0` to `N-1`. These nodes need to communicate with each other to perform various tasks. The network infrastructure is unreliable, and connections between nodes can fail.

The orchestrator's primary responsibility is to efficiently manage the network topology and ensure reliable message delivery between nodes, even in the face of network failures. You will simulate this process.

**Specifically, you need to implement a system that handles the following operations:**

1.  **`connect(node1, node2)`:** Establishes a direct connection between `node1` and `node2`. This connection is bidirectional. If the connection already exists, this operation has no effect. Assume node IDs are always valid (0 <= node1, node2 < N).

2.  **`disconnect(node1, node2)`:** Removes the direct connection between `node1` and `node2`. If the connection does not exist, this operation has no effect. Assume node IDs are always valid (0 <= node1, node2 < N).

3.  **`sendMessage(source, destination, message)`:** Sends a message from `source` to `destination`. The message must be delivered reliably, even if the direct connection between `source` and `destination` is broken. If a direct connection doesn't exist, or breaks mid-transmission, the message should be routed through intermediate nodes using the shortest possible path. If no path exists between `source` and `destination`, the message cannot be delivered.

    *   If the message is delivered successfully, return `True`.
    *   If the message cannot be delivered, return `False`.

**Constraints:**

*   **Network Size:** The number of nodes `N` can be very large (up to 10<sup>5</sup>).
*   **Operation Frequency:** The system needs to handle a high volume of operations. The number of operations can also be up to 10<sup>5</sup>.
*   **Message Size:** Messages are small, so message size itself isn't a limiting factor.
*   **Shortest Path:** When routing, prioritize the shortest path (fewest hops) between the source and destination. If multiple shortest paths exist, any one of them is acceptable.
*   **Real-time Failures:** Connections can be broken (using `disconnect`) at any time, even while a message is being sent. Your routing algorithm must be resilient to these failures.
*   **Memory Usage:** The system should be memory-efficient. Storing the entire network topology in a simple adjacency matrix might be too memory-intensive for large `N`.

**Efficiency Requirements:**

*   `connect` and `disconnect` operations should be efficient (ideally O(1) or O(log N) on average).
*   `sendMessage` operation should be reasonably efficient. While finding the absolute shortest path in a dynamically changing graph is computationally expensive, aim for a solution that performs well in practice and avoids excessive computation. You should justify your choice of algorithm and data structures.

**Edge Cases:**

*   Handle cases where `source` and `destination` are the same node.
*   Handle cases where the network is partitioned (i.e., some nodes are unreachable from others).
*   Handle cases where `node1` and `node2` in `connect` and `disconnect` are the same.

**Bonus:**

*   Implement a mechanism to detect and avoid routing loops.
*   Consider using heuristics to improve routing performance in very large networks.
*   Document your design choices and justify your algorithm's complexity.

This problem requires you to combine graph algorithms, data structures, and system design considerations to build a robust and efficient network orchestrator. Good luck!
