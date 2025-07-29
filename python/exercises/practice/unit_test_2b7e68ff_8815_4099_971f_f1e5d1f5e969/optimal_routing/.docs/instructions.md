## Project Name

`OptimalNetworkRouting`

## Question Description

You are tasked with designing an efficient routing algorithm for a large-scale communication network. The network consists of `N` nodes (numbered from 0 to N-1) and `M` bidirectional communication links. Each link connects two nodes and has a specific bandwidth capacity.

Due to increasing network congestion, some nodes are designated as "critical nodes". Routing traffic through critical nodes incurs a penalty cost proportional to the amount of traffic passing through them. Your algorithm must find the optimal path between any two nodes `start` and `end` that minimizes the total cost, considering both the path length (number of hops) and the penalty incurred by traversing critical nodes.

Specifically, given:

*   `N`: The number of nodes in the network.
*   `M`: The number of communication links.
*   `links`: A list of tuples `(u, v, bandwidth)`, where `u` and `v` are the node IDs connected by the link, and `bandwidth` is the bandwidth capacity of the link.
*   `critical_nodes`: A set of node IDs that are considered critical.
*   `start`: The starting node ID.
*   `end`: The destination node ID.
*   `penalty_factor`: A floating-point number representing the penalty multiplier for traffic passing through critical nodes.  The penalty is calculated as `penalty_factor * traffic_amount` for each critical node the route passes through. For simplicity, you can assume the traffic_amount to be 1.

Your task is to implement a function `find_optimal_route(N, links, critical_nodes, start, end, penalty_factor)` that returns a list of node IDs representing the optimal route from `start` to `end`. If no route exists, return an empty list.

**Constraints:**

*   `1 <= N <= 10000`
*   `0 <= M <= 50000`
*   `0 <= u, v < N`
*   `0 < bandwidth <= 1000`
*   `0 <= len(critical_nodes) <= N`
*   `0 <= start, end < N`
*   `0 <= penalty_factor <= 1000`
*   The graph represented by the links is undirected.
*   The solution must be reasonably efficient; brute-force approaches will likely time out.
*   There might be multiple optimal routes; return any one of them.
*   The route should not contain cycles.

**Evaluation Criteria:**

Your solution will be evaluated based on the correctness of the route, the total cost of the route (path length + critical node penalties), and the efficiency of the algorithm. Lower total cost routes are preferred.  Solutions that time out or exceed memory limits will receive a zero score.

**Bonus Challenge:**

Extend your solution to handle dynamic network changes, where links can be added or removed, and the set of critical nodes can be modified.  How would you adapt your algorithm to efficiently update the optimal routes in response to these changes?
