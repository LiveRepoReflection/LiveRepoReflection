## Problem: Distributed Key-Value Store with Range Queries

### Question Description

You are tasked with designing and implementing a simplified, distributed key-value store. This system must support basic `put` and `get` operations, but also crucially needs to efficiently handle *range queries*.

**System Architecture:**

The key-value store consists of `N` server nodes, each responsible for storing a subset of the keys.  Keys are 64-bit unsigned integers (u64). You are given a consistent hashing function `hash(key: u64) -> u64` that maps keys to a uniform distribution across the 64-bit unsigned integer space.  The servers are conceptually arranged in a ring, where each server is responsible for a contiguous range of hash values.  The server responsible for a given key `k` is determined by `hash(k) % N`, where `N` is the number of servers.

**Data Storage:**

Each server stores key-value pairs in memory.  Values are arbitrary byte arrays (`Vec<u8>`).

**Operations:**

Implement the following operations:

1.  **`put(key: u64, value: Vec<u8>)`**: Stores the given key-value pair in the appropriate server.

2.  **`get(key: u64) -> Option<Vec<u8>>`**: Retrieves the value associated with the given key. Returns `None` if the key is not found.

3.  **`range_query(start_key: u64, end_key: u64) -> Vec<(u64, Vec<u8>)>`**:  Retrieves all key-value pairs where the key `k` satisfies `start_key <= k <= end_key`. The returned key-value pairs must be sorted by key in ascending order.  This is where the challenge lies.  The range may span multiple servers, requiring coordinated queries.

**Constraints and Requirements:**

*   **Efficiency:** Range queries must be as efficient as possible. Naive solutions that involve querying all servers and filtering locally will likely time out on larger datasets.  Consider how to minimize the number of servers that need to be contacted.
*   **Data Distribution:** Assume keys are inserted with a relatively uniform distribution.
*   **Server Count:** The number of servers `N` can be large (up to 1000).
*   **Key Space:** The full 64-bit unsigned integer range is possible for keys.
*   **Scalability:** While you don't need to implement dynamic server addition/removal, your design should consider how the system could scale horizontally.
*   **Error Handling:** Implement basic error handling (e.g., return `None` for `get` if the key doesn't exist).  Assume servers don't crash.
*   **Concurrency:** The `put`, `get`, and `range_query` operations can be called concurrently.  Ensure thread safety.
*   **Optimization:**  Focus on optimizing the `range_query` operation.
*   **No external crates (except for standard library primitives):**  You are allowed to use standard Rust library features such as `Mutex`, `Arc`, `HashMap` and `RwLock`, but limit the usage of external crates to demonstrate in-depth knowledge of Rust.

**Grading Criteria:**

*   **Correctness:** The implementation must correctly handle all operations, including edge cases.
*   **Performance:** The `range_query` operation must be efficient, especially for large ranges and/or a large number of servers.  Solutions with poor performance will be penalized.
*   **Code Quality:** The code should be well-structured, readable, and maintainable.
*   **Concurrency Safety:** The implementation must be thread-safe.
*   **Design Considerations:**  Justification of design choices, especially regarding range query optimization.

This problem requires a solid understanding of data structures, algorithms, distributed systems concepts, and Rust's concurrency features. Good luck!
