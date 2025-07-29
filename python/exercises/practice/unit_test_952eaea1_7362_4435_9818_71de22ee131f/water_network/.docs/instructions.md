## Problem: Optimal Water Distribution Network

**Description:**

You are tasked with designing a water distribution network for a newly developed city. The city consists of `N` buildings, numbered from 1 to `N`. There is a central water reservoir (node 0) that can supply water to the buildings. You are given a list of possible connections between buildings and the reservoir, each with an associated cost. Your goal is to design a network that ensures every building receives water while minimizing the total cost.

You are provided with the following information:

*   `n`: An integer representing the number of buildings in the city (numbered 1 to n).
*   `pipes`: A list of tuples, where each tuple `(building1, building2, cost)` represents a possible pipe connection. `building1` and `building2` are integers representing the building numbers connected by the pipe, and `cost` is a non-negative integer representing the cost of installing that pipe. Building numbers can range from 1 to `n`. The special building 0 represents the water reservoir.
*   Some buildings may not be initially connected and need to be connected using available pipes.

Design an algorithm to find the minimum cost to connect all buildings to the central reservoir. If it is impossible to connect all buildings to the reservoir, return -1.

**Constraints:**

*   `1 <= n <= 10^5`
*   `0 <= len(pipes) <= 10^5`
*   `0 <= building1, building2 <= n`
*   `0 <= cost <= 10^5`
*   There can be multiple pipes connecting the same two buildings, however only the smallest cost is relevant.

**Optimization Requirement:**

The solution should be optimized for both time and space complexity. Solutions with high time complexity might not pass all test cases.

**Edge Cases to Consider:**

*   Empty city (`n` = 0): Should return 0.
*   No pipes available: Return -1 if n > 0.
*   Disconnected components: Return -1 if the city cannot be fully connected.
*   Cycles in the network: Ensure the algorithm does not get stuck in cycles.
*   Duplicate pipes with different costs: Consider only the pipe with the minimum cost.

**Example:**

```
n = 3
pipes = [(0, 1, 1), (1, 2, 2), (2, 3, 3), (0, 3, 4)]
```

In this example, the optimal solution is to use pipes (0, 1, 1), (1, 2, 2), and (0, 3, 4).  Total cost = 1 + 2 + 3 = 6.

**Challenge:**

Find an efficient algorithm to solve this problem. Consider using appropriate data structures and algorithms like graphs, minimum spanning trees, and disjoint set union (DSU) to achieve optimal performance.
