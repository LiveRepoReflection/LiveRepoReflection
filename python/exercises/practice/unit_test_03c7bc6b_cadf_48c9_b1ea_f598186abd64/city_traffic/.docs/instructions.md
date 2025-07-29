## Project Name

`CityTrafficSim`

## Question Description

You are tasked with building a simplified traffic simulation for a city. The city is represented as a directed graph, where nodes are intersections and edges are roads connecting them. Each road has a *capacity* (maximum number of cars it can hold) and a *travel time* (time it takes to traverse the road when it's not congested).

The simulation runs in discrete time steps. At each time step, cars attempt to move from one intersection to another along the roads. The number of cars moving along a road is limited by its capacity. If more cars want to use a road than its capacity allows, only the capacity number of cars are allowed, and the rest are queued at the origin intersection. Queued cars have priority in the next time step.

Furthermore, each intersection has a *demand*. A positive demand represents cars originating at the intersection each time step. A negative demand represents cars leaving the city from the intersection each time step. The simulation should strive to satisfy demands at each intersection, prioritizing existing queued cars over new cars originating at the intersection.

**Input:**

*   `num_intersections`: An integer representing the number of intersections in the city (numbered from 0 to `num_intersections - 1`).
*   `roads`: A list of tuples, where each tuple `(u, v, capacity, travel_time)` represents a directed road from intersection `u` to intersection `v` with the specified `capacity` and `travel_time`.
*   `demands`: A list of integers, where `demands[i]` represents the demand at intersection `i`.
*   `simulation_steps`: An integer representing the number of simulation steps to run.

**Initial State:**

*   Initially, all roads are empty (no cars).
*   Initially, there are no cars queued at any intersection.

**Simulation Rules:**

For each time step:

1.  **Car Arrival:** Cars that have been traveling on roads for their respective `travel_time` arrive at their destination intersections. Update the car counts at the destination intersections.
2.  **Demand Fulfillment:** For each intersection:
    *   First, try to satisfy the *negative* demand (cars leaving the city). Remove cars from the intersection to meet the negative demand. If there are not enough cars at the intersection to meet the demand, remove all cars from the intersection.
    *   Then, add new cars originating from the intersection to meet positive demand. Any remaining unmet positive demand is discarded for that simulation step.
3.  **Road Usage:** For each road:
    *   Calculate the number of cars *wanting* to travel on the road. This is the sum of cars queued at the origin intersection from the previous time step, plus new cars originating at the intersection at the current simulation step. If negative demand was unfulfilled, also includes the amount that was unfulfilled.
    *   Limit the number of cars actually using the road to the road's `capacity`.
    *   Update the number of cars currently traveling on the road, and the number of cars queued at the origin intersection for the next time step.
    *   If the number of cars wanting to travel on the road exceeded the capacity, the excess cars remain queued at the origin intersection for the next time step.

**Output:**

A list of integers representing the number of cars present at each intersection at the *end* of the simulation (after all `simulation_steps` have been completed).

**Constraints:**

*   1 <= `num_intersections` <= 100
*   0 <= `len(roads)` <= 500
*   0 <= `u`, `v` < `num_intersections` for each road `(u, v, capacity, travel_time)`
*   1 <= `capacity` <= 50 for each road
*   1 <= `travel_time` <= 10 for each road
*   -50 <= `demands[i]` <= 50 for each intersection `i`
*   1 <= `simulation_steps` <= 100

**Optimization Requirements:**

*   The solution should be efficient enough to handle the maximum input sizes within a reasonable time limit (e.g., 10 seconds).  Naive implementations may time out. Consider data structures and algorithms for efficient graph traversal and car counting.

**Edge Cases:**

*   Roads can exist between the same two intersections in both directions.
*   An intersection can have a road to itself.
*   The graph may not be fully connected.
*   Demand fulfillment should prioritize cars that have been waiting in the queue.
*   If a negative demand can't be fully met, the unfulfilled amount doesn't carry over to the next simulation step. Only queued cars carry over.

**Example:**

```python
num_intersections = 3
roads = [(0, 1, 10, 2), (1, 2, 5, 1), (2, 0, 3, 3)]
demands = [5, -3, 0]
simulation_steps = 5

# Expected output (example - actual value will depend on the simulation):
# [15, 0, 0] # the values are just illustrative and will change based on the correct simulation logic.
```

The problem tests the ability to simulate a system with multiple interacting components, handle constraints, prioritize resources, and optimize for performance. The directed graph, demand fulfillment, capacity limitations, and travel times introduce complexities that require careful consideration of data structures and algorithmic choices.
