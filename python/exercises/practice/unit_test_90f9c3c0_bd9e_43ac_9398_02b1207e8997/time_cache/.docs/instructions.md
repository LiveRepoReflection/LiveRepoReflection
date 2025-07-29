## Problem: Scalable Distributed Key-Value Store with Time-Based Eviction

**Description:**

You are tasked with designing a simplified, in-memory key-value store that mimics the behavior of a distributed cache with time-based eviction.  This system needs to be highly scalable and handle a large number of read and write operations efficiently.  The core requirement is the ability to automatically evict entries after a specified Time-To-Live (TTL) has expired.

**Functionality:**

Your solution must implement the following functions:

*   `put(key, value, ttl)`: Inserts or updates a key-value pair in the store. `key` is a string, `value` can be any Python object, and `ttl` is an integer representing the Time-To-Live in seconds.  If the key already exists, its value should be updated, and the TTL reset.
*   `get(key)`: Retrieves the value associated with a given `key`. If the key does not exist or the entry has expired, return `None`.
*   `remove(key)`: Removes the key-value pair associated with the key. Return `True` if the key was successfully removed, and `False` if the key does not exist.
*   `size()`: Returns the current number of key-value pairs in the store (including expired ones that haven't been explicitly removed).
*   `evict_expired()`: Explicitly removes all expired key-value pairs from the store. This function should be optimized to avoid performance bottlenecks.

**Constraints and Requirements:**

1.  **Scalability:** Your solution should be designed to handle a large number of concurrent requests (reads and writes). While true parallelism in Python is limited by the GIL, your design and choice of data structures should minimize contention and maximize throughput. Consider the impact of operations on different parts of your data structures.
2.  **Efficiency:** `get`, `put`, and `remove` operations should be optimized for speed. Aim for average-case O(1) or close to O(1) time complexity. The `evict_expired()` method needs to also be efficient to avoid blocking other operations for a long time.
3.  **Time Complexity:** Time complexity is an important factor for the evaluation of your solution.
4.  **Memory Management:** Be mindful of memory usage. Avoid unnecessary object creation and ensure that expired entries are eventually garbage collected.
5.  **Thread Safety:** Your implementation must be thread-safe to allow concurrent access from multiple threads or processes.  Use appropriate locking mechanisms to prevent race conditions and data corruption.
6.  **TTL Granularity:** The TTL is specified in seconds. While your solution doesn't need to be *perfectly* accurate (millisecond precision is not required), it should provide reasonably accurate expiration times.
7.  **No External Libraries (Mostly):** You are allowed to use the `threading` and `time` modules from the Python standard library.  Using other external libraries (e.g., `redis`, `memcached`, `asyncio`, `multiprocessing`, other database libraries) is **strictly prohibited**. You can use standard Python data structures like dictionaries, lists, and sets.
8.  **Corner Cases:** Handle edge cases gracefully, such as:
    *   Negative or zero TTL values (treat them as immediately expired).
    *   Attempting to get or remove a key that does not exist.
    *   Large values for TTL.
9.  **Optimizations:** You should focus on optimizing the put, get and evict_expired methods.

**Evaluation Criteria:**

Your solution will be evaluated based on:

*   **Correctness:** Does it correctly implement the specified functionality and handle all edge cases?
*   **Performance:** How quickly does it perform the required operations under heavy load?
*   **Scalability:** How well does it handle a large number of concurrent requests?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?
*   **Memory Usage:** Does it efficiently manage memory and avoid leaks?
*   **Thread Safety:** Is it thread-safe and free from race conditions?

This problem requires a deep understanding of data structures, algorithms, and concurrency in Python. Good luck!
