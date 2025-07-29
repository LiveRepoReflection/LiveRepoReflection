## Project Name

```
Dynamic-Connectivity-Oracle
```

## Question Description

You are tasked with designing and implementing a highly efficient dynamic connectivity oracle. This oracle must handle a massive stream of connection requests on a very large network, and provide near-instantaneous answers to connectivity queries.

The network consists of `N` nodes, numbered from `0` to `N-1`. Initially, no nodes are connected. You will receive two types of operations:

1.  **Connect(u, v):**  Establish a connection between nodes `u` and `v`. This means `u` and `v` are now in the same connected component. If they were already connected, this operation has no effect.
2.  **AreConnected(u, v):**  Determine if nodes `u` and `v` are currently connected (i.e., in the same connected component). Return `True` if they are connected, `False` otherwise.

Your solution must support these operations efficiently, especially the `AreConnected` query, as it will be called far more frequently than `Connect`.

**Constraints:**

*   `1 <= N <= 10^9` (Number of nodes. Note that you cannot pre-allocate an array of this size)
*   `1 <= Number of Connect operations <= 10^6`
*   `1 <= Number of AreConnected operations <= 10^7`
*   `0 <= u, v < N` for all `Connect(u, v)` and `AreConnected(u, v)` operations.

**Performance Requirements:**

*   `Connect(u, v)` should have an amortized time complexity of `O(log N)` or better.
*   `AreConnected(u, v)` should have a time complexity of `O(1)` or very close to it in practice.  Ideally it should avoid traversing the graph.

**Implementation Details:**

*   Implement the `Connect(u, v)` and `AreConnected(u, v)` functions within a class.
*   The class should be initialized with the number of nodes, `N`.
*   You are allowed to use standard Python libraries, but excessive memory usage will be penalized.  Specifically, avoid storing information for *every* node unless absolutely necessary.
*   Consider the trade-offs between memory usage and query performance. Solutions that are fast but consume excessive memory will be considered less optimal.
*   The input `u` and `v` in the methods will be integers.
*   The system will call the `Connect` and `AreConnected` methods repeatedly in a mixed and unpredictable order.
*   The judge may perform timing analysis to ensure your solution meets the performance requirements.

**Edge Cases to Consider:**

*   Self-loops: `Connect(u, u)`
*   Duplicate connections: `Connect(u, v)` followed by `Connect(u, v)` again.
*   Large number of nodes with relatively few connections.
*   A sequence of many Connect operations followed by a burst of AreConnected operations.
*   Input values of `u` and `v` could be the same.
