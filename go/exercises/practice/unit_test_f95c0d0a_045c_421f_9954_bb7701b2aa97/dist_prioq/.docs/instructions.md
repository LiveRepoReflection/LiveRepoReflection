## Project Name

```
distributed-priority-queue
```

## Question Description

You are tasked with designing and implementing a distributed priority queue system in Go. This system should allow multiple producers to enqueue items with associated priorities, and multiple consumers to dequeue items based on their priority. Higher priority items should be dequeued before lower priority items.

**System Requirements:**

1.  **Distributed Architecture:** The system must be able to run across multiple machines (simulated via goroutines) to handle high throughput and provide fault tolerance.
2.  **Priority-Based Dequeueing:** Items must be dequeued in priority order. If multiple items have the same priority, they should be dequeued in FIFO order.
3.  **Scalability:** The system should be designed to handle a large number of items and a high rate of enqueue/dequeue operations.
4.  **Fault Tolerance:** The system should be resilient to node failures. If a node fails, the system should continue to operate without data loss.
5.  **Concurrency:** Multiple producers and consumers should be able to enqueue and dequeue items concurrently without causing race conditions or data corruption.
6.  **Efficient Operations:** Enqueue and Dequeue operations should be as efficient as possible, considering the distributed nature of the system. Minimizing inter-node communication is key.
7.  **Data Persistence**: The priority queue data should be persistent, i.e., survive process restarts. You can use a simple embedded key-value store for this purpose.

**Data Structure:**

Each item in the queue will be a struct:

```go
type Item struct {
    Value    string
    Priority int
    Timestamp int64 // Time of insertion to maintain FIFO for same priority items
}
```

**Implementation Details:**

1.  **Sharding:** Implement sharding to distribute the items across multiple nodes. The sharding key should be based on the `Value` of the item, ensuring items with similar values are likely to reside on the same node. A consistent hashing algorithm is highly recommended for efficient rebalancing upon node failures.
2.  **Node Discovery:** Implement a simple mechanism for nodes to discover each other (e.g., a central configuration server or a gossip protocol).
3.  **Communication:** Use gRPC for inter-node communication. Define gRPC services for enqueueing and dequeueing items.
4.  **Priority Queue Implementation:** Each node should maintain a local priority queue. You can use a heap-based priority queue for efficient insertion and retrieval.
5.  **Persistence:** Use a simple embedded key-value store (e.g., BadgerDB or BoltDB) to persist the priority queue data on each node.
6.  **Fault Tolerance:** Implement a basic form of replication. Each item should be replicated to at least one other node. Upon node failure, the replicated data can be used to rebuild the priority queue on another node. Consider how to handle data consistency in the event of failures.
7.  **Concurrency Control:** Use mutexes or other synchronization primitives to protect shared data structures from concurrent access.
8.  **Optimizations:** Consider using techniques such as batching to reduce the number of gRPC calls. Explore using bloom filters to avoid unnecessary inter-node communication when dequeueing items.

**Constraints:**

*   The number of nodes in the system should be configurable.
*   The number of producers and consumers should be configurable.
*   The maximum priority value should be configurable.
*   The system should be able to handle a large number of concurrent enqueue and dequeue operations (e.g., 10,000+ per second).
*   Assume that the network is unreliable and nodes can fail at any time.
*   Assume a fixed set of nodes.

**Your task is to implement:**

*   A function to initialize the distributed priority queue system with a specified number of nodes.
*   A function to enqueue an item into the system.
*   A function to dequeue an item from the system.

The solution should be well-structured, documented, and efficient. Consider the trade-offs between consistency, availability, and performance when designing your system.
