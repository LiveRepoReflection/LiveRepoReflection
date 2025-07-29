Okay, here's a challenging Go coding problem designed to test a wide range of skills, including algorithm design, data structure selection, optimization, and edge-case handling.

### Project Name

```
network-connectivity
```

### Question Description

You are tasked with designing and implementing a system to manage network connectivity between a large number of nodes. Each node represents a server, and the network represents the possible connections between them. The system must be able to handle a high volume of requests for adding connections, removing connections, and querying the network's connectivity.

More formally:

1.  **Nodes:** The nodes in the network are represented by unique integer identifiers (node IDs), starting from 0. The maximum number of nodes in the network is `10^6`.

2.  **Connections:** A connection is an undirected edge between two nodes.

3.  **Connectivity:** Two nodes are considered connected if there exists a path between them. A path is a sequence of connections between nodes.

Your system must support the following operations:

*   `AddConnection(node1, node2)`: Adds a connection between `node1` and `node2`. If the connection already exists, this operation should be a no-op. If either `node1` or `node2` is not a valid node (ID outside the range \[0, `10^6`-1]), the operation should be a no-op.

*   `RemoveConnection(node1, node2)`: Removes the connection between `node1` and `node2`. If the connection does not exist, this operation should be a no-op. If either `node1` or `node2` is not a valid node (ID outside the range \[0, `10^6`-1]), the operation should be a no-op.

*   `AreConnected(node1, node2)`: Returns `true` if `node1` and `node2` are connected, and `false` otherwise. If either `node1` or `node2` is not a valid node (ID outside the range \[0, `10^6`-1]), return `false`.

*   `FindLargestConnectedComponent()`: Returns the size (number of nodes) of the largest connected component in the network. If the network is empty (no nodes or connections), return 0.

**Constraints:**

*   The number of `AddConnection`, `RemoveConnection`, and `AreConnected` operations can be up to `10^5`.
*   The number of `FindLargestConnectedComponent` operations can be up to `10^2`.
*   The system must be memory-efficient.  Avoid creating unnecessary copies of the network data.
*   The `AreConnected` and `FindLargestConnectedComponent` operations must be reasonably efficient. A naive solution that traverses the entire network for each call will likely time out.

**Considerations:**

*   Think carefully about the data structures you use to represent the network and the connections.
*   Consider using algorithms such as Union-Find or graph traversal algorithms (BFS, DFS) for efficient connectivity checks.
*   Pay attention to the time complexity of your operations, especially `AreConnected` and `FindLargestConnectedComponent`.
*   Handle edge cases gracefully, such as adding or removing connections between the same node, or adding/removing non-existent connections.
*   The solution should be concurrent safe. Multiple go routines could call functions in your solution at the same time.
