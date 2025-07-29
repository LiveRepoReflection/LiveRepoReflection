## Problem: Decentralized Order Book Matching

**Description:**

You are tasked with implementing a core component of a decentralized exchange (DEX): the order book matching engine. This engine is responsible for efficiently matching buy and sell orders in a permissionless and trustless manner. Due to the decentralized nature, the order book is distributed across a network of nodes, and communication between nodes is subject to latency and potential failures.

Your implementation must handle the following:

1.  **Order Representation:** Orders consist of a unique ID, a type (buy or sell), a price, and a quantity.

2.  **Order Book Structure:** Represent the order book using appropriate data structures that allow for efficient insertion, deletion, and retrieval of orders. The order book should maintain separate lists of buy and sell orders, sorted by price (highest buy price first, lowest sell price first). Consider that the order book can grow quite large.

3.  **Matching Algorithm:** Implement a matching algorithm that efficiently matches buy and sell orders based on price and time priority (first-in, first-out - FIFO). When a new order arrives, the engine should attempt to match it against existing orders in the order book. Partial fills are allowed (i.e., an order can be partially filled by multiple counter-orders).

4.  **Concurrency:** The system must be able to handle concurrent order submissions and cancellations from multiple nodes. Implement appropriate synchronization mechanisms to ensure data consistency and prevent race conditions.

5.  **Network Simulation:** Simulate the distributed nature of the system. Orders arrive from different nodes (represented by threads or asynchronous tasks). Simulate network latency by introducing random delays in order processing.

6.  **Persistence:** Implement a mechanism to persist the order book state to disk. This is crucial for recovery in case of node failures or restarts. Consider using a suitable serialization format (e.g., JSON, Protocol Buffers). Optimize for efficient read/write operations, as the order book might be very large.

7.  **Fault Tolerance:** Design the system to be resilient to node failures. If a node crashes, the order book should be able to recover its state from the persisted data. Consider using a checkpointing mechanism to periodically save the order book state.

8.  **Order Cancellation:** Orders can be cancelled. Implement a mechanism to efficiently remove cancelled orders from the order book.

9.  **Trade Execution:** When a match is found, generate trade execution records. Each record should contain the buy order ID, sell order ID, price, and quantity of the traded asset.

**Constraints and Requirements:**

*   **Performance:** The matching engine must be highly performant, capable of handling a high volume of orders with minimal latency.
*   **Data Consistency:** The order book must remain consistent even in the presence of concurrent operations and node failures.
*   **Scalability:** The system should be designed to scale to handle a large number of orders and nodes.
*   **Real-world Simulation:** The simulation should closely resemble a real-world decentralized exchange, including realistic order arrival rates, latency, and failure scenarios.
*   **Memory Efficiency:** Minimize memory usage to handle large order books.
*   **Determinism:** Given the same input sequence of orders and failures, the final state of the order book should be deterministic (important for auditing and dispute resolution in a decentralized system). Implement appropriate logging to facilitate debugging and auditing.
*   **Security:** Although complete security implementations are beyond the scope, consider potential vulnerabilities such as order spoofing or manipulation, and implement basic safeguards.

**Evaluation Criteria:**

*   Correctness of the matching algorithm
*   Performance (throughput and latency)
*   Data consistency and fault tolerance
*   Scalability and resource utilization
*   Code quality and readability
*   Adherence to constraints and requirements
*   Completeness of simulation and testing

This problem requires a solid understanding of data structures, algorithms, concurrency, distributed systems, and fault tolerance. Success requires careful design choices, efficient implementation techniques, and thorough testing. Good luck!
