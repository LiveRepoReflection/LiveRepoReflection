## Question: Optimal Intermodal Route Planning

**Problem Description:**

You are tasked with designing an efficient route planning system for intermodal transportation, combining different modes of transport like trains, trucks, ships, and airplanes to move goods between various cities.

**Input:**

The input consists of the following:

1.  **Cities:** A list of `N` cities represented by unique string identifiers (e.g., "New York", "London", "Tokyo").
2.  **Transportation Modes:** A set of allowed transportation modes: `{"train", "truck", "ship", "airplane"}`.
3.  **Connections:** A list of directed connections between cities. Each connection is represented by a tuple: `(city_A, city_B, mode, cost, time)`.
    *   `city_A`: The origin city (string).
    *   `city_B`: The destination city (string).
    *   `mode`: The transportation mode used for this connection (string, one of the allowed modes).
    *   `cost`: The cost of using this connection (integer).
    *   `time`: The time it takes to traverse this connection (integer).
4.  **Start City:** The origin city for the route (string).
5.  **End City:** The destination city for the route (string).
6.  **Budget:** An integer representing the maximum budget available for the entire route.
7.  **Time Limit:** An integer representing the maximum time allowed for the entire route.
8.  **Mode Restrictions:** A dictionary where keys are cities and values are sets of allowed modes for leaving that city. For example, `{"New York": {"truck", "train"}, "London": {"ship"}}` would mean that you can only use trucks or trains when leaving New York and only ships when leaving London. If a city is not present in this dictionary, all modes are allowed.

**Output:**

Your task is to find the optimal route from the `Start City` to the `End City` that satisfies the following constraints:

1.  The total cost of the route must not exceed the `Budget`.
2.  The total time of the route must not exceed the `Time Limit`.
3.  The route must respect the `Mode Restrictions` for each city.

The output should be a list of tuples, representing the sequence of connections used in the optimal route. Each tuple should be in the same format as the input connections: `(city_A, city_B, mode, cost, time)`.

If no route exists that satisfies all the constraints, return an empty list `[]`.

**Optimization Requirements:**

*   The primary optimization goal is to minimize the **total travel time**.  If multiple routes have the same minimum travel time, choose the one with the lowest cost.

**Constraints:**

*   `1 <= N <= 1000` (Number of cities)
*   `1 <= Number of Connections <= 5000`
*   `1 <= cost <= 1000`
*   `1 <= time <= 1000`
*   `1 <= Budget <= 10000`
*   `1 <= Time Limit <= 10000`
*   The graph of connections may not be fully connected.
*   Cycles are possible in the graph.
*   The same city can appear multiple times in the route.
*   The same connection can be used multiple times, but be aware that this may affect the overall cost and time.
*   Mode Restrictions dictionary may be empty.

**Example:**

```python
cities = ["A", "B", "C", "D"]
modes = {"train", "truck"}
connections = [
    ("A", "B", "train", 5, 10),
    ("A", "C", "truck", 3, 15),
    ("B", "D", "train", 7, 5),
    ("C", "D", "truck", 2, 8),
]
start_city = "A"
end_city = "D"
budget = 15
time_limit = 25
mode_restrictions = {}
```

A possible optimal route would be `[("A", "C", "truck", 3, 15), ("C", "D", "truck", 2, 8)]`.  This route has a total cost of 5 (3 + 2) which is less than the budget of 15, and a total time of 23 (15 + 8) which is less than the time limit of 25.  There might be other routes, but this one has the lowest time while staying within the budget.

**Scoring:**

Solutions will be judged on correctness and efficiency. Solutions that time out or exceed memory limits will receive a score of 0. Solutions that produce incorrect output will also receive a score of 0. Solutions will be tested against a variety of test cases, including large graphs, complex mode restrictions, and tight budget/time constraints.  Partial credit may be awarded based on the number of test cases passed.
