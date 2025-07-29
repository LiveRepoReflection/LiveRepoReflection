## Question: Real-Time Collaborative Text Editor with Operational Transformation

**Description:**

Design and implement the core logic for a real-time collaborative text editor, focusing on conflict resolution using Operational Transformation (OT).

Imagine a distributed system where multiple users are simultaneously editing the same document. Each user has a local copy of the document and makes changes (operations) locally. These operations are then broadcast to other users. Due to network latency and concurrent edits, operations can arrive out of order and potentially conflict with each other, leading to inconsistent document states across different users' copies.

Your task is to implement the `transform` function, a crucial component of OT, which resolves these conflicts. Given two concurrent operations, `op1` and `op2`, where `op1` is the operation that the local user has already applied to their document, and `op2` is an operation received from a remote user, the `transform` function must produce `op2'`, a transformed version of `op2`, such that applying `op1` followed by `op2'` to the local document results in the same final state as applying `op2` followed by `op1` to the remote document (assuming both started with the same initial state).

**Constraints:**

1.  **Operation Types:** You need to support two basic operation types:
    *   `insert`: Inserts a string at a specific index. Represented as `{'type': 'insert', 'index': integer, 'text': string}`.
    *   `delete`: Deletes a substring starting at a specific index. Represented as `{'type': 'delete', 'index': integer, 'length': integer}`.

2.  **Index-Based Transformation:** The `transform` function must correctly handle transformations for operations based on their indices, considering the impact of other operations on those indices. You must ensure that the indices within operations always point to the correct location in the string.

3.  **Handling Concurrent Inserts and Deletes:** Pay special attention to cases where inserts and deletes occur concurrently at or near the same index. Consider different strategies for resolving these conflicts, such as prioritizing local operations or remote operations, and explain your chosen strategy in your code comments.

4.  **Efficiency:** The `transform` function should be efficient. Avoid unnecessary iterations or complex calculations. Aim for a time complexity of O(1) for most operations, but in the worst case, O(length of operation content) for insert or delete operations with very large strings.

5.  **Correctness:** The most important aspect is the correctness of the transformations. Ensure that applying the transformed operations results in a consistent document state across all users.

6.  **Real-World Considerations:** While you don't need to build a full-fledged editor, think about how your design decisions would scale to handle a large number of concurrent users and large documents. Consider the trade-offs between different OT strategies.

7. **Edge Cases:** Your solution should properly handle all edge cases, including operations at the beginning or end of the document, empty insert strings or delete lengths, and overlapping delete ranges.

**Input:**

*   `op1`: A dictionary representing the first operation (the one that has already been applied locally).
*   `op2`: A dictionary representing the second operation (the one received from a remote user).

**Output:**

*   A dictionary representing the transformed version of `op2` (`op2'`).

**Example:**

Let's say the document is initially "abc".

*   `op1 = {'type': 'insert', 'index': 1, 'text': 'X'}` (local user inserts "X" at index 1, document becomes "aXbc")
*   `op2 = {'type': 'delete', 'index': 2, 'length': 1}` (remote user deletes 1 character at index 2, thinking the document is still "abc")

The `transform` function should return:

*   `op2' = {'type': 'delete', 'index': 3, 'length': 1}` (the remote delete operation is transformed to account for the local insert, now deleting at index 3 in the local document "aXbc")
