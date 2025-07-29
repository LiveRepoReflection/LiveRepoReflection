## Project Name

`OptimalRoutePlanner`

## Question Description

You are tasked with designing an efficient route planning system for a delivery company operating in a large city. The city is represented as a directed graph where nodes represent intersections and edges represent roads. Each road has a travel time (in minutes), a traffic density factor (a floating-point number between 0.1 and 1.0, where 0.1 indicates very light traffic and 1.0 indicates heavy traffic), and a toll cost (in USD).

Your system needs to handle a large number of delivery requests concurrently. Each request specifies a start intersection, a destination intersection, a departure time (in minutes from the start of the day), and a maximum budget (in USD) for tolls.

Your goal is to find the fastest route for each delivery request, considering both travel time and traffic density, while staying within the specified toll budget.

**Specific Requirements:**

1.  **Graph Representation:** Implement a suitable data structure to represent the city's road network. The graph should be efficiently searchable and allow for dynamic updates (e.g., road closures, changes in traffic density - these updates do NOT need to be implemented, but the design should be flexible enough to accomodate it).

2.  **Route Finding Algorithm:** Implement an algorithm to find the fastest route between two intersections, considering travel time and traffic density.  The total travel time for a road is calculated as: `road_travel_time * traffic_density_factor`. The algorithm must also respect the maximum toll budget.

3.  **Real-Time Traffic:** The traffic density on each road can change over time. Your route-finding algorithm should consider the traffic density at the *estimated* time of arrival at each intersection. You can assume that you have a function `get_traffic_density(road_id, time)` that returns the traffic density factor for a given road at a given time (in minutes).  This function is external and you do not need to implement it.

4.  **Optimization:** The system must be able to handle a large number of concurrent requests efficiently.  Consider using appropriate data structures and algorithmic optimizations to minimize the response time for each request.

5.  **Scalability:**  The system should be designed in a way that it can be scaled to handle a larger city with more intersections and roads.

6.  **Edge Cases:** Handle the following edge cases:

    *   No route exists between the start and destination intersections within the budget.
    *   The start and destination intersections are the same.
    *   The budget is insufficient to cover even the cheapest route.
    *   Invalid input data (e.g., negative travel time, invalid intersection IDs).

7.  **Time Complexity:** Your solution's route-finding algorithm should aim for a time complexity that is as efficient as possible, considering the trade-offs between speed and memory usage.  Solutions that are demonstrably inefficient (e.g., repeatedly recalculating the same shortest paths) may not pass all test cases.

**Input:**

*   The city's road network (a directed graph represented as a list of edges, where each edge contains: `start_intersection_id`, `destination_intersection_id`, `travel_time`, `traffic_density_factor`, `toll_cost`).  This will be provided in a format suitable for your chosen graph representation (e.g., adjacency list).  The initial traffic density factor can be used as a default if the `get_traffic_density` function is not used initially.
*   A list of delivery requests, where each request contains: `start_intersection_id`, `destination_intersection_id`, `departure_time`, `maximum_toll_budget`.

**Output:**

For each delivery request, return a list of intersection IDs representing the fastest route, or an empty list if no route is found within the budget. Also return the total travel time (in minutes) and the total toll cost (in USD) for the found route.

**Grading Criteria:**

*   **Correctness:** The solution must find the correct fastest route within the budget for all test cases.
*   **Efficiency:** The solution must be efficient enough to handle a large number of requests and a large road network within a reasonable time limit.
*   **Scalability:** The solution should be designed in a way that it can be scaled to handle larger cities.
*   **Code Quality:** The code should be well-structured, readable, and well-documented.
*   **Handling of Edge Cases:** The solution must correctly handle all specified edge cases.
