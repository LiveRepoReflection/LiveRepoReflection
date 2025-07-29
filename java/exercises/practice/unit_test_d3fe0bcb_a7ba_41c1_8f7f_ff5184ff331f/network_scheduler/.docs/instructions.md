## Project Name

`NetworkFlowScheduler`

## Question Description

You are tasked with designing a sophisticated scheduler for a network data center. The data center contains a set of `N` servers (numbered 0 to N-1) and `M` network switches (numbered 0 to M-1). Data flows need to be scheduled through this network.

Each server can send and receive data. Each network switch can route data between servers and other switches. The network topology is represented by an adjacency matrix `adjMatrix` of size `(N+M) x (N+M)`. `adjMatrix[i][j] = bandwidth` if there is a direct link between node `i` and node `j` with the given bandwidth. Otherwise, `adjMatrix[i][j] = 0` if there is no direct link. Note that the first `N` nodes are servers, and the next `M` nodes are switches. `adjMatrix[i][j]` can be different from `adjMatrix[j][i]`, representing asymmetric bandwidth.

You are given a list of `K` data flow requests. Each request `k` is defined by a tuple `(source, destination, dataSize, deadline)`, where:

*   `source`: The server ID (0 to N-1) that initiates the data flow.
*   `destination`: The server ID (0 to N-1) that should receive the data flow.
*   `dataSize`: The amount of data (in MB) that needs to be transferred.
*   `deadline`: The time (in seconds) by which the data transfer must be completed.

Your scheduler must determine a feasible schedule for these data flows, maximizing the number of completed flows before their deadlines. A flow is considered completed if all of its data is transferred from the source to the destination server within its deadline.

**Constraints:**

1.  **Bandwidth Sharing:** If multiple data flows are using the same link (between any two nodes i and j) at the same time, the bandwidth of that link is divided equally among the active flows. For instance, if `adjMatrix[i][j] = 100` and two flows are using this link concurrently, each flow gets a bandwidth of 50.  The bandwidth division is continuous, not discrete.

2.  **Path Selection:** You need to determine a path for each data flow from its source to its destination. The path can traverse multiple switches. You are free to choose any valid path (a path composed of existing links according to `adjMatrix`).

3.  **Non-preemptive:** Once a flow starts using a particular path, it cannot be interrupted or rerouted until it's fully completed.

4.  **Concurrency:** Multiple data flows can occur concurrently, potentially sharing network links.

5.  **Optimization:** Your primary goal is to maximize the *number* of data flows completed before their deadlines. Secondarily, you may consider minimizing the average completion time of the completed flows, but this is not strictly required for correctness.

6.  **Realistic Network:** The `adjMatrix` will be sparse, meaning that most servers and switches aren't directly connected. The maximum degree of any node (server or switch) is limited to 10.

7.  **Input Size:** `1 <= N <= 50`, `1 <= M <= 20`, `1 <= K <= 1000`. `1 <= dataSize <= 1000` (MB), `1 <= deadline <= 100` (seconds). Bandwidth will be integer between 1 and 1000 (MB/s).

8.  **No splitting:** Each flow must be routed along a single path from source to destination. You cannot split a flow into multiple sub-flows that take different paths.

**Input:**

*   `N`: Number of servers.
*   `M`: Number of network switches.
*   `adjMatrix`: A 2D integer array representing the adjacency matrix of the network topology.
*   `flows`: A list of data flow requests, where each request is a tuple `(source, destination, dataSize, deadline)`.

**Output:**

Return a list of integers representing the indices of the data flows (0-indexed) that can be successfully scheduled before their deadlines. The order of indices in the returned list does not matter.

**Example:**

(Simplified for brevity - a real example would be much larger)

```
N = 2
M = 1
adjMatrix = [
    [0, 0, 10],  // Server 0
    [0, 0, 5],   // Server 1
    [10, 5, 0]   // Switch 0
]

flows = [
    (0, 1, 10, 2), // source, destination, dataSize, deadline
    (1, 0, 5, 1)
]

// Possible Output (one valid solution):
// [0, 1]  (Both flows can be scheduled)

// Another possible adjMatrix example (Unidirectional)
// adjMatrix = [
//    [0, 0, 10],  // Server 0
//    [0, 0, 0],   // Server 1
//    [0, 5, 0]   // Switch 0
// ]
// In this case, flow 1 cannot be scheduled because there is no link for server 1 to switch 0.
```

**Grading:**

Your solution will be evaluated based on the number of data flows successfully scheduled within their deadlines across a set of test cases. Test cases will vary in network topology, flow characteristics, and the degree of contention for network resources. The more flows your scheduler can complete, the higher your score. Performance and efficient resource utilization will be critical to success.
