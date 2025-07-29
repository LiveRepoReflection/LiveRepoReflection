Okay, here's a challenging Go coding problem designed to be LeetCode Hard level.

### Project Name

```
optimal-network-deployment
```

### Question Description

A large cloud provider, "NebulaCloud," is planning to deploy a new service across its global network of data centers. The network consists of `N` data centers, interconnected by `M` bidirectional communication links. Each data center `i` (indexed from 0 to N-1) has a specific processing capacity, represented by `capacity[i]`. Each communication link `j` (indexed from 0 to M-1) between data centers `u` and `v` has a latency, represented by `latency[j]`.  The latency between data centers `u` and `v` is only considered if there is a direct link connecting them.

NebulaCloud needs to select a subset of data centers to host the new service. Deploying the service in a data center incurs a fixed cost `deploymentCost`. However, the service benefits from being deployed in data centers that are well-connected and have high capacity.

The **utility** of deploying the service in a subset of data centers `S` is defined as follows:

1.  **Total Capacity:** The sum of the processing capacities of all data centers in `S`: `sum(capacity[i] for i in S)`.

2.  **Connectivity Bonus:** For each data center `i` in `S`, calculate the sum of the reciprocals of the latencies to all other data centers `j` in `S` that are directly connected to `i`.  If there is no direct connection between data center `i` and any other data center `j` in `S`, the connectivity bonus for data center `i` is zero. The connectivity bonus for a data center `i` is calculated as follows:

   `connectivityBonus[i] = sum(1 / latency[link_index] for j in S and link exists between i and j)`

   where `link_index` is the index of the communication link between i and j.

   The total connectivity bonus is the sum of the connectivity bonuses of all data centers in `S`.

3.  **Deployment Cost:** The total cost of deploying the service in all data centers in `S`: `len(S) * deploymentCost`.

The **overall utility** of deploying the service in subset `S` is:

`utility(S) = totalCapacity + totalConnectivityBonus - deploymentCost`

**Your Task:**

Write a function `OptimalDeployment(capacities []int, links [][]int, latencies []int, deploymentCost int) float64` that takes the following inputs:

*   `capacities`: An array of integers representing the processing capacity of each data center.
*   `links`: A 2D array of integers representing the bidirectional communication links. Each inner array `[u, v]` represents a link between data centers `u` and `v`.  Data center indices are 0-based.
*   `latencies`: An array of integers representing the latency of each communication link.  `latencies[i]` corresponds to the latency of the link `links[i]`.
*   `deploymentCost`: An integer representing the fixed cost of deploying the service in a single data center.

Your function should return the **maximum possible overall utility** that can be achieved by deploying the service in any subset of data centers.

**Constraints:**

*   `1 <= N <= 15` (Number of data centers)
*   `0 <= M <= N * (N - 1) / 2` (Number of links)
*   `1 <= capacities[i] <= 1000`
*   `1 <= latencies[j] <= 100`
*   `1 <= deploymentCost <= 500`

**Edge Cases and Considerations:**

*   The graph may not be fully connected.
*   Multiple links between the same two data centers are not allowed.
*   Zero latency is invalid and will not be present in the input.
*   The number of data centers is small enough to consider brute force or dynamic programming approaches, but the constant factors and floating-point precision need to be considered.
*   The `float64` result should be accurate to within a tolerance of `1e-6`.

**Example:**

```go
capacities := []int{100, 150, 200}
links := [][]int{{0, 1}, {1, 2}}
latencies := []int{10, 20}
deploymentCost := 50

result := OptimalDeployment(capacities, links, latencies, deploymentCost)
// Possible optimal solution is deploying in data centers {1,2}
// Total capacity = 150 + 200 = 350
// Connectivity bonus for 1 = 1/10 (link with 0 is not included because data center 0 is not in S)
// Connectivity bonus for 2 = 1/20
// Total connectivity bonus = 1/10 + 1/20 = 0.15
// Deployment cost = 2 * 50 = 100
// Overall utility = 350 + 0.15 - 100 = 250.15

// The function must return 250.15
```
Good luck! This problem requires careful consideration of all possible subsets and accurate calculation of the utility function. The small size of `N` allows for exploring all subsets, but the connectivity bonus calculation with floating-point numbers and the edge cases will make this a challenging problem.
