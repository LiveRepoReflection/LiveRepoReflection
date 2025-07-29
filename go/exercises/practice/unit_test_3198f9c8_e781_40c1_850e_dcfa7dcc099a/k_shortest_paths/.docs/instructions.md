Okay, here's a challenging Go coding problem designed to be difficult and sophisticated, suitable for a high-level programming competition, similar to a LeetCode hard problem.

### Project Name

`k-Shortest-Paths`

### Question Description

You are given a directed graph represented as an adjacency list, where each node is labeled with an integer from `0` to `n-1`. Each edge in the graph has a non-negative weight associated with it.

Your task is to implement a function that finds the *k* shortest paths from a given source node `start` to a destination node `end` in the graph. The paths do not have to be simple (i.e., they can contain cycles).

Return the lengths of the *k* shortest paths in ascending order as a slice of integers. If there are fewer than *k* paths from `start` to `end`, return all path lengths found. If no paths exist between `start` and `end`, return an empty slice.

**Input:**

*   `n`: The number of nodes in the graph (integer).
*   `graph`: An adjacency list representing the directed graph, where `graph[i]` is a slice of `[node, weight]` pairs representing the outgoing edges from node `i`. `node` is an integer representing the destination node, and `weight` is an integer representing the weight of the edge.
*   `start`: The starting node (integer).
*   `end`: The destination node (integer).
*   `k`: The number of shortest paths to find (integer).

**Output:**

*   A slice of integers representing the lengths of the *k* shortest paths from `start` to `end`, in ascending order.

**Constraints:**

*   `1 <= n <= 1000`
*   `0 <= start, end < n`
*   `1 <= k <= 100`
*   `0 <= weight <= 100`
*   The graph may contain cycles.
*   The graph may be disconnected.
*   The graph may have multiple edges between two nodes.

**Example:**

```
n = 5
graph = [][]int{
    {[]int{1, 2}, []int{2, 4}}, // Node 0
    {[]int{2, 1}, []int{3, 7}}, // Node 1
    {[]int{3, 3}},             // Node 2
    {[]int{4, 1}},             // Node 3
    {},                         // Node 4
}
start = 0
end = 4
k = 3

Output: []int{8, 10, 12}
```

**Explanation:**

The shortest paths from node 0 to node 4, and their lengths, are:

1.  0 -> 1 -> 2 -> 3 -> 4 (2 + 1 + 3 + 1 = 7)
2.  0 -> 2 -> 3 -> 4 (4 + 3 + 1 = 8)
3.  0 -> 1 -> 3 -> 4 (2 + 7 + 1 = 10)
4.  0 -> 1 -> 2 -> 3 -> 4 (2 + 1 + 3 + 1 = 7)
5. 0 -> 0 -> 1 -> 2 -> 3 -> 4 (0 + 2 + 1 + 3 + 1 = 7)
6. 0 -> 0 -> 2 -> 3 -> 4 (0 + 4 + 3 + 1 = 8)
7. 0 -> 0 -> 1 -> 3 -> 4 (0 + 2 + 7 + 1 = 10)

The `k=3` shortest paths are `7`, `8` and `10`.

**Optimization Requirements:**

The solution should be efficient enough to handle graphs with up to 1000 nodes within reasonable time limits. Brute-force approaches that explore all possible paths will likely time out. Consider using appropriate data structures and algorithms to optimize your solution. Efficiency and memory optimization are important.

**System Design Aspects:**

Consider the scalability of your solution. How would your approach change if the graph were much larger (e.g., millions of nodes)? While a fully scalable solution is not required for this problem, think about the limitations of your approach.

Good luck!
