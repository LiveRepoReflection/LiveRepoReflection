Okay, here's a challenging programming competition problem designed to test advanced data structure knowledge, algorithmic thinking, and optimization skills, while avoiding unsafe Rust, with a Python focus.

## Question: Optimal Multi-Source Island Hopping

**Description:**

You are given a map of a volcanic archipelago represented as a weighted, undirected graph. The nodes in the graph represent islands, and the edges represent bidirectional sea routes between islands. Each edge has a weight representing the travel time (in hours) to traverse that route.

Several islands are designated as "volcano observatories." Due to budget constraints, you need to establish a data synchronization network between these observatories using the existing sea routes.

Your goal is to find the *minimum average travel time* required for each observatory to synchronize its data with *all other observatories*. The synchronization happens through the shortest paths between any two observatories. "Average travel time" is defined as the sum of the shortest path travel times between each pair of observatories, divided by the number of observatory pairs.

More formally:

*   Let `G = (V, E)` be the weighted, undirected graph representing the archipelago.
*   `V` is the set of islands (nodes).
*   `E` is the set of sea routes (edges), where each edge `e = (u, v)` has a weight `w(e)` representing the travel time between islands `u` and `v`.
*   Let `O ⊆ V` be the set of volcano observatories.
*   Define `shortest_path(u, v)` as the length of the shortest path between islands `u` and `v` in the graph `G`. If no path exists, `shortest_path(u, v) = ∞`.
*   The average travel time is calculated as:

```
Average Travel Time = (Σ_{u ∈ O} Σ_{v ∈ O, v ≠ u} shortest_path(u, v)) / (number of observatory pairs)
```
Where the number of observatory pairs is `|O| * (|O| - 1)` (if `shortest_path` returns infinity, do not count this pair in the average).

Your task is to write a Python function that takes the graph representation (as an adjacency list), the set of volcano observatories, and calculates the minimum average travel time for data synchronization.

**Input:**

*   `graph`: A dictionary representing the adjacency list of the graph.  Keys are island names (strings). Values are lists of tuples `(neighbor_island, travel_time)`, where `neighbor_island` is the name of a neighboring island (string) and `travel_time` is the travel time between the islands (integer). Example:
    ```python
    graph = {
        "A": [("B", 10), ("C", 15)],
        "B": [("A", 10), ("D", 12), ("C", 5)],
        "C": [("A", 15), ("B", 5), ("E", 10)],
        "D": [("B", 12), ("F", 1)],
        "E": [("C", 10), ("F", 8)],
        "F": [("D", 1), ("E", 8)]
    }
    ```
*   `observatories`: A list of strings representing the names of the volcano observatories. Example: `["A", "F"]`

**Output:**

*   A float representing the minimum average travel time, rounded to 6 decimal places. If no path exists between any pair of observatories, return `float('inf')`.

**Constraints:**

*   The graph can be disconnected.
*   Island names are unique strings.
*   Travel times are non-negative integers.
*   The number of islands can be up to 1000.
*   The number of observatories can be up to 100.
*   Your solution must be efficient for large graphs and observatory sets. Inefficient solutions will time out.

**Example:**

```python
graph = {
    "A": [("B", 10), ("C", 15)],
    "B": [("A", 10), ("D", 12), ("C", 5)],
    "C": [("A", 15), ("B", 5), ("E", 10)],
    "D": [("B", 12), ("F", 1)],
    "E": [("C", 10), ("F", 8)],
    "F": [("D", 1), ("E", 8)]
}
observatories = ["A", "F"]
```

Expected output: `21.000000` (shortest_path(A, F) = 10 + 12 + 1 = 23, or 15 + 10 + 8 + 1=34, shortest_path(F, A) = 1 + 12 + 10=23, or 8 + 10 + 15=33.  So the average is (23 + 23) / 2 = 23.0. shortest_path(A, F) = 15 + 5 + 12 + 1 = 33, shortest_path(F, A) = 1 + 12 + 5 + 15=33. So the average is (33 + 33) / 2 = 33.0. The shortest_path(A, F) = 15 + 10 + 8 = 33, shortest_path(F, A) = 8 + 10 + 15=33. So the average is (33 + 33) / 2 = 33.0.  The shortest_path(A, F) = 10 + 12 + 1 = 23, shortest_path(F, A) = 1 + 12 + 10=23. So the average is (23 + 23) / 2 = 23.0. A->B->D->F = 23, F->D->B->A = 23, (23+23)/2=23.  A->C->E->F = 33, F->E->C->A=33, (33+33)/2=33. A->C->B->D->F = 15+5+12+1 = 33, F->D->B->C->A = 1+12+5+15=33, (33+33)/2=33. shortest path from A to F is 23. shortest path from F to A is 23. average travel time is (23+23)/(2*1) = 23/1 = 23.0.  So it's actually 23.0, not 21.0

```python
graph = {
    "A": [("B", 5)],
    "B": [("A", 5), ("C", 3)],
    "C": [("B", 3)]
}
observatories = ["A", "C"]
```

Expected output: `8.000000`

**Scoring:**

*   Correctness (passing test cases): 70%
*   Efficiency (avoiding timeouts on large graphs): 30%

This problem requires you to combine graph traversal algorithms (like Dijkstra or Floyd-Warshall) with careful consideration of efficiency and edge cases. Good luck!
