Okay, here's a challenging problem for a Go programming competition, focusing on graph algorithms, optimization, and real-world constraints.

## Project Name

```
network-congestion
```

## Question Description

You are tasked with designing a system to analyze and mitigate network congestion in a large-scale data center. The data center network can be represented as a directed graph, where nodes represent servers and edges represent network connections between them.  Each edge has a capacity, representing the maximum bandwidth it can handle.

You are given a series of data transfer requests. Each request specifies a source server, a destination server, and the amount of data to be transferred.  Your goal is to determine the *minimum number of requests that need to be rejected* to ensure that **no edge exceeds its capacity** at any point in time while maximizing the total amount of data successfully transferred.

**Input:**

*   `servers`: An integer representing the number of servers in the network. Servers are numbered from `0` to `servers - 1`.
*   `edges`: A 2D array (slice of slices in Go) where each row represents a directed edge in the form `[source, destination, capacity]`.
*   `requests`: A 2D array where each row represents a data transfer request in the form `[source, destination, data_amount]`.

**Output:**

An integer representing the minimum number of requests that must be rejected.

**Constraints:**

*   `1 <= servers <= 1000`
*   `0 <= len(edges) <= 5000`
*   `0 <= len(requests) <= 2000`
*   `0 <= source, destination < servers` for all edges and requests
*   `1 <= capacity <= 1000` for all edges
*   `1 <= data_amount <= 1000` for all requests

**Optimization Requirements:**

*   The solution should be efficient. Brute-force approaches will likely time out. Consider using appropriate graph algorithms and data structures.
*   The solution should minimize the number of rejected requests while maximizing the total data transferred.

**Edge Cases:**

*   Disconnected graph:  Some servers may not be reachable from others.
*   No path between source and destination for some requests.
*   Requests that individually exceed the capacity of edges on their path (even before considering other requests).
*   Multiple possible solutions with the same number of rejected requests. The algorithm should strive to maximize the total data transferred in such cases.

**System Design Aspects (Implicit):**

*   The solution should be scalable enough to handle a moderate number of servers, edges, and requests.

**Multiple Valid Approaches:**

*   Network flow algorithms (e.g., Ford-Fulkerson, Edmonds-Karp) could be adapted, but require modification to handle the request rejection constraint.
*   Greedy approaches with careful sorting and pathfinding might be possible, but proving optimality will be challenging.
*   Dynamic programming combined with graph traversal could be considered.

**Example:**

```
servers = 4
edges = [[0, 1, 10], [0, 2, 5], [1, 3, 10], [2, 3, 15]]
requests = [[0, 3, 7], [0, 3, 8], [1, 2, 5]]

//Possible solution: Reject the second request [0,3,8]
//Output: 1
```

**Clarifications:**

*   You are allowed to use any standard Go libraries.
*   You do not need to implement any external communication or persistence mechanisms.
*   The judge will evaluate the correctness of your solution and its efficiency in terms of runtime and memory usage.

This problem requires a combination of algorithmic knowledge, careful implementation, and optimization skills. Good luck!
