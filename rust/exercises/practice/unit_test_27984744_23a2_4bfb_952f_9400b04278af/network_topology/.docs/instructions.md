Okay, I'm ready. Here's a challenging Rust coding problem designed to be similar to a LeetCode Hard difficulty question.

## Project Name

`NetworkTopology`

## Question Description

You are tasked with designing and implementing a system to manage and analyze a dynamic network topology. The network consists of nodes and unidirectional links between them. Each node has a unique identifier (an integer). The network is constantly changing, with nodes being added or removed, and links being created or destroyed.

Your system must support the following operations:

1.  **`add_node(node_id: i32)`**: Adds a new node to the network. If a node with the same ID already exists, the operation should be ignored.

2.  **`remove_node(node_id: i32)`**: Removes a node from the network and all links connected to it (incoming and outgoing). If a node with the given ID does not exist, the operation should be ignored.

3.  **`add_link(from_node: i32, to_node: i32, latency: i32)`**: Adds a unidirectional link from `from_node` to `to_node` with the specified `latency`. The latency is a non-negative integer representing the time it takes to transmit data from one node to another. If either `from_node` or `to_node` does not exist, or if the link already exists, the operation should be ignored.

4.  **`remove_link(from_node: i32, to_node: i32)`**: Removes the link from `from_node` to `to_node`. If either `from_node` or `to_node` does not exist, or if the link does not exist, the operation should be ignored.

5.  **`shortest_path(start_node: i32, end_node: i32) -> Option<i32>`**: Calculates the shortest path (minimum total latency) from `start_node` to `end_node` using Dijkstra's algorithm. If no path exists, return `None`.  If either `start_node` or `end_node` does not exist, return `None`.

6.  **`is_strongly_connected() -> bool`**: Determines whether the network is strongly connected. A network is strongly connected if every node is reachable from every other node. The network is considered strongly connected even if there are zero or one nodes.

7. **`find_critical_links() -> Vec<(i32, i32)>`**: Find all critical links in the network. A critical link is a link that, if removed, would increase the shortest path between its source and destination nodes, or disconnect the destination from the source entirely. Return a vector of tuples, where each tuple represents a critical link `(from_node, to_node)`. The order of links in the vector doesn't matter.

## Requirements and Constraints

*   **Efficiency:** The `shortest_path` and `is_strongly_connected` and `find_critical_links` operations should be implemented with reasonable algorithmic efficiency.  Consider the time complexity of your algorithms, especially as the number of nodes and links grows.  Aim for solutions better than O(N^2) for `shortest_path` if possible.

*   **Data Structures:** Choose appropriate data structures to represent the network topology efficiently. Consider the trade-offs between different data structures in terms of memory usage and performance for various operations.

*   **Error Handling:** Handle edge cases gracefully. Operations that attempt to access non-existent nodes or links should be handled appropriately (e.g., by ignoring the operation or returning an error).

*   **Scalability:** Your solution should be able to handle a reasonably large network (e.g., up to 10,000 nodes and 100,000 links).

*   **Memory Usage:** Be mindful of memory usage, especially when dealing with large networks.

*   **Rust Idiomaticity:** Write clean, idiomatic Rust code, utilizing Rust's features (e.g., ownership, borrowing, lifetimes) effectively.
*   **No external crates**: You must use only standard library features.

This problem requires careful consideration of data structures, algorithm design, and optimization to achieve acceptable performance. Good luck!
