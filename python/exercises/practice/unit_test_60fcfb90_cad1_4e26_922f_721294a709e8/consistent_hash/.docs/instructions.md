## Project Name

`DistributedConsistentHashing`

## Question Description

You are tasked with designing and implementing a distributed key-value store using consistent hashing. The system consists of a cluster of `N` nodes (servers), each identified by a unique integer ID from 0 to N-1. Your goal is to distribute keys across these nodes in a way that minimizes data movement when nodes are added or removed from the cluster.

**Requirements:**

1.  **Consistent Hashing Implementation:** Implement a consistent hashing algorithm using a hash ring. Each node and key should be hashed to a point on the ring (0 to 2<sup>32</sup>-1). The key is assigned to the node whose hash value is the smallest that is greater than or equal to the key's hash value. If no node's hash is greater than the key's hash, then the key is assigned to the node with the smallest hash value (wrapping around the ring).

2.  **Dynamic Node Management:** The system must support adding and removing nodes dynamically. When a node is added, only a minimal number of keys should be re-assigned. Similarly, when a node is removed, its keys should be redistributed to other nodes in the cluster with minimal disruption.

3.  **Key Distribution:** Given a key, the system should be able to determine which node is responsible for storing that key.

4.  **Virtual Nodes:** To ensure a more even distribution of keys, each physical node should be represented by `V` virtual nodes on the hash ring. These virtual nodes should be dispersed across the hash ring, allowing a single physical node to handle keys from various parts of the key space.  The virtual node ID should be derived deterministically from the physical node ID.

5.  **Handling Node Failures:** The system should be designed to handle node failures gracefully. When a node fails, its keys should be automatically redistributed to the next available node on the ring.

6.  **Performance Considerations:**  The key distribution and node management operations should be as efficient as possible.  Consider the time complexity of these operations, especially when dealing with a large number of nodes and virtual nodes.  Use appropriate data structures and algorithms to optimize performance.

7.  **Data Structure Choice:** You are free to choose appropriate data structures, but a sorted data structure (e.g., a balanced tree or sorted array) to represent the hash ring is highly recommended for efficient key lookup.

**Constraints:**

*   `N` (number of nodes): 1 <= N <= 1000
*   `V` (number of virtual nodes per physical node): 1 <= V <= 100
*   Key space: Strings of alphanumeric characters with length between 1 and 20.
*   Nodes are identified by integers from 0 to N-1.
*   Hash function: You can use any readily available hash function (e.g., MurmurHash3, SHA-256) or a simple custom hash function, but clearly specify which hash function you are using.  The hash function must produce a 32-bit integer output.
*   Minimize data movement: Adding or removing a single node should ideally only affect `1/N` of the keys, where N is the total number of nodes.

**Input/Output:**

The system will be tested through a series of operations:

*   `add_node(node_id)`: Adds a new node with the given ID to the cluster.
*   `remove_node(node_id)`: Removes the node with the given ID from the cluster.
*   `get_node(key)`: Returns the ID of the node responsible for storing the given key. If there are no nodes in the system, return -1.

**Example:**

Initially, the cluster is empty.

1.  `add_node(0)`
2.  `add_node(1)`
3.  `get_node("key1")` -> Returns either 0 or 1 (depending on the hash values of "key1", virtual nodes associated to node 0 and virtual nodes associated to node 1)
4.  `get_node("key2")` -> Returns either 0 or 1 (depending on the hash values of "key2", virtual nodes associated to node 0 and virtual nodes associated to node 1)
5.  `remove_node(0)`
6.  `get_node("key1")` -> Returns 1 (since node 0 is removed, "key1" is now assigned to node 1)
7. `add_node(2)`
8.  `get_node("key1")` -> Returns either 1 or 2 (depending on the hash values of "key1", virtual nodes associated to node 1 and virtual nodes associated to node 2)

**Grading Criteria:**

*   Correctness: The system must correctly distribute keys across nodes, even with dynamic node additions and removals.
*   Efficiency: The key distribution and node management operations should be efficient, especially for large clusters.
*   Data Movement Minimization: Adding or removing nodes should result in minimal data movement.
*   Robustness: The system should handle node failures gracefully and continue to operate correctly.
*   Code Quality: The code should be well-structured, readable, and maintainable.

This problem challenges you to design and implement a robust and scalable distributed key-value store using consistent hashing. It requires a deep understanding of data structures, algorithms, and distributed systems concepts. Good luck!
