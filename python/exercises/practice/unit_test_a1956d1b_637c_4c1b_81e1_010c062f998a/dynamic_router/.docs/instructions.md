## Question: Optimal Multi-Source Shortest Path Routing in a Dynamic Network

**Problem Description:**

You are tasked with designing a routing algorithm for a dynamic communication network. This network consists of `N` nodes (numbered 0 to N-1) and a set of bidirectional communication links between them. The network is dynamic, meaning that the latency of each link can change over time.

You are given a series of routing requests. Each request specifies a set of *source* nodes `S` and a *destination* node `D`.  The goal is to find the *minimum possible latency* to send data from *any* node in `S` to `D`.  Since the network is dynamic, you must consider the latency of the links *at the moment of the routing request*.

**Specifics:**

1.  **Network Representation:** The network is represented by a dictionary. The keys are node indices (integers from 0 to N-1). The value associated with each node is another dictionary representing its neighbors and the current latency to each neighbor. For example:

    ```python
    network = {
        0: {1: 5, 2: 10}, # Node 0 is connected to node 1 with latency 5 and node 2 with latency 10
        1: {0: 5, 3: 2},  # Node 1 is connected to node 0 with latency 5 and node 3 with latency 2
        2: {0: 10, 3: 7}, # Node 2 is connected to node 0 with latency 10 and node 3 with latency 7
        3: {1: 2, 2: 7}   # Node 3 is connected to node 1 with latency 2 and node 2 with latency 7
    }
    ```

2.  **Routing Requests:** Each routing request is a tuple of the form `(S, D)`, where:

    *   `S` is a set of source node indices (e.g., `{0, 1}`).
    *   `D` is the destination node index (e.g., `3`).

3.  **Dynamic Latency Updates:** Before each routing request, you might receive a list of latency updates. Each update is a tuple of the form `(U, V, L)`, where:

    *   `U` and `V` are node indices representing a link between nodes `U` and `V`.
    *   `L` is the new latency for the link between `U` and `V`. You must update the network representation to reflect this change.

4. **Constraints:**

   *   The number of nodes `N` can be large (up to 10<sup>5</sup>).
   *   The number of routing requests can also be large (up to 10<sup>5</sup>).
   *   The latency of a link is always a positive integer.
   *   The size of the source set `S` can vary.
   *   The network is *not guaranteed* to be fully connected. There may not be a path from every source node to the destination node.
   *   **Time Complexity:** Your solution must be efficient enough to handle a large number of nodes and requests within a reasonable time limit.  Brute-force approaches that recalculate shortest paths from scratch for every request will likely time out. Consider using appropriate data structures and algorithms to optimize performance.

5. **Error Handling:**

    * If no path exists from *any* source node in `S` to the destination node `D`, return `-1`.

**Input:**

You will be given:

*   `N`: The number of nodes in the network.
*   A list of initial links `initial_links`: A list of tuples `(U, V, L)` representing the initial state of the network.
*   A list of operations `operations`: A list of either latency updates or routing requests.
    *   Latency updates are tuples `(U, V, L)`.
    *   Routing requests are tuples `(S, D)`.
    *   You need to process the operations in the order they appear in the list.

**Output:**

For each routing request in the `operations` list, output the minimum possible latency to send data from any node in `S` to `D`. If no path exists, output `-1`.

**Example:**

```python
N = 4
initial_links = [(0, 1, 5), (0, 2, 10), (1, 3, 2), (2, 3, 7)]
operations = [
    ({0, 1}, 3),  # Routing request: sources = {0, 1}, destination = 3
    (1, 3, 1),    # Latency update: link between 1 and 3 now has latency 1
    ({0}, 3),     # Routing request: source = {0}, destination = 3
    (0, 2, 12),   # Latency update: link between 0 and 2 now has latency 12
    ({2, 3}, 1)   # Routing request: sources = {2, 3}, destination = 1
]

# Expected Output:
# 7 (0 -> 1 -> 3 = 5 + 2, 1 -> 3 = 2.  Minimum is 2+5=7, min(5+2, 2) =7)
# 6 (0 -> 1 -> 3 = 5 + 1)
# 7 (2 -> 0 -> 1 = 12+5, 3->1 = 1. min(12+5, 1) = 1)
```

**Challenge:**

The primary challenge is to efficiently handle a large number of nodes, requests, and latency updates. You will need to choose appropriate data structures and algorithms to achieve acceptable performance. Pre-calculating all-pairs shortest paths at the beginning is not feasible due to the dynamic nature of the network. Consider algorithms that can incrementally update shortest paths or find shortest paths on demand in an efficient manner. Good luck!
