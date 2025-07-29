## The Intergalactic Resource Allocation Problem

**Question Description:**

The Intergalactic Federation (IGF) faces a critical resource allocation challenge. They have `N` planets under their control, each with a unique set of resources and needs.  The Federation needs to distribute `M` units of a vital energy resource, "Energium," across these planets to maximize the overall stability and prosperity of the Federation.

Each planet `i` has the following characteristics:

*   `resource_production[i]`: The amount of a specific rare resource Planet `i` produces annually.
*   `energium_need[i]`: The amount of Energium Planet `i` requires annually to function optimally.
*   `stability_coefficient[i]`: A coefficient representing the contribution of Planet `i` to the overall stability of the Federation. This coefficient is directly proportional to both the planet's resource production and the square of the Energium it receives, but only up to its Energium need. Receiving Energium beyond the planet's need provides no additional stability benefit. The stability contribution for planet `i` is defined as:

    *   `stability_coefficient[i] * resource_production[i] * min(energium_received[i], energium_need[i])^2`

The IGF also faces the following constraints:

1.  **Limited Energium:** The total Energium allocated cannot exceed `M`.
2.  **Integer Allocation:** Energium must be allocated in whole units (integers).
3.  **Non-Negativity:** Each planet must receive a non-negative amount of Energium.
4.  **Resource Dependence:** A planet's stability coefficient is significantly impacted by the amount of specific rare resource the planet produces.
5.  **Interplanetary Trade:** Planets can trade the rare resource with each other to increase the overall stability of the federation. Each planet `i` has a `trade_partners` list which contains a list of planets it can trade with. There is also a `trade_efficiency` matrix that gives efficiency of resource trade between any two planets. For example `trade_efficiency[i][j]` gives the efficiency of resource trade from planet `i` to planet `j`. If planet `i` sends one unit of rare resource to planet `j`, planet `j` effectively receives `trade_efficiency[i][j]` units of the rare resource.

Your task is to write a Go program that determines the optimal allocation of Energium to each planet to maximize the total stability of the Intergalactic Federation, considering the constraints and the resource trading.

**Input:**

*   `N`: The number of planets (integer).
*   `M`: The total amount of Energium available (integer).
*   `resource_production`: A slice of `N` integers representing the annual resource production of each planet.
*   `energium_need`: A slice of `N` integers representing the annual Energium need of each planet.
*   `stability_coefficient`: A slice of `N` floating-point numbers representing the stability coefficient of each planet.
*   `trade_partners`: A slice of slice of integers representing list of planets that can trade with the current planet.
*   `trade_efficiency`: A 2D slice of floating-point numbers representing efficiency of resource trade between any two planets.

**Output:**

*   A slice of `N` integers representing the optimal Energium allocation for each planet, maximizing the total stability of the Federation.

**Constraints:**

*   1 <= N <= 20
*   1 <= M <= 1000
*   1 <= resource\_production[i] <= 100
*   1 <= energium\_need[i] <= 50
*   0.1 <= stability\_coefficient[i] <= 10.0
*   0.1 <= trade\_efficiency[i][j] <= 1.0

**Optimization Requirements:**

*   The solution should be efficient enough to handle the given constraints.  Brute-force approaches may not be feasible.  Consider algorithmic optimizations.
*   The solution should return the optimal Energium allocation that maximizes the total stability, not just a feasible solution.

**Edge Cases:**

*   Consider the cases where M is very small (e.g., M = 1) or very large compared to the total Energium needs of the planets.
*   Handle cases where some planets have very low or zero resource production, impacting their stability contribution.
*   Consider edge cases of the trade partners and trade efficiency matrix.

**Real-World Practical Scenarios:**

*   Resource allocation problems are common in various domains, such as cloud computing (allocating resources to VMs), logistics (distributing goods), and finance (portfolio optimization). This problem abstracts a common challenge in a complex system.

**System Design Aspects:**

*   The solution should be well-structured and modular, allowing for future extensions or modifications (e.g., adding new types of resources or constraints).

Good luck, programmer! The fate of the Intergalactic Federation rests in your hands!
