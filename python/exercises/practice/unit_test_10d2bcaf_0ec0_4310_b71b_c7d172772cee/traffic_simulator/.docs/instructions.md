## Question: Optimized Traffic Flow Simulation

### Question Description

You are tasked with building a highly optimized traffic flow simulation engine for a large metropolitan area. The city's road network is represented as a directed graph where nodes represent intersections and edges represent road segments connecting them. Each road segment has a `capacity` representing the maximum number of vehicles that can travel on it per unit time. Each road segment also has a `length`.

Vehicles originate from different source intersections and need to reach their respective destination intersections. Each vehicle has a `departure_time` and a `destination`.

Your goal is to simulate the traffic flow over a fixed time period `T` and determine the **average travel time** of all vehicles that successfully reach their destinations within the simulation period.

However, traffic congestion occurs when the number of vehicles attempting to use a road segment exceeds its `capacity` at any given time. When congestion occurs, the travel time on that road segment increases. Specifically, if at time `t`, the number of vehicles on road segment `e` exceeds its `capacity`, the travel time for all vehicles entering that segment at time `t` is multiplied by a `congestion_factor` (congestion_factor > 1). This increased travel time also propagates to subsequent road segments in their paths, potentially causing further congestion.

**Constraints:**

*   The road network can be very large (up to 10,000 intersections and 50,000 road segments).
*   The number of vehicles can also be very large (up to 100,000).
*   The simulation period `T` can be up to 1000 time units.
*   The simulation needs to be reasonably fast. Solutions that take excessively long will time out.
*   You are given the road network graph, vehicle information, road segment capacities and lengths, and the `congestion_factor`.
*   Vehicles that do not reach their destinations within the simulation period `T` should not be included in the average travel time calculation.
*   The time complexity of the solution is critical. Naive approaches will not pass the test cases.
*   Assume vehicles travel at a constant speed unless there is congestion. The base travel time on a road segment is the length of the road segment.

**Input:**

*   `graph`: A dictionary representing the road network. Keys are source intersections, and values are lists of tuples, where each tuple represents a road segment and contains the destination intersection, capacity, and length. E.g., `{1: [(2, 100, 5), (3, 50, 10)], 2: [(4, 75, 8)]}`. This means from intersection 1, there's a road to intersection 2 with capacity 100 and length 5, and another road to intersection 3 with capacity 50 and length 10.
*   `vehicles`: A list of tuples, where each tuple represents a vehicle and contains its source intersection, destination intersection, and departure time. E.g., `[(1, 4, 0), (2, 4, 2)]`.
*   `congestion_factor`: A float value greater than 1, representing the factor by which travel time increases during congestion.
*   `T`: The simulation period.

**Output:**

*   The average travel time of all vehicles that reach their destinations within the simulation period `T`. Return 0 if no vehicles reach their destination within `T`.

**Example:**

```python
graph = {
    1: [(2, 10, 5)],  # From 1 to 2, capacity 10, length 5
    2: [(3, 5, 10)],  # From 2 to 3, capacity 5, length 10
    3: []
}
vehicles = [(1, 3, 0), (1, 3, 2)] #Two cars travel from 1 to 3. One leaves at time 0 and the other at time 2
congestion_factor = 2.0
T = 30
```

In this example, if both vehicles reach their destination within T, and the first vehicle experiences congestion on the road from 2 to 3, while the second does not, the average travel time would be calculated accordingly.

**Judging Criteria:**

The solution will be judged based on:

*   Correctness: The solution must accurately simulate traffic flow and calculate the average travel time.
*   Efficiency: The solution must be efficient enough to handle large road networks and vehicle counts within a reasonable time limit.
*   Clarity: The code should be well-structured and easy to understand.

This problem requires you to combine graph algorithms (shortest path finding), discrete event simulation, and optimization techniques to achieve a feasible solution. Good luck!
