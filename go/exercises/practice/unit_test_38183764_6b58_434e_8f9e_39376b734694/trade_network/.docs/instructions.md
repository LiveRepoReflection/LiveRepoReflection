Okay, here's a challenging Go coding problem description for a programming competition, aimed at a difficulty level similar to LeetCode Hard.

## Project Name

`IntergalacticTradeNetwork`

## Question Description

The Intergalactic Trade Network (ITN) is a complex system connecting various planets through wormholes. Each planet has its own production and consumption needs for a set of goods. The ITN aims to optimize the flow of goods between planets to maximize overall trade efficiency and minimize transportation costs.

You are tasked with implementing a core component of the ITN: a system that, given the network topology, planet demands and supplies, and wormhole transportation costs, determines the optimal flow of goods to satisfy demand while minimizing total cost.

**Specifics:**

1.  **Network Representation:** The ITN is represented as a directed graph. Planets are nodes, and wormholes are directed edges. Each wormhole has a specific transportation cost per unit of goods.

2.  **Goods:** There are `N` types of goods circulating within the network. Each planet has a demand (positive value) or supply (negative value) for each type of good.

3.  **Wormhole Capacity:** Each wormhole has a maximum capacity for each good, representing the maximum amount of that good that can be transported through the wormhole.

4.  **Optimization Goal:** The objective is to find a flow of goods along the wormholes that satisfies all planet demands (or minimizes unmet demand if full satisfaction is impossible) while minimizing the total transportation cost.  The cost is the sum of (flow through each wormhole * cost per unit for that wormhole) across all wormholes and all goods.

5.  **Constraints:**

    *   The number of planets will not exceed 100.
    *   The number of goods will not exceed 10.
    *   The number of wormholes will not exceed 500.
    *   Planet demands and supplies will be integers.
    *   Wormhole costs and capacities will be positive integers.
    *   The sum of all demands for each good across all planets should equal the sum of all supplies for that good (total demand = total supply). If it doesn't, your algorithm should minimize unmet demand penalties (defined below).
    *   It is possible that a solution does not exist where all demands can be met.

6.  **Unmet Demand Penalty:** If a planet's demand for a particular good cannot be fully satisfied, there will be a penalty. The penalty is a fixed cost `P` per unit of unmet demand. You should minimize the sum of the transportation cost and the unmet demand penalty. The value of `P` will be given as part of the input.

7.  **Input:**

    *   Number of planets `numPlanets` (integer). Planets are numbered from 0 to `numPlanets - 1`.
    *   Number of goods `numGoods` (integer). Goods are numbered from 0 to `numGoods - 1`.
    *   A 2D array `demandSupply` of size `numPlanets x numGoods`, where `demandSupply[i][j]` represents the demand/supply of planet `i` for good `j`.  Positive values indicate demand; negative values indicate supply.
    *   A 2D array `wormholes` representing the directed graph. Each row represents a wormhole with the format: `[sourcePlanet, destinationPlanet, cost, capacity_good_0, capacity_good_1, ..., capacity_good_(numGoods-1)]`.  `sourcePlanet` and `destinationPlanet` are planet indices. `cost` is the transportation cost per unit of goods. `capacity_good_k` is the capacity of the wormhole for good `k`.
    *   Unmet demand penalty `P` (integer).

8.  **Output:**

    *   The minimum total cost (transportation cost + unmet demand penalty) as an integer.

**Judging Criteria:**

*   Correctness: Your solution must produce the correct minimum total cost for all test cases.
*   Efficiency: Your solution must be efficient enough to handle the given input sizes within a reasonable time limit.  Consider algorithmic complexity and optimization techniques.
*   Handling Edge Cases: Your solution should gracefully handle various edge cases, such as disconnected networks, zero demands/supplies, zero capacities, and the inability to satisfy all demands.

This problem requires knowledge of graph algorithms, network flow optimization, and careful consideration of constraints and edge cases. The optimization aspect makes it particularly challenging.  Good luck!
