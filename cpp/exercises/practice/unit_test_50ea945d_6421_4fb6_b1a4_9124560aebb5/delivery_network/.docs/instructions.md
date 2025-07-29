Okay, here's a challenging C++ coding problem designed to test a wide range of skills.

**Project Name:** `OptimalDeliveryNetwork`

**Question Description:**

A national logistics company, "SwiftRoute," is optimizing its delivery network. The country is represented as a graph where cities are nodes and roads connecting cities are edges. Each road has a `distance` (in kilometers) and a `toll_cost` (in credits).

SwiftRoute needs to deliver a large number of packages from a central depot (city 0) to *every* other city in the country.  However, due to budget constraints, they want to minimize their *total* cost, where the total cost is a weighted sum of the total distance traveled and the total toll costs incurred.

Specifically, the total cost is calculated as:

`TotalCost = (TotalDistance * distance_weight) + (TotalTollCost * toll_weight)`

where `distance_weight` and `toll_weight` are given constants.

You are given the following inputs:

*   `num_cities`: An integer representing the number of cities in the country (numbered from 0 to `num_cities - 1`).
*   `roads`: A vector of tuples. Each tuple represents a road and contains the following information: `(city_u, city_v, distance, toll_cost)`. The roads are undirected.
*   `distance_weight`: A floating-point number representing the weight for the total distance.
*   `toll_weight`: A floating-point number representing the weight for the total toll costs.

Your task is to find the *minimum* possible `TotalCost` to deliver packages from the central depot (city 0) to *every* other city. This requires finding a set of paths from city 0 to each other city such that every other city is reachable from city 0, and the overall weighted cost is minimized.  The paths to different cities may share edges.

**Constraints and Requirements:**

1.  **Graph Representation:** You must efficiently represent the graph. Adjacency lists are highly recommended.
2.  **Connectivity:** The graph is guaranteed to be connected, meaning there is at least one path between any two cities.
3.  **Large Input:** `num_cities` can be up to 10,000. The number of `roads` can be up to 100,000.
4.  **Positive Values:** `distance` and `toll_cost` are positive integers.  `distance_weight` and `toll_weight` are positive floating-point numbers.
5.  **Efficiency:** Your solution must be efficient enough to handle large inputs within a reasonable time limit (e.g., a few seconds). Consider algorithmic complexity.  A naive solution that explores all possible paths will likely time out.
6.  **Optimal Solution:** The solution must guarantee finding the *absolute minimum* total cost.
7.  **Floating-Point Precision:** Be mindful of floating-point precision issues when calculating the `TotalCost`. Use appropriate data types (e.g., `double`) and consider using a small tolerance when comparing floating-point numbers.
8.  **Memory Usage:** Keep memory usage in mind, especially with larger graphs.

**Clarifications:**

*   You need to find a path from city 0 to *every other* city. This does *not* necessarily mean finding a single path that visits every city (a Hamiltonian path).
*   You are allowed to re-visit cities and roads.  The goal is to minimize the *total* cost, even if it means taking a slightly longer route to save on tolls, or vice-versa.
*   The output should be a single floating-point number representing the minimum `TotalCost`.

This problem requires a combination of graph algorithms (potentially a modified shortest-path algorithm like Dijkstra or A\*), careful optimization, and attention to detail regarding floating-point arithmetic. Good luck!
