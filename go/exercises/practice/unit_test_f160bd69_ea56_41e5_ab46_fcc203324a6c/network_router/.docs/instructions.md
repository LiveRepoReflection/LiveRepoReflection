Okay, here's a challenging Go coding problem designed to test a candidate's ability to work with graphs, optimize for performance, and handle complex constraints.

## Project Name

`NetworkOptimization`

## Question Description

Imagine you are building the core routing engine for a large Content Delivery Network (CDN). This CDN operates across a vast network of geographically distributed servers (nodes). Each server has a limited bandwidth capacity.  Your task is to design an algorithm that efficiently routes traffic through the network to minimize latency for users requesting content.

**Problem Details:**

You are given a representation of the CDN network as a directed graph.

*   **Nodes:** Each node represents a CDN server. Each node has a unique ID (an integer).
*   **Edges:** Each edge represents a direct network connection between two CDN servers. Each edge has:
    *   `Source`: The ID of the source server.
    *   `Destination`: The ID of the destination server.
    *   `Latency`:  A measure of the network latency (delay) along this connection (represented as an integer).
    *   `Bandwidth`: The maximum bandwidth capacity of the connection (represented as an integer).

You are also given a list of content requests. Each request has:

*   `UserID`: A unique identifier for the user making the request.
*   `ContentID`: A unique identifier for the content being requested.
*   `SourceServer`: The ID of the server closest to the user (where the request originates).
*   `DestinationServer`: The ID of the server that holds the requested content.
*   `BandwidthRequired`: The amount of bandwidth (in Mbps) required to fulfill this request.

**Objective:**

Implement a function `OptimizeNetwork(networkGraph, requests)` that takes the network graph and a list of content requests as input. The function should determine the optimal path for each request, satisfying the following constraints:

1.  **Bandwidth Constraints:** The total bandwidth used on any given edge *cannot* exceed the edge's `Bandwidth` capacity.  If a path cannot be found to satisfy the bandwidth requirement without exceeding capacity on any edge, the request should be rejected.
2.  **Latency Minimization:** Among all possible paths that satisfy the bandwidth constraints, choose the path with the *lowest total latency*.  Total latency is the sum of the `Latency` values of all edges in the path.
3.  **Global Optimization:** The algorithm must consider all requests simultaneously when making routing decisions. This is crucial because routing one request might block optimal paths for other requests.
4.  **Rejection Handling:** If a request *cannot* be routed due to bandwidth limitations (even after considering all possible paths and the routing of other requests), it should be rejected. Rejected requests should be returned in a list.

**Output:**

The function `OptimizeNetwork` should return two values:

1.  `routedRequests`: A map where the key is `UserID` and the value is a slice of `Node` IDs representing the optimal path (in order) for that request. If a request is rejected, it should *not* be included in this map.
2.  `rejectedRequests`: A list of `UserID` values representing the requests that could not be routed due to bandwidth limitations.

**Constraints and Considerations:**

*   **Graph Size:** The network graph can be large (hundreds or thousands of nodes and edges).
*   **Request Volume:** The number of content requests can also be significant.
*   **Algorithmic Complexity:**  Brute-force solutions (e.g., trying all possible paths for each request) will likely time out.  Consider efficient graph traversal algorithms and optimization techniques.
*   **Real-time Routing:** Although not strictly enforced, solutions should strive for performance characteristics that would be suitable for a near real-time routing system.
*   **Edge cases**: Handle cases when there are no routes available between the source and destination server for a given request.
*   **Multiple optimal paths**: If there are multiple paths with the same minimal latency, any of these paths is considered a valid solution.
*   **Fairness**: While minimizing overall latency, the algorithm should ideally avoid unfairly prioritizing certain requests over others. (This is a soft requirement; correctness and performance are paramount.)

**Data Structures (Go):**

```go
type Node struct {
    ID int
}

type Edge struct {
    Source int
    Destination int
    Latency int
    Bandwidth int
}

type ContentRequest struct {
    UserID int
    ContentID int
    SourceServer int
    DestinationServer int
    BandwidthRequired int
}

type NetworkGraph struct {
    Nodes []Node
    Edges []Edge
}

func OptimizeNetwork(networkGraph NetworkGraph, requests []ContentRequest) (map[int][]int, []int) {
    // Your implementation here
}
```

**Scoring:**

The solution will be evaluated based on:

1.  **Correctness:**  Does the algorithm correctly route requests while respecting bandwidth constraints and minimizing latency?
2.  **Performance:**  How efficiently does the algorithm handle large graphs and request volumes?  Solutions will be tested with a variety of test cases with varying sizes.
3.  **Code Quality:** Is the code well-structured, readable, and maintainable?
4.  **Edge Case Handling:** Does the algorithm correctly handle cases where no feasible path exists?

Good luck! This is intended to be a very challenging problem, requiring a solid understanding of graph algorithms, optimization techniques, and Go programming.
