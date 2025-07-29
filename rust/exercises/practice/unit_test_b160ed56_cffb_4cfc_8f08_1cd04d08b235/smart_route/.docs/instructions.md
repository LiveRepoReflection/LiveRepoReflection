## Question: Optimized Network Routing with Congestion Awareness

### Project Name

`smart-router`

### Question Description

You are tasked with designing an intelligent routing algorithm for a network of interconnected routers. The network is represented as a weighted, undirected graph where nodes represent routers and edges represent the communication links between them. Each link has a *capacity* (maximum bandwidth) and a *current utilization* (amount of bandwidth currently in use).

Given a network graph, a source router, a destination router, and a data size to be transmitted, your goal is to find the optimal route that minimizes the *transmission time* while respecting the capacity constraints of each link.

**Transmission Time Calculation:**

The transmission time for a given route is calculated as the sum of the transmission times on each link in the route. The transmission time on a single link is calculated as `data_size / (available_bandwidth)`, where `available_bandwidth = capacity - utilization`.

**Network Dynamics:**

The network is dynamic. Before your routing decision is implemented, the `utilization` of each link may change due to other network traffic. You will be provided with an initial network state, and a function to simulate network updates.  You need to consider these potential changes when choosing your route.

**Constraints and Requirements:**

1.  **Correctness:** The calculated route must connect the source and destination routers. The route must respect link capacities at all times. Sending data through a link exceeding its capacity is invalid.
2.  **Optimization:** Minimize the total transmission time for the given data size.  Consider multiple routes and select the best one.
3.  **Dynamic Network:** Before your algorithm chooses a route, call the provided function `simulate_network_updates(network)` to simulate a single time step of network traffic changes. The returned network represents the updated utilizations on each link. Your routing decision must be based on this *updated* network state.
4.  **Scalability:** The network can be large (up to 1000 routers and 10,000 links).  Your solution must be efficient in terms of both time and memory.  Naive algorithms like brute-force search will likely timeout.
5.  **Edge Cases:** Handle cases where no route exists between the source and destination, or where all possible routes violate capacity constraints.
6.  **Real-world Considerations:**  The network is not perfectly reliable. Implement a mechanism to avoid links with extremely high utilization (approaching capacity). This can be achieved by adding a penalty to the link's transmission time based on its utilization relative to its capacity. The higher the utilization, the higher the penalty.

**Input:**

*   `network`: A graph represented as an adjacency list (e.g., a `HashMap<RouterID, Vec<(RouterID, Capacity, Utilization)>>`). `RouterID` is an integer representing the unique identifier for each router. `Capacity` and `Utilization` are floating-point numbers representing the link capacity and current utilization, respectively.
*   `source`: The `RouterID` of the source router.
*   `destination`: The `RouterID` of the destination router.
*   `data_size`: The size of the data to be transmitted (floating-point number).
*   `simulate_network_updates`: A function that takes the current `network` as input, simulates a single time step of network traffic changes, and returns the updated `network`.

**Output:**

A `Vec<RouterID>` representing the optimal route (an ordered list of router IDs) from the source to the destination.  Return an empty `Vec` if no valid route is found.

**Judging Criteria:**

Your solution will be judged based on the following criteria:

*   **Correctness:** Does the solution find a valid route (if one exists) that connects the source and destination without exceeding link capacities?
*   **Efficiency:** Is the solution efficient enough to handle large networks within the time limit?
*   **Optimality:** Does the solution find a route with a near-optimal transmission time?  Solutions that consistently find significantly sub-optimal routes will be penalized.
*   **Robustness:** Does the solution handle edge cases and dynamic network changes gracefully?

This problem requires a combination of graph algorithms, optimization techniques, and careful handling of constraints to arrive at a robust and efficient solution. Good luck!
