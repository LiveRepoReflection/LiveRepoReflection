## Problem: Distributed Consensus Log

### Question Description

You are tasked with designing a highly available and consistent distributed log service. This service is used by various applications to record events in a sequential and reliable manner. The core of the service is a cluster of nodes that must maintain a consistent view of the log, even in the presence of node failures and network partitions.

Your implementation must adhere to the following requirements:

1.  **Log Structure:** The log is an ordered sequence of entries. Each entry has a unique, monotonically increasing integer index (starting from 1). Each entry contains a string of arbitrary data.

2.  **Consensus:** The cluster must use a consensus algorithm (like Raft or Paxos - you don't need to *implement* Raft/Paxos, but your design should be compatible with such algorithms. Consider *how* your design would interact with such an algorithm) to agree on the order and content of the log entries.

3.  **High Availability:** The service should remain available for reads and writes even if a minority of nodes in the cluster fail.

4.  **Linearizability:** All reads should return the latest committed value.  If a client writes a value, any subsequent read (globally) must return that value or a later value.

5.  **Durability:** Once a log entry is committed, it must be persistently stored and recoverable even if the entire cluster restarts.

6. **Scalability:** Design should allow scaling horizontally.

You are given a cluster of `N` nodes (where `N` is an odd number, to ensure a majority). Each node has:

*   A unique ID (an integer).
*   Persistent storage (e.g., a local disk).
*   The ability to communicate with other nodes in the cluster via a reliable (but potentially slow and subject to network partitions) network.

Your task is to implement the following functions:

*   `append(data: str) -> int`: Appends a new entry containing `data` to the log. Returns the index of the newly appended entry. This operation must be consistent across the cluster. This should be the leader node operation, and must be robust to leader failure.
*   `read(index: int) -> str`: Reads the entry at the given `index` in the log. Returns the data contained in the entry. If the index is out of bounds (i.e., greater than the highest committed index), the operation should block *until* the entry at that index is available. If the index is invalid (less than 1), raise an exception.
* `get_highest_index() -> int`: Returns the index of the highest committed entry in the log.

**Constraints and Considerations:**

*   **Concurrency:** The `append` and `read` operations can be called concurrently from multiple clients.
*   **Node Failures:** Nodes can fail at any time. The system should automatically recover from node failures.
*   **Network Partitions:** The network can be partitioned, leading to nodes being temporarily unable to communicate with each other. The system should maintain consistency even during partitions.
*   **Performance:** While correctness is paramount, strive for reasonable performance. Minimize latency for both `append` and `read` operations. Consider caching strategies.
*   **Storage Efficiency:** Design your storage mechanism to be as efficient as possible. Consider log compaction techniques to prevent the log from growing indefinitely.
*   **Fault Tolerance:** Consider that network connection between nodes could fail.

**Extra Challenge:**

*   Implement a mechanism for log compaction (snapshotting or log segment merging) to reclaim disk space.
*   Implement a client-side retry mechanism with exponential backoff to handle temporary network errors.
*   Implement leader election.

**Note:** You do *not* need to implement the underlying consensus algorithm (Raft/Paxos) from scratch. You can assume that a "black box" consensus library is available that provides the primitives for leader election, log replication, and agreement on a sequence of commands. Your task is to design how to *use* this consensus library to build the distributed log service. Focus on the data structures, API design, fault tolerance, and performance aspects. Consider what data is stored on disk.
