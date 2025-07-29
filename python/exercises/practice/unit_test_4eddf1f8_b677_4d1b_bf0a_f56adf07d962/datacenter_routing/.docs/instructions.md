## Question: Optimizing Inter-Datacenter Traffic Routing

### Question Description

A large, geographically distributed company operates `N` datacenters across the globe. Each datacenter `i` contains a certain number of servers denoted by `servers[i]`. These datacenters frequently need to communicate with each other, transferring large volumes of data. The cost of transferring data between two datacenters depends on the network latency between them and the amount of data being transferred. The company wants to minimize its overall inter-datacenter communication cost.

You are given a matrix `latency[N][N]` representing the network latency between each pair of datacenters. `latency[i][j]` denotes the latency between datacenter `i` and datacenter `j`.  This matrix is symmetric, i.e., `latency[i][j] = latency[j][i]`. The diagonal elements `latency[i][i]` are always 0.

Additionally, you are given a matrix `traffic[N][N]` representing the amount of data (in GB) that needs to be transferred between each pair of datacenters. `traffic[i][j]` represents the amount of data to be transferred *from* datacenter `i` *to* datacenter `j`. Note that `traffic[i][j]` may not be equal to `traffic[j][i]`.

Currently, all data is transferred directly between the source and destination datacenters.  The company is considering using intermediate datacenters to route some traffic to potentially reduce the overall cost.

**Your task is to determine the optimal routing strategy for minimizing the total inter-datacenter communication cost.**

**Cost Calculation:** The cost of transferring `x` GB of data between datacenters `i` and `j` is `x * latency[i][j]`. If data is routed through intermediate datacenters, the cost is the sum of the costs of each hop. For example, routing `x` GB from datacenter `i` to datacenter `j` via datacenter `k` incurs a cost of `x * latency[i][k] + x * latency[k][j]`.

**Constraints:**

*   `1 <= N <= 100` (Number of datacenters)
*   `0 <= servers[i] <= 10^6` (Number of servers in each datacenter)
*   `0 <= latency[i][j] <= 1000` (Network latency between datacenters)
*   `0 <= traffic[i][j] <= 10^3` (Data transfer volume in GB)
*   The solution should be computationally efficient, aiming for a time complexity better than O(N^4).  Solutions with higher complexity might time out on larger test cases.
*   You need to output a matrix `routing[N][N][N]`. `routing[i][j][k]` represents the amount of traffic (in GB) from datacenter `i` to datacenter `j` that should be routed through datacenter `k`. If no traffic from `i` to `j` should be routed through `k`, then `routing[i][j][k] = 0`. The remaining traffic `traffic[i][j] - sum(routing[i][j][:])` should be routed directly from `i` to `j`.
*   The sum of all `routing[i][j][k]` for a fixed `i` and `j` must be less than or equal to `traffic[i][j]`.

**Output:**

A three-dimensional matrix `routing[N][N][N]` representing the optimal routing strategy. The values in the matrix can be floating-point numbers to represent partial routing. The total cost calculated based on your `routing` matrix should be minimized as much as possible.

**Scoring:**

Your solution will be evaluated based on the total communication cost achieved by your routing strategy. Lower cost will result in a higher score. The solution with the lowest cost across all test cases will be considered the best. The correctness of your solution will be verified before calculating the cost.
