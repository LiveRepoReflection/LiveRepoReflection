## The Intergalactic Resource Allocation Problem

**Question Description:**

The Intergalactic Federation (IF) is responsible for managing resource distribution across its vast network of planets. Each planet has specific resource requirements and production capabilities. The IF has established a complex interplanetary transportation network to facilitate resource exchange.

You are tasked with developing an efficient resource allocation algorithm to minimize the overall transportation cost while fulfilling the resource demands of each planet.

**Specifics:**

1.  **Planets:** The IF consists of `N` planets, numbered from 0 to `N-1`.

2.  **Resources:** There are `M` types of resources, numbered from 0 to `M-1`.

3.  **Resource Needs:** Each planet `i` has a demand for each resource `j`, represented by `demand[i][j]`, indicating the required amount of resource `j` on planet `i`.  A negative value indicates a surplus (planet `i` *produces* this amount of resource `j`).

4.  **Transportation Network:** The transportation network is a directed graph where each planet is a node. A directed edge from planet `u` to planet `v` indicates a transportation route. The weight of the edge `(u, v)` is `cost[u][v][j]`, representing the cost of transporting one unit of resource `j` from planet `u` to `v`. If `cost[u][v][j]` is -1, it means there is no direct route between planet `u` and `v` for resource `j`.

5.  **Constraints:**
    *   All resource demands *must* be satisfied.
    *   Transportation is only allowed along the directed edges defined in the transportation network.
    *   Resource transportation is *not* instantaneous; it occurs over time.
    *   The total amount of resource `j` leaving a planet `u` for all other planets *must* be less than or equal to the amount of resource `j` produced on planet `u` plus any amount that reaches planet `u` through transportation.
    *   All values in `demand` and `cost` are integers.

6.  **Optimization Goal:** Minimize the total transportation cost. The total transportation cost is the sum of the cost of transporting each unit of each resource along each edge.

**Input:**

*   `N`: The number of planets (integer).
*   `M`: The number of resource types (integer).
*   `demand`: A 2D array of size `N x M`, where `demand[i][j]` represents the demand of resource `j` for planet `i` (integer).
*   `cost`: A 3D array of size `N x N x M`, where `cost[u][v][j]` represents the cost of transporting one unit of resource `j` from planet `u` to planet `v` (integer). `cost[u][v][j] = -1` means no direct path exists.

**Output:**

*   Return the minimum total transportation cost as an integer.
*   If it's impossible to satisfy all demands, return `-1`.

**Complexity Expectations:**

*   Your solution should be able to handle up to `N=50` planets and `M=10` resource types.
*   The algorithm should have an efficient runtime, aiming for a time complexity better than `O(N^5 * M)`.

**Edge Cases and Considerations:**

*   Disconnected components in the transportation network.
*   Planets with both resource surpluses and deficits.
*   Resource dependencies (some resources might be required to produce other resources, although this isn't explicitly part of the demand matrix, it can affect optimal transportation).
*   Cycles in the transportation network.
*   Optimal solutions might involve transporting resources through multiple intermediate planets.
*   Large integer values for resource demands and costs that might lead to overflow issues if not handled carefully.

This problem requires careful consideration of graph algorithms, optimization techniques (potentially linear programming or network flow algorithms), and efficient data structures to represent the interplanetary network and resource flow. Good luck!
