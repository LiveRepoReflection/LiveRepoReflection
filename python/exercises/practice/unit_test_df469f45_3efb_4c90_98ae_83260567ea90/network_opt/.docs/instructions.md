## Project Name

`NetworkTopologyOptimization`

## Question Description

You are tasked with designing an optimal network topology for a distributed system. The system consists of `n` nodes, each performing a specific computation. The goal is to connect these nodes in a way that minimizes the average latency between any two nodes while considering node processing capacity and network bandwidth constraints.

The network is represented as a graph, where nodes are vertices and connections between nodes are edges. Each node `i` has a processing capacity `p_i`, representing the amount of data it can process per unit time. Each connection (edge) between nodes `i` and `j` has a bandwidth `b_{ij}`, representing the amount of data that can be transmitted per unit time.

The latency between two nodes `i` and `j` is defined as the sum of:
1.  Processing Latency: Data sent from node `i` must be processed by node `i` before transmission. This latency is inversely proportional to the node's processing capacity. Let `d` be the data sent. Processing latency is `d / p_i`
2.  Transmission Latency: The latency incurred when sending data over a connection. This latency is inversely proportional to the bandwidth of the connection.  Let `d` be the data sent. Transmission latency is `d / b_{ij}`.

When data is sent across multiple hops, the total latency is the sum of processing and transmission latencies along the shortest path between two nodes.

Your task is to design a network topology (determine which nodes to connect with edges and the bandwidth of each edge) that minimizes the average latency between all pairs of nodes, subject to the following constraints:

1.  **Connectivity:** All nodes must be reachable from each other (the graph must be connected).
2.  **Bandwidth Limits:**  Each edge `(i, j)` can have a bandwidth `b_{ij}` between a specified minimum `min_bandwidth` and a maximum `max_bandwidth`.  The bandwidth can be any real number within this range.
3.  **Cost Constraint:** Establishing a connection between two nodes `i` and `j` incurs a cost `c_{ij}`. The total cost of the network (sum of all `c_{ij}` for established connections) must not exceed a given budget `B`.
4.  **Node Degree Limit:** Each node can have at most `D` connections to other nodes. This limits the complexity and management overhead of each node.
5.  **Symmetry:** If there is a connection between node `i` and node `j`, then node `j` must also have a connection with node `i` with the same bandwidth. If `(i,j)` is in the graph, `(j,i)` must be in the graph and `b_{ij} == b_{ji}`.

You are given the following inputs:

*   `n`: The number of nodes in the system.
*   `p`: A list of `n` integers representing the processing capacities `p_i` of each node.
*   `c`: A `n x n` matrix representing the cost `c_{ij}` of establishing a connection between nodes `i` and `j`. Note that `c[i][i] = 0` and `c[i][j] = c[j][i]`. If there is no possible connection, `c[i][j] = infinity`.
*   `min_bandwidth`: The minimum bandwidth allowed for any connection.
*   `max_bandwidth`: The maximum bandwidth allowed for any connection.
*   `B`: The total budget available for establishing connections.
*   `D`: The maximum degree (number of connections) allowed for each node.
*   `data_size`: The amount of data transmitted between each pair of nodes for latency calculation. This value is constant across all node pairs.

You need to output:

*   A `n x n` matrix representing the adjacency matrix of the optimal network topology.  `adj[i][j] = b_{ij}` if there is a connection between node `i` and node `j`, and `adj[i][j] = 0` otherwise. The bandwidth `b_{ij}` should be a real number between `min_bandwidth` and `max_bandwidth`.

**Constraints:**

*   `2 <= n <= 50`
*   `1 <= p_i <= 1000`
*   `0 <= c_{ij} <= 1000` (or infinity if no connection is possible)
*   `1 <= min_bandwidth <= max_bandwidth <= 1000`
*   `1000 <= B <= 50000`
*   `1 <= D <= n - 1`
*   `1 <= data_size <= 100`

**Optimization Requirement:**

Your solution will be evaluated based on the average latency achieved across all pairs of nodes. The lower the average latency, the better your solution. Due to the complexity of the problem, finding a provably optimal solution is not required.  Focus on developing an efficient heuristic or approximation algorithm that yields good results within the time and memory constraints.

**Edge Cases:**

*   Consider cases where the budget `B` is too small to create a connected graph. In such cases, return a valid connected graph that minimizes average latency within the budget. If no connected graph can be created within the budget, return an all-zero adjacency matrix.
*   Handle cases where some nodes have very low processing capacity compared to others. The network design should account for these bottlenecks.
*   Consider scenarios where some connections are significantly more expensive than others.

**Algorithmic Efficiency Requirements:**

*   The algorithm should aim for a time complexity that is polynomial in `n`. Exponential-time solutions are unlikely to pass the test cases within the time limit.
*   Efficient data structures should be used to represent the graph and calculate shortest paths.

**Multiple Valid Approaches:**

There are several valid approaches to solving this problem, including:

*   Greedy algorithms: Start with an empty graph and iteratively add edges that provide the largest reduction in average latency per unit cost.
*   Simulated annealing: Start with a random graph and iteratively make small changes to the graph (add/remove edges, adjust bandwidth) based on a simulated temperature.
*   Genetic algorithms: Maintain a population of candidate graphs and evolve them over time through selection, crossover, and mutation.
*   Linear programming (with relaxation): Formulate the problem as an integer linear program and use a solver to find an optimal solution. However, due to the integer constraints, this approach may not be scalable to larger values of `n`.  Consider relaxing the integer constraints to obtain a feasible solution.

Choose an approach that balances solution quality with computational efficiency.

This problem requires a combination of graph algorithms, optimization techniques, and careful consideration of constraints and edge cases. Good luck!
