## Problem: Optimal Highway Construction

**Description:**

The nation of Algorithma is planning a massive highway construction project to connect its major cities and boost its economy. Algorithma consists of *N* cities, numbered from 1 to *N*. The government wants to build a highway network that satisfies the following requirements:

1.  **Connectivity:** Every city must be reachable from every other city using the highway network.

2.  **Budget Constraint:** The total cost of building the highway network must not exceed a given budget *B*.

3.  **Strategic Importance:** Certain cities are designated as "strategic hubs".  The shortest path (in terms of number of highway segments) between any two strategic hubs in the highway network must not exceed a maximum distance *D*.

4.  **Minimization of Environmental Impact:**  Building highways causes significant environmental damage. The government wants to minimize the maximum degree of any city in the highway network. The degree of a city is defined as the number of highways directly connected to it. (In other words, minimize the maximum number of highways that connect to any single city.)

You are given:

*   *N*: The number of cities in Algorithma.
*   *B*: The total budget for the highway construction.
*   *D*: The maximum allowed shortest path distance between any two strategic hubs.
*   `city_costs`: A list of tuples `(u, v, cost)`, where `u` and `v` are city numbers (1-indexed) and `cost` is the cost of building a highway directly between them. There can be multiple possible costs between two cities.
*   `strategic_hubs`: A list of city numbers that are designated as strategic hubs.

Your task is to find the highway network that satisfies all the given conditions and minimizes the maximum degree of any city in the network.

**Input:**

*   `N` (int): The number of cities.
*   `B` (int): The total budget.
*   `D` (int): The maximum allowed shortest path distance between any two strategic hubs.
*   `city_costs` (list of tuples): A list of tuples of the form `(u, v, cost)`, where `u` and `v` are city numbers, and `cost` is the cost of building a highway between them.
*   `strategic_hubs` (list of ints): A list of city numbers that are strategic hubs.

**Output:**

An integer representing the minimum possible maximum degree of any city in a valid highway network. If no valid highway network exists, return -1.

**Constraints:**

*   2 <= N <= 200
*   1 <= B <= 10000
*   1 <= D <= N
*   1 <= u, v <= N
*   1 <= cost <= 100
*   1 <= len(strategic_hubs) <= N
*   All cities are numbered starting from 1.

**Efficiency Requirements:**

Your solution must be efficient enough to handle the maximum input size within a reasonable time limit (e.g., a few seconds). Consider algorithmic complexity and data structure choices carefully.

**Example:**

```python
N = 5
B = 20
D = 2
city_costs = [(1, 2, 5), (1, 3, 7), (2, 3, 2), (2, 4, 4), (3, 5, 3), (4, 5, 6), (1,5,8)]
strategic_hubs = [1, 4, 5]

# Expected Output: 2
# Explanation: A possible solution is to build highways:
# 1-2 (cost 5)
# 2-3 (cost 2)
# 2-4 (cost 4)
# 3-5 (cost 3)
# Total cost: 14 <= 20
# Strategic hubs 1, 4, and 5 are connected with a maximum shortest path of 2.
# The maximum degree is 3 (city 2)

```
```python
N = 4
B = 5
D = 1
city_costs = [(1, 2, 5), (1, 3, 7), (2, 3, 2), (2, 4, 4), (3, 4, 6)]
strategic_hubs = [1, 4]

# Expected Output: -1
# Explanation: It's impossible to connect 1 and 4 within distance 1 with a cost less than or equal to 5
```
