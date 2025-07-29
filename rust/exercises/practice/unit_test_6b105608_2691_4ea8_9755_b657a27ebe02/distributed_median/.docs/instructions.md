Okay, here's a problem designed to be challenging, sophisticated, and suitable for a high-level programming competition in Rust:

## Project Name

```
DistributedMedian
```

## Question Description

You are building a distributed system for processing massive datasets. A core requirement is to efficiently calculate the median of numerical data distributed across multiple nodes.

Each node in the system holds a sorted stream of integers. These streams can be of varying lengths and arrive at different times. Your task is to design and implement a system in Rust that can efficiently compute the global median of all the numbers observed so far across all nodes.

Specifically, you need to implement the following functionality:

1.  **Node Registration:** Nodes can dynamically register with the system. Each node is identified by a unique `node_id` (a `u64`).
2.  **Data Streaming:** After registration, each node can stream sorted integers to the system using the `add_data(node_id: u64, data: &[i64])` API. The `data` slice contains integers that are already sorted in ascending order within the slice for that node.
3.  **Median Calculation:** At any point, a client can request the current global median of all the numbers received so far from all registered nodes. Your `get_median()` function must return the correct median. If no data has been received, it should return `None`.
4.  **Memory Constraints:** The system must be able to handle a large number of nodes and a massive volume of data *without* storing all the data in memory simultaneously.  Consider that a single node may stream billions of integers over time.
5.  **Performance Requirements:** The `get_median()` function must be reasonably efficient.  Naive solutions involving sorting all received data on each call will not be acceptable.  Minimize the time complexity of computing the median.
6.  **Concurrency:** Multiple nodes may stream data concurrently. Your system must be thread-safe and handle concurrent data updates correctly. The `get_median()` function must provide a consistent view of the data, even during concurrent updates.

**Constraints:**

*   The number of nodes can be up to 10,000.
*   Each node can stream up to 10^9 integers.
*   Integers can be positive, negative, or zero.
*   The system should be optimized for minimizing the time taken to calculate the median, while respecting the memory constraints.
*   You must use appropriate data structures and algorithms to meet both the memory and performance requirements.

**Specific Implementation Requirements:**

*   Implement a struct called `DistributedMedianSystem`.
*   Implement the following methods:
    *   `new()`: Creates a new `DistributedMedianSystem`.
    *   `register_node(node_id: u64)`: Registers a new node with the given `node_id`.  Returns `true` if successful, `false` if the `node_id` is already registered.
    *   `add_data(node_id: u64, data: &[i64])`: Adds a sorted stream of integers to the system from the specified node.
    *   `get_median() -> Option<f64>`: Returns the current global median of all the numbers received so far. Returns `None` if no data has been received.

**Example Usage:**

```rust
let system = DistributedMedianSystem::new();
system.register_node(1);
system.add_data(1, &[1, 2, 3]);
system.register_node(2);
system.add_data(2, &[4, 5]);
let median = system.get_median(); // Should return Some(3.0)
system.add_data(1, &[6, 7]);
let median = system.get_median(); // Should return Some(4.0)
```

**Judging Criteria:**

*   **Correctness:** The `get_median()` function must always return the correct median.
*   **Efficiency:** The implementation must be efficient in terms of both time and memory usage.
*   **Concurrency:** The system must be thread-safe and handle concurrent data updates correctly.
*   **Code Quality:** The code must be well-structured, readable, and maintainable.
*   **Handling Edge Cases:**  The implementation must gracefully handle edge cases, such as empty data streams, duplicate numbers, and a large number of nodes.

This problem challenges the contestant to think about distributed systems, data structures, algorithms, concurrency, and memory management. Good luck!
