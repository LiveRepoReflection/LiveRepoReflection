## Question: Distributed Key-Value Store with Eventual Consistency

### Question Description

You are tasked with designing and implementing a simplified version of a distributed key-value store. This system will consist of multiple nodes that store data redundantly to ensure availability and fault tolerance. However, due to network latency and potential failures, the system will employ an eventual consistency model.

**Core Requirements:**

1.  **Data Model:** The key-value store should support storing string keys and string values.

2.  **Node Behavior:** Each node in the system should be able to handle the following operations:

    *   `put(key, value)`: Stores the given key-value pair locally.
    *   `get(key)`: Retrieves the value associated with the given key from its local storage. Returns `None` if the key is not found.
    *   `replicate(data)`: Accepts a dictionary of key-value pairs and merges them into its local storage.  You must handle potential conflicts (see Conflict Resolution below).
    *   `get_all_data()`: Returns a dictionary containing all key-value pairs stored locally.

3.  **Conflict Resolution:** In the event of conflicting updates to the same key across different nodes, the system should use a Last Write Wins (LWW) strategy based on timestamps. Each key-value pair should be associated with a timestamp representing the time of the last update. The `put` and `replicate` operations need to update the timestamp for each key-value pair.

4.  **Eventual Consistency:** The system should eventually converge to a consistent state. This means that if no new updates are made to the system for a sufficiently long time, all nodes should eventually have the same data for any given key. You don't need to implement a specific mechanism for triggering replication. Assume that nodes will periodically share their data with each other, and replication is invoked using `replicate(data)`.

5.  **Optimized Replication:** When replicating data between nodes, only the key-value pairs that are *newer* than the receiving node's data for that key should be sent. This reduces unnecessary network traffic.

6.  **Concurrency Handling:**  The system should be able to handle concurrent `put`, `get`, and `replicate` operations without data corruption or race conditions.

**Constraints:**

*   The system should be designed to be scalable to a large number of nodes. However, you don't need to explicitly handle node discovery or membership. You can assume a fixed set of nodes with known addresses.
*   Assume that network communication is unreliable and messages may be lost or delayed. However, you don't need to implement explicit error handling for network failures. Focus on the core data consistency logic.
*   You can use standard Python libraries for data structures and concurrency.

**Considerations:**

*   Think about how to efficiently store and retrieve key-value pairs with timestamps.
*   Consider the trade-offs between different data structures for storing the data.
*   How would you ensure that the timestamp assigned is globally unique in the distributed environment? (You don't need to implement a full solution, but describe your thought process).
*   How would you handle node failures and ensure data durability? (Describe potential strategies, but you don't need to implement them).
*   How does this design align with the CAP theorem?

**Your Task:**

Implement the `Node` class with the `put`, `get`, `replicate`, and `get_all_data` methods. Pay close attention to the LWW conflict resolution strategy, optimized replication, and concurrency handling. Your solution should be efficient and scalable.
