## The Byzantine Fault Tolerant Key-Value Store

### Question Description

You are tasked with designing and implementing a simplified, in-memory, Byzantine Fault Tolerant Key-Value store in Rust. In a distributed system, Byzantine faults refer to situations where nodes can behave arbitrarily, including sending incorrect or malicious information. Your key-value store needs to tolerate a certain number of these faulty nodes while still providing consistent and reliable data.

**Core Requirements:**

1.  **Data Structure:** Implement an in-memory key-value store. Keys and values are both strings. You can use standard Rust data structures like `HashMap` internally.

2.  **Replication:** The key-value store is replicated across `N` nodes (replicas). You will be given `N` as input.

3.  **Fault Tolerance:** The system must tolerate up to `f` Byzantine faulty nodes, where `f < N/3`. In other words, `N > 3f`. You will be given `f` as input.

4.  **Operations:** Implement the following operations:
    *   `put(key: String, value: String)`: Stores the `value` associated with the `key`.
    *   `get(key: String)`: Retrieves the `value` associated with the `key`. Returns `None` if the key does not exist.

5.  **Byzantine Fault Tolerance Mechanism:** Implement the Practical Byzantine Fault Tolerance (PBFT) consensus protocol for both `put` and `get` operations (simplified version described below).

**Simplified PBFT Consensus Protocol:**

1.  **Request:** The client (the entity calling `put` or `get`) sends the request to a designated "primary" replica.  The primary is selected round-robin.

2.  **Pre-prepare:** The primary replica proposes a value to all other replicas (the "backups"). This message includes a sequence number (incremented for each new request) and a cryptographic hash of the request.

3.  **Prepare:** Each backup replica, upon receiving the `pre-prepare` message, validates the request (check the hash and sequence number). If valid, it sends a `prepare` message to all other replicas, including the primary.

4.  **Commit:** Each replica waits until it receives `2f` `prepare` messages (including its own) from different replicas, all agreeing on the same request.  If so, it sends a `commit` message to all other replicas.

5.  **Reply:** Each replica waits until it receives `2f + 1` `commit` messages (including its own) from different replicas, all agreeing on the same request. The replica then executes the request locally (either storing the value for `put` or retrieving the value for `get`) and sends the result back to the client.

6. **Client Receives:** The client waits for `f + 1` identical replies from different replicas before accepting the result as valid.

**Constraints and Considerations:**

*   **Simplified Model:** You can assume a synchronous network (messages are delivered within a known time bound). You do NOT need to handle timeouts or view changes.
*   **No Persistence:** The data is stored in memory and is lost upon program termination.
*   **Concurrency:** Your implementation must be thread-safe, allowing multiple clients to interact with the key-value store concurrently. Use appropriate locking mechanisms (e.g., `Mutex`).
*   **Efficiency:** Your implementation should aim to minimize communication overhead and latency. Consider the complexity of your chosen data structures and algorithms. The `put` and `get` operations should be reasonably fast for small datasets (e.g., less than 10,000 key-value pairs).
*   **Testing:** You must write comprehensive unit tests to demonstrate the correctness and fault tolerance of your implementation. Consider testing scenarios with different numbers of replicas and faulty nodes.
*   **Fault Simulation:** You need to simulate Byzantine faults.  You'll be given a list of faulty nodes.  When a faulty node receives a request, it can behave arbitrarily: it can send incorrect messages, send no messages, send messages to the wrong recipients, etc.  Your code should include logic to simulate these faults based on the faulty node list.  The behaviour of the faulty node should be random. For example, a faulty node might ignore 50% of the requests, send incorrect data in 30% of the requests, and behave correctly in 20% of the requests.

**Input:**

*   `N`: The number of replicas.
*   `f`: The maximum number of faulty replicas that can be tolerated.
*   `faulty_nodes: Vec<usize>`: A vector of indices representing the faulty nodes (0-indexed).
*   A series of `put` and `get` operations.

**Output:**

*   For each `get` operation, return the value associated with the key (or `None` if the key does not exist).
*   The `put` operation does not return any value.

**Challenge:**

The main challenge is to implement the PBFT consensus protocol correctly and efficiently, while also simulating Byzantine faults and ensuring that the key-value store remains consistent and reliable even in the presence of these faults.  Think carefully about how to structure your code to handle the different phases of the protocol and how to simulate the behaviour of faulty nodes.  Consider the trade-offs between different approaches and choose the one that best balances correctness, efficiency, and maintainability.
