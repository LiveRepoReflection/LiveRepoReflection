Okay, here's a challenging problem description for a programming competition, focusing on graph algorithms and optimization.

### Project Name

`OptimalAirNetwork`

### Question Description

The "Global Connectivity Initiative" aims to establish a resilient and efficient air transportation network connecting major cities worldwide.  You are tasked with designing the optimal air network, minimizing both infrastructure costs and travel times, while adhering to strict safety and operational constraints.

You are given a set of `N` cities, each represented by its geographical coordinates (latitude, longitude). You are also given a list of `M` potential airport locations, each with an associated construction cost. Each airport can support a maximum number of flights per day (`capacity`).  Building an airport at a city is not mandatory.

A direct flight route can exist between any two airports. The cost of establishing a direct flight route between two airports is proportional to the distance between them (calculated using the Haversine formula) and a route difficulty factor.

**Objective:**

Your task is to design an air network that satisfies the following requirements:

1.  **Connectivity:** Any traveler should be able to travel between any two cities in the network, potentially requiring multiple flights.
2.  **Airport Capacity:** The total number of flights originating from any airport should not exceed its capacity.
3.  **Minimize Total Cost:** Minimize the sum of airport construction costs and flight route establishment costs.
4.  **Minimize Maximum Travel Time:** Minimize the longest travel time between any two cities in the network using the designed air routes. Travel time between two directly connected airports can be calculated using `distance / average_speed`, where average_speed is a constant 800 km/h.

**Input:**

*   `N`: The number of cities.
*   `cities`: A list of `N` tuples, where each tuple `(latitude, longitude)` represents a city's coordinates.
*   `M`: The number of potential airport locations.
*   `airports`: A list of `M` tuples, where each tuple `(latitude, longitude, construction_cost, capacity)` represents a potential airport location. These locations are a subset of the cities.
*   `route_difficulty_factor`: A constant representing the difficulty of establishing a route. This should be multiplied by the distance to determine the cost of a route.

**Output:**

Return a tuple: `(total_cost, max_travel_time, airport_locations, flight_routes)`.

*   `total_cost`: The total cost of the network (airport construction + flight route establishment).
*   `max_travel_time`: The maximum travel time between any two cities in the network, in hours.  If the network is disconnected, return `float('inf')`.
*   `airport_locations`: A list of indices (0-indexed) corresponding to the selected airport locations from the `airports` list.
*   `flight_routes`: A list of tuples, where each tuple `(airport_index_1, airport_index_2)` represents a direct flight route between two selected airports (airport indices also 0-indexed, referring to the `airport_locations` list).

**Constraints:**

*   `1 <= N <= 100`
*   `1 <= M <= N`
*   Coordinates are valid latitude/longitude values.
*   Construction costs and capacities are positive integers.
*   Optimization is critical. Solutions exceeding a reasonable time limit will be rejected.
*   Assume the earth is a perfect sphere with a radius of 6371 km for Haversine distance calculations.
*   The algorithm should aim for the absolute optimal. If the total cost are equal, the lower the max_travel_time the better.

**Edge Cases:**

*   A single city with no airport.
*   Cities that cannot be connected given the airport locations.
*   Airport capacities are insufficient to support all possible flight routes.
*   Empty `airports` list.

**Judging Criteria:**

The solution will be judged based on the following:

*   **Correctness:** The solution must produce a valid air network that satisfies all constraints.
*   **Cost Minimization:** The solution should minimize the total cost of the network.
*   **Travel Time Minimization:** Subject to cost minimization, the solution should minimize the maximum travel time between any two cities.
*   **Efficiency:** The solution should execute within a reasonable time limit.
*   **Code Quality:** The code should be well-structured, readable, and maintainable.

This problem combines graph traversal (for connectivity and travel time), optimization (minimizing cost and travel time), and practical considerations (airport capacity). It requires a sophisticated approach to achieve an optimal solution, making it a challenging and rewarding problem for skilled programmers.
