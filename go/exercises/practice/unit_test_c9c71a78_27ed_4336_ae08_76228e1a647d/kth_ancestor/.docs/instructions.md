Okay, here's a challenging Go coding problem designed to test a range of skills, focusing on efficiency and edge-case handling.

**Project Name:** `kth-ancestor`

**Question Description:**

You are given a rooted tree with `n` nodes, labeled from `0` to `n-1`. The tree is represented by a parent array `parents` of length `n`, where `parents[i]` is the parent of node `i`. The root node is the node with `parents[i] == -1`.

You need to implement a data structure `KthAncestor` that efficiently answers queries about the k-th ancestor of any node in the tree.

The `KthAncestor` data structure should support the following operations:

*   **`KthAncestor(n int, parents []int)`:**  Constructor to initialize the data structure with the number of nodes `n` and the `parents` array. This is where you should precompute any necessary data structures for efficient querying.
*   **`GetKthAncestor(node int, k int) int`:** Returns the k-th ancestor of the given `node`. If the k-th ancestor doesn't exist (i.e., we go beyond the root), return `-1`.

**Constraints and Requirements:**

1.  **Large Tree:** The number of nodes `n` can be up to 10<sup>5</sup>.
2.  **Frequent Queries:** The `GetKthAncestor` method will be called many times (up to 10<sup>5</sup> times). Therefore, the initialization and query methods *must* be optimized for speed.
3.  **Large k:** The value of `k` in `GetKthAncestor` can also be up to 10<sup>5</sup>.  A naive iterative approach will likely be too slow.
4.  **Memory Constraints:** Be mindful of memory usage. Creating excessively large data structures could lead to memory limit exceeded errors.
5.  **Time Complexity:**  The goal is to achieve a time complexity for `GetKthAncestor` significantly better than O(k) in the worst case. Solutions with O(log n) or better query time are desirable. The constructor's time complexity is less critical but should still be reasonable (e.g., O(n log n) or better).

**Example:**

```go
n := 7
parents := []int{-1, 0, 0, 1, 1, 2, 2}
kthAncestor := Constructor(n, parents)

//kthAncestor.GetKthAncestor(3, 1) // return 1 (1 is the 1st ancestor of 3)
//kthAncestor.GetKthAncestor(5, 2) // return 0 (0 is the 2nd ancestor of 5)
//kthAncestor.GetKthAncestor(6, 3) // return -1 (there is no 3rd ancestor of 6)
```

**Hints (Implied):**

*   Consider using dynamic programming to precompute ancestor information.
*   Think about representing ancestor information in a way that allows you to "jump" up the tree efficiently. A binary lifting technique could be useful.
*   Handle edge cases carefully, such as `k = 0`, `node` being the root node, and `k` being larger than the node's depth.

This problem requires a good understanding of tree data structures, algorithmic optimization, and efficient implementation in Go. Good luck!
