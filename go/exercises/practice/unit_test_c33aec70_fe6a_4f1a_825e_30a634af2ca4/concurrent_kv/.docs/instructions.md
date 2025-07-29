## Project Name

`ConcurrentKVStore`

## Question Description

You are tasked with implementing a highly concurrent, in-memory key-value store. This KV store needs to handle a large number of concurrent requests for reading and writing data, with a focus on both correctness and performance.

**Requirements:**

1.  **Data Storage:** The KV store should store data in memory. You can choose the data structure(s) you deem most suitable (e.g., `map`, `sync.Map`). Keys and values should be strings.
2.  **Concurrency:** The KV store *must* be thread-safe and support a high degree of concurrency. Multiple goroutines should be able to read and write to the store simultaneously without data corruption or race conditions.
3.  **Operations:** Implement the following operations:
    *   `Get(key string) (string, bool)`: Retrieves the value associated with the given key. Returns the value and a boolean indicating whether the key exists.
    *   `Put(key string, value string)`: Stores the given value under the given key. Overwrites any existing value for the key.
    *   `Delete(key string)`: Deletes the key and its associated value from the store.
    *   `Snapshot() map[string]string`: Returns a consistent snapshot of the entire key-value store at a specific point in time. This operation should not block other operations (Get, Put, Delete) for an extended period.  The returned map should be a *copy* of the data, not a direct reference to the internal store.
4.  **Atomicity:** All operations (`Get`, `Put`, `Delete`) must be atomic.
5.  **Performance:**
    *   Minimize lock contention to ensure high throughput.
    *   Optimize for both read and write performance. Consider the trade-offs between different concurrency control mechanisms.
6.  **Error Handling:** While the basic operations don't need to return explicit errors, ensure graceful handling of any internal errors or unexpected situations (e.g., memory allocation failures).  Log such errors appropriately.
7.  **Scalability:** The design should be scalable to a large number of keys and values. Consider potential memory usage implications.
8.  **Correctness:** Data consistency is paramount. Ensure that reads always return the most up-to-date value written by a successful `Put` operation.
9.  **No External Dependencies:** You are restricted to using the Go standard library only. No external packages are allowed.

**Constraints:**

*   The KV store should be designed to handle a large number of concurrent requests (e.g., thousands per second).
*   The size of individual keys and values can be up to 1MB.
*   The total size of the data stored in the KV store can be up to several GB.
*   The `Snapshot()` operation should complete reasonably quickly, even with a large dataset.  Aim for a time complexity that's better than O(N) if possible, where N is the number of key-value pairs. However, you can assume it will be called much less frequently than the other methods.
*   The solution must be written in idiomatic Go.

**Bonus Challenges:**

*   Implement a mechanism to evict least recently used (LRU) entries when the store reaches a certain memory limit.
*   Add support for transactions with ACID properties (Atomicity, Consistency, Isolation, Durability - in memory).  Consider how to handle potential conflicts between concurrent transactions. (This is extremely challenging given the time constraints of a competition.)

This problem requires you to demonstrate a strong understanding of concurrency, data structures, and algorithm design in Go. Good luck!
