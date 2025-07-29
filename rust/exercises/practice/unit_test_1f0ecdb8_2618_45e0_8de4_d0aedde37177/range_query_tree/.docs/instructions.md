Okay, here's a challenging Rust coding problem designed to be at the "Hard" level, incorporating advanced data structures, complex constraints, and optimization requirements.

### Project Name

`RangeQueryTree`

### Question Description

You are tasked with implementing a persistent range query tree (a variant of a segment tree) to efficiently handle a large number of range queries on an initially immutable array.  Persistence means that after each update, you maintain access to all previous versions of the array.

**Input:**

1.  An initial array `arr` of `n` integers (indexed from 0 to n-1).
2.  A sequence of `m` operations, each of which is one of the following types:

    *   **`Update(version, index, value)`:**  Create a new version of the array based on `version`, where the element at `index` is updated to `value`. `version` refers to the version number *before* this update. The first version is version 0 (the initial array).
    *   **`RangeSum(version, left, right)`:** Query the sum of the elements in the range `[left, right]` (inclusive) in `version` of the array.
    *   **`MinValue(version, left, right)`:** Query the minimum value of the elements in the range `[left, right]` (inclusive) in `version` of the array.
    *   **`QueryVersion(version)`**: Output the array of specific version.

**Output:**

For each `RangeSum`, `MinValue`, or `QueryVersion` operation, output the result to the console.

**Constraints:**

*   `1 <= n <= 10^5` (Initial array size)
*   `1 <= m <= 10^5` (Number of operations)
*   `-10^9 <= arr[i] <= 10^9` (Initial array element values)
*   `0 <= index < n` (Update index)
*   `-10^9 <= value <= 10^9` (Update value)
*   `0 <= left <= right < n` (Range query bounds)
*   `0 <= version < current_version` (Version number, starting from 0.  The `current_version` is the total number of updates performed so far.)
*   Memory usage is extremely important and will be heavily tested.  Solutions that use excessive memory will be penalized or may even crash.

**Requirements:**

1.  **Persistence:**  Each update should create a new version of the array without modifying previous versions. All versions must be accessible for querying.
2.  **Efficiency:** Range queries (sum and min) must be answered efficiently.  Aim for a solution with a time complexity of *O(log n)* per query, where n is the size of the array.
3.  **Memory Optimization:**  The persistent nature of the data structure means that each update potentially creates new nodes in the tree. Minimize memory usage by sharing common subtrees between different versions. Consider lazy propagation techniques (if applicable) to further reduce the number of nodes created.
4.  **Error Handling:** If the input `version` does not exist, the program will print error message and return.

**Considerations:**

*   Implement a persistent segment tree (or a similar persistent data structure) that supports range sum and minimum queries.
*   Focus on sharing nodes between different versions of the tree to minimize memory usage.  This is critical for the scale of the problem.
*   Think about how to efficiently manage the version history.  A simple array of tree roots might suffice, but consider alternative approaches if memory becomes a bottleneck.
*   Pay close attention to edge cases and boundary conditions.
*   Rust's ownership and borrowing system will be crucial for managing memory safely and efficiently.
*   The problem requires careful consideration of algorithmic efficiency and memory footprint, making it a challenging and sophisticated task.

This problem requires a good understanding of persistent data structures, segment trees, and careful memory management in Rust. Good luck!
