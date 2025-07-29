## Project Name

```
NetworkOptimization
```

## Question Description

You are given a network of routers represented as a graph. Each router has a unique ID from `0` to `n-1`, where `n` is the total number of routers. The network topology is described by a list of bidirectional edges, where each edge represents a direct connection between two routers. Each router also has a certain processing *capacity* and a certain amount of *traffic* it needs to handle.

Your task is to optimize the network to minimize the **maximum traffic load** on any single router in the network. Traffic can be rerouted between routers, subject to the following constraints:

1.  **Capacity Constraint**: The total traffic passing through any router (including its original traffic) cannot exceed its capacity.
2.  **Flow Conservation**: For each router (except for source and destination routers), the total incoming traffic must equal the total outgoing traffic.
3.  **Traffic Splitting**: Traffic can be split and routed along multiple paths.
4. **Delay Minimization:** Each router has an associated *delay* cost per unit of traffic it forwards. The overall traffic flow should minimize the total delay across the network. The delay cost of a path is the sum of the delay costs of routers present on that path, multiplied by the total flow along that path.

You are given:

*   `n`: The number of routers.
*   `capacities`: An array of integers, where `capacities[i]` represents the processing capacity of router `i`.
*   `traffic`: An array of integers, where `traffic[i]` represents the initial traffic load of router `i`. Note: traffic[i] can be negative, which means that the router is a *source* of traffic (it needs to send out -traffic[i] amount of traffic). Positive traffic[i] means that the router is a *sink* of traffic (it needs to receive traffic[i] amount of traffic). traffic[i] = 0 means that this router acts as an intermediary.
*   `edges`: A list of lists, where each inner list `[u, v]` represents a bidirectional connection between router `u` and router `v`.
*   `delays`: An array of integers, where `delays[i]` represents the delay cost per unit of traffic of router `i`.

Your goal is to determine the optimal traffic flow through the network such that:

*   No router's traffic load exceeds its capacity.
*   The maximum traffic load on any router is minimized.
*   The total delay across the network is minimized.

Your function should return the minimized **maximum traffic load** on any router in the network, if a feasible solution exists. If no feasible solution exists, return `-1`.

**Constraints:**

*   `1 <= n <= 100`
*   `0 <= capacities[i] <= 1000`
*   `-1000 <= traffic[i] <= 1000`
*   `0 <= edges.length <= n * (n - 1) / 2`
*   `0 <= u, v < n`
*   `0 <= delays[i] <= 100`
*   The sum of `traffic` is guaranteed to be 0.

**Example:**

```
n = 4
capacities = [20, 20, 20, 20]
traffic = [-5, 5, 0, 0]
edges = [[0, 1], [1, 2], [0, 3], [3, 2]]
delays = [1, 1, 1, 1]
```

One possible optimal solution is to route 5 units of traffic from router 0 to router 1.
The maximum traffic load on any router is 5 (router 1's original traffic + 5 routed from router 0).

In this scenario, the function should return `5`.

**Note:**

*   This is a challenging optimization problem that may require knowledge of network flow algorithms, linear programming, or other optimization techniques.
*   You are free to use any standard Java libraries.
*   The input will always be valid according to the constraints. You do not need to perform extensive input validation.
*   The goal is to find a solution that minimizes the maximum traffic load. A solution that satisfies the capacity and flow conservation constraints but doesn't minimize the maximum traffic load will not be considered correct.
*   While aiming for the minimal maximum traffic load, you also need to minimize the overall delay.

This problem will require a combination of algorithmic thinking, data structure manipulation, and careful consideration of edge cases and constraints. Good luck!
