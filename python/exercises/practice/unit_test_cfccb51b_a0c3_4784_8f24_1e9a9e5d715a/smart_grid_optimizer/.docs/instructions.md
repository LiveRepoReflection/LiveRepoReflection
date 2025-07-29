Okay, here's a challenging coding problem designed to be LeetCode Hard level, focusing on graph algorithms and optimization, with a real-world flavor:

**Project Name:** `SmartGridOptimizer`

**Question Description:**

You are tasked with optimizing the power distribution in a smart grid. The smart grid is represented as a graph where:

*   **Nodes:** Represent power substations. Each substation has a `capacity` (maximum power it can handle) and a `current_load` (amount of power it's currently handling).
*   **Edges:** Represent power lines between substations. Each power line has a `capacity` (maximum power it can transmit) and a `cost` (associated with transmitting one unit of power across it). The power line is directional.

You are given a set of `power_demands`. Each `power_demand` is a tuple `(source_substation, destination_substation, power_required)`. The goal is to satisfy all power demands while minimizing the total cost of power transmission across the grid.

**Constraints and Requirements:**

1.  **Capacity Constraints:** The power flowing through any substation cannot exceed its `capacity`. The power flowing through any power line cannot exceed its `capacity`.
2.  **Flow Conservation:** For each substation (except source and destination substations for power demands), the total power flowing into the substation must equal the total power flowing out of the substation.
3.  **Optimization:** Your solution must minimize the total cost of power transmission. The cost is calculated as the sum of (power transmitted through a power line \* cost of that power line) across all power lines used.
4.  **Real-world Considerations:**
    *   Substations can act as both sources and sinks of power.
    *   Multiple power demands can exist simultaneously.
    *   Power demands can be partially fulfilled if fulfilling them entirely is not feasible due to capacity limitations. In such cases, maximize the total amount of fulfilled power demands.
5.  **Efficiency:** The smart grid can be very large (thousands of substations and power lines). Your solution must be reasonably efficient (avoid brute-force approaches). Consider algorithmic complexity.
6.  **Edge Cases:**
    *   The graph may be disconnected.
    *   There may be no path between the source and destination substation for some power demands.
    *   The power demands may exceed the total capacity of the grid.
    *   Cycles may exist in the graph.

**Input:**

*   `substations`: A dictionary where keys are substation IDs (integers) and values are dictionaries with keys `'capacity'` (integer) and `'current_load'` (integer).
    Example: `{1: {'capacity': 100, 'current_load': 20}, 2: {'capacity': 150, 'current_load': 50}}`
*   `power_lines`: A list of tuples `(source_substation, destination_substation, capacity, cost)`.
    Example: `[(1, 2, 50, 2), (2, 3, 40, 1)]`
*   `power_demands`: A list of tuples `(source_substation, destination_substation, power_required)`.
    Example: `[(1, 3, 30), (2, 3, 20)]`

**Output:**

A tuple containing:

*   `total_cost`: The minimum total cost of power transmission to satisfy (or partially satisfy) the power demands.
*   `fulfilled_demands`: A dictionary where keys are tuples `(source_substation, destination_substation, power_required)` from the input `power_demands` and values are the amount of power actually delivered for that demand. If a demand is not fulfilled at all, the value is 0.

**Example:**

```python
substations = {
    1: {'capacity': 100, 'current_load': 20},
    2: {'capacity': 150, 'current_load': 50},
    3: {'capacity': 200, 'current_load': 30}
}
power_lines = [
    (1, 2, 50, 2),
    (2, 3, 40, 1)
]
power_demands = [
    (1, 3, 30),
    (2, 3, 20)
]

total_cost, fulfilled_demands = solve(substations, power_lines, power_demands)

# Expected output (values might slightly vary depending on the exact algorithm)
# total_cost: A number representing the optimal cost (e.g., 110)
# fulfilled_demands: {(1, 3, 30): 30, (2, 3, 20): 20}
```

**Hints (to guide toward intended difficulty):**

*   Consider using a min-cost max-flow algorithm (e.g., using the Edmonds-Karp or Successive Shortest Path algorithm) to solve the optimization problem. You'll need to represent the smart grid as a flow network.
*   You may need to create a super-source and a super-sink to handle multiple power demands efficiently.
*   Remember to account for the initial `current_load` of each substation when calculating available capacity.
*   Handle partial fulfillment of power demands gracefully.

This problem requires careful consideration of graph algorithms, network flow, optimization techniques, and edge cases, making it a challenging and sophisticated problem suitable for a high-level programming competition. Good luck!
