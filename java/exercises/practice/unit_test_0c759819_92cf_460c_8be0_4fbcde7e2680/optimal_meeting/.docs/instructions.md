## Question: Optimal Meeting Point

### Question Description

Imagine a city represented as a weighted, undirected graph where nodes are locations and edges represent roads with associated travel times (weights). A company with `N` employees, each located at a different node in the graph, needs to hold a meeting. The goal is to find the optimal meeting point - a node in the graph that minimizes the *maximum* travel time any employee has to undertake to reach it.

Formally:

*   **Graph:** `G = (V, E)`, where `V` is the set of locations (nodes) and `E` is the set of roads (edges). Each edge `e` in `E` has a weight `w(e)` representing the travel time.
*   **Employees:** `E = {e1, e2, ..., eN}`, where `ei` is the location (node) of the *i*-th employee. All employee locations are guaranteed to be unique.
*   **Meeting Point:** A node `m` in `V`.
*   **Distance:** `dist(u, v)` represents the shortest travel time (weighted path length) between nodes `u` and `v` in `G`.
*   **Objective:** Find a meeting point `m` that minimizes `max(dist(ei, m))` for all employees `ei` in `E`. In other words, minimize the maximum travel time any single employee must experience to attend the meeting.

**Input:**

*   `n`: The number of nodes in the graph (numbered from 0 to n-1).
*   `edges`: A list of edges represented as `int[][] edges`, where each `edges[i]` contains three integers: `[u, v, weight]`. This represents an undirected edge between nodes `u` and `v` with a travel time of `weight`.
*   `employeeLocations`: An array of `int[] employeeLocations` containing the node index of each employee.  The length of `employeeLocations` is `N`.

**Output:**

*   Return the node index of the optimal meeting point `m`. If multiple nodes achieve the same minimum maximum travel time, return the node with the smallest index.

**Constraints:**

*   `1 <= n <= 1000`
*   `0 <= edges.length <= n * (n - 1) / 2`  (representing a potentially dense graph)
*   `0 <= u, v < n` for each edge `[u, v, weight]`
*   `1 <= weight <= 1000` for each edge `[u, v, weight]`
*   `1 <= employeeLocations.length <= n`
*   All values in `employeeLocations` are unique and within the range `[0, n)`.
*   The graph is guaranteed to be connected.
*   The graph can have cycles.

**Optimization Requirements:**

*   Your solution must be efficient enough to handle large, potentially dense graphs within a reasonable time limit (e.g., a few seconds).  Brute-force solutions that calculate distances from every node to every employee location and find the minimum maximum distance will likely time out.
*   Consider using appropriate data structures and algorithms to optimize distance calculations.

**Edge Cases:**

*   The graph could be a tree, a complete graph, or something in between.
*   Edge weights can vary significantly.
*   The number of employees can be small (e.g., 1 or 2) or large (close to 'n').
*   There might be multiple optimal meeting points.  Return the one with the smallest index.

**System Design Aspects (Implicit):**

*   Consider how your solution would scale if the number of nodes, edges, or employees were significantly larger (e.g., millions). While you don't need to *implement* a distributed solution, thinking about scalability can influence your design choices (e.g., using graph data structures suitable for sparse graphs).
