Okay, here is a challenging coding problem designed to be similar to LeetCode Hard difficulty, focusing on algorithmic efficiency and real-world application.

## Problem: Optimal Supply Chain Routing

### Question Description

A large multinational corporation, "GlobalMart," is restructuring its supply chain network to minimize transportation costs. GlobalMart has a set of `N` warehouses and `M` retail stores distributed across the globe. Each warehouse has a limited supply of goods, and each retail store has a specific demand.

Your task is to design an algorithm that determines the optimal routing of goods from warehouses to retail stores, minimizing the total transportation cost while satisfying all demands and respecting warehouse capacities.

**Input:**

*   `N`: The number of warehouses (1 <= N <= 500).
*   `M`: The number of retail stores (1 <= M <= 500).
*   `capacities`: A list of integers of length `N`, where `capacities[i]` represents the maximum supply of goods available at warehouse `i`.
*   `demands`: A list of integers of length `M`, where `demands[j]` represents the required demand of goods at retail store `j`.
*   `costs`: A 2D list of integers of size `N x M`, where `costs[i][j]` represents the cost of transporting one unit of goods from warehouse `i` to retail store `j`.

**Output:**

A 2D list of integers of size `N x M`, representing the optimal flow of goods. `flow[i][j]` indicates the number of goods to be transported from warehouse `i` to retail store `j`. If no feasible solution exists (i.e., it's impossible to satisfy all demands given the warehouse capacities), return `None`.

**Constraints and Requirements:**

1.  **Feasibility:** The total supply from all warehouses must be greater than or equal to the total demand from all retail stores. If the total supply is less than the total demand, there is no feasible solution.
2.  **Capacity Constraints:** The total flow from each warehouse `i` must not exceed its capacity `capacities[i]`.
3.  **Demand Constraints:** The total flow to each retail store `j` must satisfy its demand `demands[j]`.
4.  **Non-negativity:** The flow `flow[i][j]` must be a non-negative integer.
5.  **Minimization:** The algorithm must minimize the total transportation cost, which is calculated as the sum of `flow[i][j] * costs[i][j]` for all `i` and `j`.
6.  **Efficiency:** The algorithm should be efficient enough to handle input sizes up to `N = 500` and `M = 500` within a reasonable time limit (e.g., a few seconds).  Solutions with high time complexity will likely time out.
7.  **Integer Flow:** You must return integer flow values. Fractional flows are not allowed in the solution.

**Example:**

```
N = 2
M = 2
capacities = [100, 50]
demands = [70, 80]
costs = [[2, 3], [4, 1]]

# Possible Optimal Solution:
# flow = [[70, 30], [0, 50]]

# Explanation:
# Warehouse 0 sends 70 units to retail store 0 and 30 units to retail store 1.
# Warehouse 1 sends 0 units to retail store 0 and 50 units to retail store 1.
# Total cost = (70 * 2) + (30 * 3) + (0 * 4) + (50 * 1) = 140 + 90 + 0 + 50 = 280

```

**Hints:**

*   Consider using network flow algorithms like the Min-Cost Max-Flow algorithm. Specifically, the successive shortest path algorithm is a strong contender.
*   Carefully handle the constraints to ensure feasibility and optimality.
*   Think about how to represent the problem as a network flow graph.  Nodes are warehouses and stores, edges represent the flow of goods, and edge weights represent the cost of transportation. Add a source and sink node to complete the network.
*   Pay attention to potential integer overflow issues if using large capacities, demands, or costs.
*   Consider the time complexity of your chosen algorithm. A naive approach may not be efficient enough.

This problem requires a good understanding of network flow algorithms and the ability to apply them to a practical scenario. Good luck!
