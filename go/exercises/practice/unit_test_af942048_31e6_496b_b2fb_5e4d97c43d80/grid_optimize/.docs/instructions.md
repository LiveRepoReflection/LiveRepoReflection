## Question: Optimal Meeting Point in a Power Grid

**Problem Description:**

A smart city is powered by a network of power substations. Due to increasing demand, the city council wants to build a new community center and connect it to the power grid. To minimize energy loss and construction costs, the council wants to find the optimal location to connect the community center to the grid.

The power grid is represented as a weighted, undirected graph. Each node in the graph represents a power substation, and each edge represents a power line connecting two substations. The weight of an edge represents the length of the power line.

You are given:

*   `n`: The number of power substations (nodes) in the grid, numbered from `0` to `n-1`.
*   `edges`: A list of edges, where each edge is represented as a tuple `(u, v, w)`, where `u` and `v` are the substation IDs connected by the edge, and `w` is the length (weight) of the power line between them.
*   `power_demands`: A list of integers, where `power_demands[i]` represents the power demand of substation `i`.
*   `max_capacity`: The maximum power any one substation can supply.

The community center can be built at any point in the city, including:

1.  At an existing substation location.
2.  Along an existing power line between two substations.

If the community center is built along an edge, you can consider it as adding a new node to the graph that divides the edge into two new edges. The distances of the new edges are proportional to the location of the community center along the original edge. The new node ID should be n.

Your task is to determine the optimal location for the community center that minimizes the **maximum load** on any single substation in the power grid after connecting the community center. Assume the community center has a constant power demand of `community_demand`.

The load on a substation is defined as the total power flowing *through* that substation. The total power flowing through a substation is equal to the sum of all power demands of the substations it supplies, plus the community center's demand if it's supplied by that substation.

Power is supplied from a substation to another substation via the shortest path. The community center should be supplied by the substation that minimizes the maximum load on any substation.

**Constraints:**

*   1 <= `n` <= 200
*   0 <= `u`, `v` < `n`
*   1 <= `w` <= 1000
*   0 <= `power_demands[i]` <= 50
*   1 <= `community_demand` <= 100
*   1 <= `max_capacity` <= 10000
*   The graph is connected.
*   There are no self-loops or duplicate edges.
*   The power grid is bidirectional.

**Output:**

Return the minimum possible maximum load on any substation in the grid, rounded up to the nearest integer, after connecting the community center optimally. If any substation has a load exceeding `max_capacity`, return -1.

**Example:**

```
n = 4
edges = [[0, 1, 1], [0, 2, 5], [1, 2, 2], [1, 3, 1]]
power_demands = [10, 12, 15, 8]
community_demand = 10
max_capacity = 40
```

In this example, the optimal location might be at substation 1.

**Challenge:**

*   The number of possible locations for the community center is infinite along each edge. Finding the absolute optimal location requires careful consideration.
*   Efficiently calculating the shortest paths between all pairs of nodes in the graph is crucial.
*   Calculating the loads on each substation for a given community center location and supply path requires careful accounting.
*   The solution must handle cases where the power demand exceeds the maximum capacity of a substation, leading to an infeasible solution.
*   The graph may not be sparse.
