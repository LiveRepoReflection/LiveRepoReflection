## Project Name

`OptimalNetworkAllocation`

## Question Description

You are tasked with designing and implementing an algorithm for optimal allocation of network resources in a dynamic environment.  A telecommunications company manages a network represented as a graph where nodes are routers and edges are communication links with associated capacities and costs.  The company receives a continuous stream of service requests, each specifying a bandwidth demand and a source and destination router.

The network has `N` routers (numbered 0 to N-1) and `M` links. Each link `i` connecting routers `u` and `v` has a capacity `C_i` and a cost per unit bandwidth `P_i`.

Your algorithm must efficiently determine whether a new service request can be accommodated without exceeding link capacities, and if so, find the minimum cost path to route the requested bandwidth.

**Specifically, you need to implement a function that:**

1.  Takes as input:
    *   The network topology (routers and links with capacities and costs). The network is represented by 2 dictionaries:
        *   `capacities`: A dictionary where keys are tuples of (source_router, destination_router) and values are the capacities of the link between them. Note that the graph is undirected, so (u, v) and (v, u) represent the same link, and only one of them will be present in the dictionary.
        *   `costs`: A dictionary where keys are tuples of (source_router, destination_router) and values are the cost per unit bandwidth of the link between them.
    *   The current bandwidth allocation on each link. This represented by a dictionary where keys are tuples of (source_router, destination_router) and values are the currently used bandwidth on that link.
    *   A new service request, defined by:
        *   `source`: The source router for the request.
        *   `destination`: The destination router for the request.
        *   `bandwidth`: The bandwidth required by the request.

2.  Performs the following checks:
    *   Determines if a path exists between the source and destination routers in the network.
    *   Checks if there is enough capacity on each link along the path to accommodate the new bandwidth request.
    *   If multiple paths exist, find the path with the minimum total cost (sum of link costs multiplied by the bandwidth).

3.  Returns:

    *   If a feasible path is found:
        *   A tuple containing:
            *   The optimal path as a list of router indices (including source and destination).
            *   The total cost of routing the bandwidth along the optimal path.
    *   If no feasible path is found, return `None`.

**Constraints:**

*   The number of routers `N` can be up to 1000.
*   The number of links `M` can be up to 5000.
*   Bandwidth demands can be floating point numbers.
*   Link capacities and costs are positive floating point numbers.
*   The algorithm must be efficient enough to handle a large number of requests in a reasonable time. Think about the time complexity of your solution.
*   Consider edge cases such as disconnected graphs, zero-capacity links, and invalid input.
*   You need to handle the undirected nature of the network links.
*   The solution should be robust to floating point precision issues.

**Example:**

```python
capacities = {(0, 1): 10.0, (1, 2): 5.0, (0, 2): 12.0}
costs = {(0, 1): 1.0, (1, 2): 2.0, (0, 2): 3.0}
allocations = {(0, 1): 3.0, (1, 2): 1.0, (0, 2): 5.0}
source = 0
destination = 2
bandwidth = 4.0

# Expected output: ([0, 2], 12.0)
# (Path 0->2 is cheaper (4.0 * 3.0 = 12.0) than 0->1->2 (4.0 * (1.0 + 2.0) = 12.0), even though both are equally viable.
```

**Optimization Requirements:**

*   The solution must be computationally efficient, especially when dealing with a large number of routers and links.  Consider using appropriate data structures and algorithms to minimize execution time.
*   Be mindful of memory usage, as the network topology can be large.

This problem requires a combination of graph traversal algorithms (Dijkstra or similar for shortest path), capacity checking, and careful handling of floating-point arithmetic and data structures. It encourages thinking about algorithm complexity and optimization in a practical networking scenario.
