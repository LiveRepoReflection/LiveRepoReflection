## Question: Distributed Key-Value Store Simulation

**Problem Description:**

You are tasked with simulating a simplified distributed key-value store. The store consists of `N` nodes, numbered from 0 to N-1. Your system must support the following operations with specific performance characteristics:

1.  **`PUT(key, value, replication_factor)`:** Stores the `value` associated with the given `key` across `replication_factor` distinct nodes. The `key` is a string, and the `value` is a positive integer. The `replication_factor` indicates how many nodes should hold a copy of the data. The nodes to store the data on should be chosen randomly but deterministically (based on the `key` - see details below).

2.  **`GET(key)`:** Retrieves the `value` associated with the given `key`.  If the `key` exists on at least one node, return the value. If the key does not exist in the system return -1. You must return the most recently `PUT` value for the `key`.

3.  **`DELETE(key)`:** Deletes the `key` and its associated value from all nodes.

**Constraints and Requirements:**

*   **Node Count (N):** 100 <= N <= 1000
*   **Replication Factor:** 1 <= replication\_factor <= N
*   **Key Length:** 1 <= len(key) <= 50 (string of alphanumeric characters)
*   **Value Range:** 1 <= value <= 10^9
*   **Operation Count:** Your solution must efficiently handle a very large number of operations (up to 10^6) of the above types.
*   **Deterministic Node Selection:** The nodes selected for `PUT` operations *must* be deterministic and solely based on the `key`. Implement a consistent hashing strategy. A simple way to achieve this is to hash the key (e.g., using Python's `hash()` function or a similar suitable hash function), take the modulo `N`, and then use the result as a starting point to select `replication_factor` distinct nodes.  If you use only mod N, consider using a better more advanced hashing function to avoid collisions for a large number of keys. The subsequent nodes can be selected by incrementing the starting index modulo `N`. This ensures that the same key always maps to the same set of nodes, regardless of the system state.
*   **Data Consistency:**  The GET operation should return the most recently PUT value. You need to implement a mechanism to track the version or timestamp of each key-value pair stored on a node.  A simple incrementing counter across all PUT operations is sufficient.
*   **Fault Tolerance (Simplified):** While not explicitly implemented, the design should consider that nodes may fail. The `replication_factor` helps mitigate data loss, but you don't need to simulate node failures.
*   **Optimization:** The solution should be optimized for speed.  Consider the time complexity of each operation. Brute-force approaches will likely time out. Focus on efficient data structures and algorithms.
*   **Memory Usage:** Minimize memory usage. Avoid storing unnecessary data.
*   **Concurrency (Implicit):** While you don't need to implement explicit threading or multiprocessing, consider how your design would scale in a concurrent environment. Your data structures and algorithms should be chosen with concurrency in mind.
*   **Edge Cases:** Handle edge cases such as:
    *   Putting a key that already exists.
    *   Getting a key that does not exist.
    *   Deleting a key that does not exist.
    *   Invalid input (e.g., invalid key format, replication\_factor outside the valid range).

**Input Format:**

The input will be a list of operations. Each operation is a string.

*   `PUT key value replication_factor`
*   `GET key`
*   `DELETE key`

**Output Format:**

For each `GET` operation, print the retrieved `value` or -1 if the key does not exist.  `PUT` and `DELETE` operations do not produce output.

**Example:**

```
Input:
PUT key1 123 3
GET key1
PUT key2 456 2
GET key2
DELETE key1
GET key1
PUT key1 789 1
GET key1

Output:
123
456
-1
789
```

**Judging Criteria:**

The solution will be judged based on correctness, efficiency (execution time), and code quality. The test cases will include a mix of small and large datasets to thoroughly evaluate performance.  Solutions that are slow or inefficient will likely time out. Solutions that crash or produce incorrect results will fail. Submissions will be penalized for excessive memory usage.
