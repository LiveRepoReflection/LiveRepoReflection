## Project Name

```
TrafficSimulation
```

## Question Description

You are tasked with building a sophisticated traffic simulation engine for a busy city. The city is represented as a directed graph where nodes are intersections and edges are one-way streets. Each street has a capacity (maximum number of vehicles it can hold), a length (distance), and a speed limit.

Vehicles in the simulation are of different types (e.g., car, truck, bus), each with different speed characteristics and space requirements (size). The simulation runs in discrete time steps. At each time step, vehicles can move from one intersection to the next along a street if there is sufficient capacity on that street.

Your goal is to implement a traffic flow algorithm that optimizes the overall traffic flow in the city, minimizing congestion and travel times.  Specifically, you need to simulate the movement of vehicles through the city for a given number of time steps and report the average travel time of all vehicles that successfully reach their destination.

**Input:**

*   **City Graph:** A directed graph represented as a dictionary where keys are intersection IDs (integers) and values are lists of tuples. Each tuple represents a street originating from that intersection in the form `(destination_intersection_id, capacity, length, speed_limit)`.
*   **Vehicle Data:** A list of dictionaries, where each dictionary represents a vehicle with the following keys: `vehicle_id` (integer), `type` (string: "car", "truck", or "bus"), `start_intersection` (integer), `destination_intersection` (integer), `departure_time` (integer, representing the time step when the vehicle enters the simulation).  Each vehicle also implicitly has a `size`, where cars have size 1, trucks have size 2, and buses have size 3.
*   **Simulation Time:** An integer representing the total number of time steps to simulate.
*   **Routing Function:** You are provided with a function called `find_shortest_path(graph, start, end)` that finds the shortest path (in terms of total distance) between two intersections in the city graph, returning a list of intersection IDs representing the path, or `None` if no path exists. You **must** use this function to calculate the route for each vehicle, and you **cannot** modify it.

**Output:**

*   The average travel time (as a float) of all vehicles that successfully reach their destination within the simulation time. Travel time is defined as the difference between the arrival time at the destination and the departure time.
*   If no vehicles reach their destination, return -1.

**Constraints:**

*   You must use the provided `find_shortest_path` function for routing.
*   Vehicles cannot overtake each other on a street.
*   At each time step, a vehicle can move to the next intersection on its route if and only if:
    *   There is a street connecting the current intersection to the next intersection on the route.
    *   The street has enough remaining capacity to accommodate the vehicle's size.
*   A vehicle's speed is limited by the speed limit of the street it is currently on.  At each time step, a vehicle can travel a maximum distance equal to the street's speed limit. You can assume the time unit is chosen in such a way that vehicles can move their maximum speed limit distance in one time step.
*   Multiple vehicles can depart from the same intersection at the same time step.
*   The simulation ends after the specified number of time steps.  Vehicles that have not reached their destination by this time are considered unsuccessful.
*   Assume that the graph is valid (no self-loops, valid intersection IDs).
*   Vehicle IDs are unique.
*   If a vehicle reaches its destination at the same time step it departed, its travel time is 0.
*   You must handle edge cases gracefully, such as vehicles that cannot reach their destination due to lack of a path or full streets.

**Optimization Requirements:**

*   Your solution should be efficient and able to handle a large number of vehicles and intersections. Aim for a time complexity that avoids brute-force approaches. Consider using appropriate data structures to optimize the simulation.

**Example:**

```python
# Example City Graph
city_graph = {
    1: [(2, 5, 10, 60), (3, 3, 15, 40)],  # Intersection 1: (destination, capacity, length, speed_limit)
    2: [(4, 4, 8, 50)],
    3: [(4, 2, 12, 30)],
    4: []
}

# Example Vehicle Data
vehicles = [
    {"vehicle_id": 1, "type": "car", "start_intersection": 1, "destination_intersection": 4, "departure_time": 0},
    {"vehicle_id": 2, "type": "truck", "start_intersection": 1, "destination_intersection": 4, "departure_time": 2},
    {"vehicle_id": 3, "type": "bus", "start_intersection": 2, "destination_intersection": 4, "departure_time": 1}
]

simulation_time = 20

# Assume find_shortest_path is defined elsewhere and works correctly
def find_shortest_path(graph, start, end):
  # In a real implementation, this would be a proper shortest path algorithm
  # For this example, just return a simple path if it exists
  if start == 1 and end == 4:
    return [1, 2, 4]
  elif start == 2 and end == 4:
    return [2, 4]
  else:
    return None

# Expected (approximate) output:
# The exact travel time depends on the precise simulation logic.  
# In this example, assuming the cars can all travel at the speed limit,
# vehicle 1 should take distance(10+8) / speed(60 then 50) = 0.3 + 0.16 = ~1 time.
# vehicle 2 should take distance(10+8) / speed(60 then 50) = ~1 time.
# vehicle 3 should take distance(8) / speed(50) = ~0.16 time.
# average = 1.16/3= ~0.38

# Note: The actual calculation depends on the implementation.
# ~5.666666666666667 (This is just an example; the correct answer depends on your simulation)

```

This problem challenges you to combine graph algorithms, simulation techniques, and optimization strategies to model a complex real-world scenario.  Pay close attention to the constraints and edge cases to ensure your solution is robust and efficient.
