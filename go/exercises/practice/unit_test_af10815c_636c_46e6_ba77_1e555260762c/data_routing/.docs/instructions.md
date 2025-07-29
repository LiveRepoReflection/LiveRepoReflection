## Question: Optimizing Inter-Data-Center Routing

**Description:**

You are tasked with optimizing the routing of data packets across a network of interconnected data centers. Each data center houses a large number of servers and acts as a node in a graph. The goal is to minimize the average latency experienced by data packets traveling between any two servers, considering bandwidth constraints and the dynamic nature of network congestion.

**Specifically:**

1.  **Data Center Network:** The data center network is represented as an undirected, weighted graph.
    *   Nodes represent data centers, identified by unique integer IDs (1 to N).
    *   Edges represent network connections between data centers.
    *   Edge weights represent the latency (in milliseconds) of sending a packet across that connection.

2.  **Bandwidth Constraints:** Each connection (edge) has a limited bandwidth capacity, representing the maximum number of packets that can be transmitted concurrently without significant latency increase. Exceeding the bandwidth capacity of an edge results in packet loss, which is unacceptable.

3.  **Dynamic Congestion:** Each data center periodically reports its congestion level. Congestion at a data center adds to the latency of packets passing through it. This congestion latency is a function of the current number of packets passing through the data center.  Assume that you can get the congestion level from a function (see details below).

4.  **Packet Routing:** You need to implement a routing algorithm that determines the optimal path for data packets between any two servers located in different data centers. "Optimal" means minimizing the *total* latency, considering both the inherent network latency and the dynamic congestion latency at data centers along the path.

5.  **Server Identification:**  Each server is identified by a tuple `(data_center_id, server_id)`. The `server_id` is unique within a data center, but not globally.

**Function Signature:**

Implement a function `FindOptimalPath(network map[int]map[int]int, bandwidth map[int]map[int]int, source tuple, destination tuple) []int`.

*   `network`:  A map representing the network graph. The outer key is the source data center ID, the inner key is the destination data center ID, and the value is the latency (in ms) between the two data centers. `network[i][j]` gives the latency between data center `i` and `j`. If `network[i][j]` and `network[j][i]` both exist, their latencies must be equal. If `network[i][j]` does not exist, there is no direct connection between data center `i` and `j`.
*   `bandwidth`: A map representing the bandwidth capacity of each connection. Similar to `network`, `bandwidth[i][j]` gives the bandwidth between data center `i` and `j`. If `bandwidth[i][j]` and `bandwidth[j][i]` both exist, their bandwidths must be equal. If `bandwidth[i][j]` does not exist, there is no direct connection between data center `i` and `j`.
*   `source`: A tuple `(source_data_center_id, source_server_id)` representing the source server.
*   `destination`: A tuple `(destination_data_center_id, destination_server_id)` representing the destination server.

**Return Value:**

*   A slice of integers representing the optimal path, where each integer is a data center ID. The path should start with the source data center ID and end with the destination data center ID.
*   If no path exists between the source and destination data centers, return an empty slice.

**Constraints:**

*   The number of data centers (N) can be up to 1000.
*   The number of connections (edges) can be up to 5000.
*   Latency values are non-negative integers.
*   Bandwidth values are positive integers.
*   You can assume that a direct connection between two data centers exists in both `network` and `bandwidth` maps, or in neither. In other words, if `network[i][j]` exists, then `bandwidth[i][j]` also exists. If `network[i][j]` does not exist, then `bandwidth[i][j]` also does not exist.
*   Assume you have access to a function `GetCongestionLatency(data_center_id int, path []int) int` that estimates the congestion latency at a given data center, considering the current path being evaluated.  This function is external and its implementation is hidden. It returns a non-negative integer representing the congestion latency (in ms) at the given data center, for the current path. `path` is the tentative path being explored from the source to the data_center_id, inclusive. This function takes into account all existing traffic, therefore you should call this function as few times as possible and only on tentative paths being considered. This function has a significant computational cost, so avoiding unnecessary calls is critical for performance.
*   The total latency for any path must be a 64-bit integer.

**Optimization Requirements:**

*   The solution must be efficient in terms of both time and memory complexity.
*   The solution should avoid unnecessary computations, especially calls to `GetCongestionLatency`.
*   Consider using appropriate data structures and algorithms to optimize the search for the optimal path.
*   The solution will be judged based on its correctness and performance on a large set of test cases.

**Example:**

```go
network := map[int]map[int]int{
    1: {2: 10, 3: 20},
    2: {1: 10, 3: 30, 4: 5},
    3: {1: 20, 2: 30, 4: 15},
    4: {2: 5, 3: 15},
}

bandwidth := map[int]map[int]int{
    1: {2: 100, 3: 50},
    2: {1: 100, 3: 75, 4: 200},
    3: {1: 50, 2: 75, 4: 150},
    4: {2: 200, 3: 150},
}

source := tuple{1, 101}
destination := tuple{4, 401}

optimalPath := FindOptimalPath(network, bandwidth, source, destination)
// Expected Output (example, might vary based on GetCongestionLatency): [1, 2, 4] or [1, 3, 4]
```
