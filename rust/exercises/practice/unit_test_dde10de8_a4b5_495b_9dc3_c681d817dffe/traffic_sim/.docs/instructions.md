Okay, here's a challenging Rust coding problem designed to be difficult and sophisticated, incorporating various complex elements.

**Project Name:** `TrafficSim`

**Question Description:**

You are tasked with building a simplified, but highly efficient, traffic simulation engine for a city. The city is represented as a directed graph where nodes are intersections and edges are roads. Each road has a *capacity* (maximum number of vehicles it can hold) and a *speed limit*.

Vehicles enter the simulation at certain intersections (entry points) with predefined routes (sequences of intersections to traverse). Your simulation needs to manage the movement of these vehicles, adhering to road capacities and speed limits, and efficiently calculate the *travel time* for each vehicle to reach its destination.

The simulation proceeds in discrete time steps. At each time step, vehicles attempt to move along their routes. Movement is governed by the following rules:

1.  **Capacity Constraint:** A vehicle can only enter a road if the current number of vehicles on that road is strictly less than its capacity.
2.  **Speed Limit:** The time taken to traverse a road is equal to the road's length divided by the vehicle's current speed. The vehicle's current speed is capped by the road's speed limit.  For simplicity, assume all vehicles have the same maximum possible speed. Also, assume the vehicle's current speed is not relevant when calculating road occupancy.
3.  **Simultaneous Movement:** All vehicles attempt to move simultaneously. The movement of a vehicle from road A to road B in a given time step depends on road B having available capacity at the *beginning* of the time step.
4.  **Route Completion:** Once a vehicle reaches its destination intersection, it exits the simulation.

**Specific Requirements:**

*   **Data Structures:**
    *   You must use an adjacency list representation for the city graph.
    *   You must implement a custom priority queue (min-heap) to efficiently determine which vehicles are closest to their destinations at each time step. Use travel time as priority.
*   **Efficiency:** The simulation should be able to handle a large number of vehicles and intersections (e.g., 10,000+ vehicles, 1000+ intersections).  Therefore, algorithmic efficiency is crucial. Avoid unnecessary cloning or copying of large data structures.
*   **Concurrency:**  The simulation engine should be designed to take advantage of multi-core processors. Consider using `rayon` or other suitable concurrency libraries to parallelize the movement of vehicles across different parts of the city graph. Be mindful of data races.
*   **Accuracy:** The travel time calculated for each vehicle should be as accurate as possible, given the discrete nature of the simulation. You'll need to handle fractional travel times carefully.
*   **Edge Cases:**
    *   Handle cases where a vehicle's route is invalid (e.g., a path doesn't exist).
    *   Handle cases where a vehicle is stuck due to capacity constraints (i.e., cannot proceed to the next road on its route). In these cases, the vehicle should wait until capacity becomes available.
    *   Consider cases with very short/long roads.
*   **API:**
    You need to implement a `simulate` function with the following signature:

```rust
fn simulate(
    city_graph: &CityGraph,
    vehicles: Vec<Vehicle>,
    max_steps: u32,
) -> HashMap<VehicleId, f64>;
```

Where:

*   `CityGraph`: A struct representing the city's road network (adjacency list).
*   `Vehicle`: A struct representing a vehicle with an ID, route (vector of intersection IDs), maximum speed, and entry time to the simulation.
*   `VehicleId`: The unique ID of a vehicle.
*   `max_steps`: The maximum number of simulation steps to run.
*   The function returns a HashMap mapping each VehicleId to its total travel time (in simulation time units) or `f64::INFINITY` if the vehicle could not reach its destination within `max_steps`.

**Constraints:**

*   The number of intersections is limited to 1000.
*   The number of roads is limited to 5000.
*   The number of vehicles is limited to 10000.
*   The simulation time unit is one second.

**Judging Criteria:**

The solution will be judged based on:

1.  **Correctness:** Accurate calculation of travel times.
2.  **Efficiency:**  The ability to handle a large number of vehicles and intersections within a reasonable time limit.
3.  **Code Quality:**  Clean, well-documented, and maintainable code.
4.  **Concurrency:** Proper utilization of multi-core processors to improve performance.

This question requires a strong understanding of data structures, algorithms, concurrency, and system design. It also necessitates careful consideration of edge cases and optimization techniques. Good luck!
