## Project Name

`DistributedKeyValStore`

## Question Description

You are tasked with designing and implementing a distributed key-value store. This store should be able to handle a high volume of read and write requests, tolerate node failures, and maintain data consistency.

Specifically, you need to implement a system that consists of a cluster of nodes. Each node in the cluster can:

1.  **Store Key-Value Pairs:** Each node has a local storage (e.g., a hashmap) to store key-value pairs. Keys and values are arbitrary byte arrays.
2.  **Handle Read Requests:** When a node receives a read request for a key, it should return the corresponding value if it exists in its local storage. If the key does not exist, the node should return an appropriate error.
3.  **Handle Write Requests:** When a node receives a write request for a key-value pair, it should store the key-value pair in its local storage.
4.  **Replicate Data (Eventual Consistency):** Implement a mechanism to replicate data across multiple nodes to ensure fault tolerance. Use an *eventual consistency* model.  When a node receives a write request, it should asynchronously replicate the write to `N-1` other nodes, where `N` is total number of nodes in the cluster. The other `N-1` target nodes are chosen randomly.
5.  **Handle Node Failures:** The system should be able to tolerate node failures without losing data. If a node fails, the remaining nodes should continue to operate normally. You do *not* need to implement automatic node recovery.  Assume that failed nodes remain failed and do not come back online.
6.  **Conflict Resolution (Last Write Wins):** In case of conflicting writes to the same key, implement a "Last Write Wins" strategy based on timestamps. Each write operation must be associated with a timestamp. When resolving conflicts, the write with the latest timestamp should be considered the correct value.
7.  **Gossip Protocol for Failure Detection:** Implement a simple gossip protocol where nodes periodically exchange heartbeat messages with a subset of other nodes. If a node doesn't receive a heartbeat from another node for a certain period, it marks that node as failed.
8.  **Read Repair:** When a client requests a read and gets inconsistent data (due to eventual consistency), initiate a read repair mechanism. The node handling the read request should query other nodes for the latest version of the data (based on timestamps) and update its local storage if necessary.

**Constraints and Requirements:**

*   **Concurrency:** Your solution must be thread-safe and handle concurrent read and write requests efficiently. Use appropriate synchronization mechanisms (e.g., mutexes, channels).
*   **Scalability:** While you don't need to implement horizontal scaling in this exercise, your design should consider scalability aspects.
*   **Error Handling:** Implement robust error handling. Return meaningful error messages to the client when operations fail.
*   **Optimization:** Strive for optimal performance. Consider factors such as network latency, data serialization, and concurrency control.
*   **N Value:**  The replication factor `N` can be configured.
*   **Timestamp Generation:** Your timestamp generation mechanism must be monotonically increasing *per node*.
*   **Gossip Interval:** The frequency of heartbeat messages should be configurable.
*   **Failure Threshold:** The number of missed heartbeats before a node is considered failed should be configurable.
*   **Data Size:** You may assume keys and values are relatively small (e.g., up to 1KB).
*   **Node Count:** The number of nodes in the cluster is known at initialization.

**Bonus (Optional):**

*   Implement a mechanism to detect and resolve data inconsistencies between nodes (e.g., using Merkle trees).
*   Implement a more sophisticated conflict resolution strategy (e.g., vector clocks).
*   Add support for data expiration (TTL).

This problem requires a solid understanding of distributed systems concepts, concurrency, data structures, and algorithms. It also challenges your ability to design and implement a robust and efficient system. Good luck!
