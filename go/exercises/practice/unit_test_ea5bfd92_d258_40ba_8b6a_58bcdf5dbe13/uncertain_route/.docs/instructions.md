## Question: Optimal Multi-Hop Route Planning with Uncertainties

### Description

You are tasked with designing an efficient route planning system for a delivery company operating in a large, dynamically changing urban environment. The city can be represented as a directed graph where nodes are delivery locations (warehouses, customer addresses, etc.) and edges represent potential delivery routes between locations. Each edge has associated with it:

*   **Distance:** The physical distance of the route (in kilometers).
*   **Estimated Travel Time:** The estimated travel time (in minutes) based on historical traffic data.
*   **Uncertainty Factor:** A value between 0.0 and 1.0 representing the *uncertainty* in the estimated travel time. This factor accounts for unpredictable events like accidents, road closures, or unexpected traffic surges. A higher uncertainty factor implies a greater potential deviation from the estimated travel time.

The delivery company needs to transport a package from a source location to a destination location. However, direct routes are not always the fastest or most reliable. Your system must find the *optimal* multi-hop route, considering both the estimated travel time and the uncertainty associated with each route segment.

**Optimization Goal:**

Minimize the **Risk-Adjusted Travel Time**. The Risk-Adjusted Travel Time for a route is calculated as follows:

1.  For each edge (route segment) in the path, calculate the *Risk*. The risk is defined as: `Risk = Estimated Travel Time * Uncertainty Factor`.
2.  Calculate the *Total Travel Time* for the route by summing the Estimated Travel Times of all edges in the path.
3.  Calculate the *Total Risk* for the route by summing the Risks of all edges in the path.
4.  The Risk-Adjusted Travel Time is then: `Risk-Adjusted Travel Time = Total Travel Time + Total Risk`.

**Constraints and Requirements:**

*   **Large Graph:** The city graph can contain up to 10,000 nodes and 50,000 edges.
*   **Dynamic Updates:** The edge properties (distance, estimated travel time, and uncertainty factor) can change frequently (simulating real-time traffic updates). Your solution should be able to adapt to these changes efficiently. Updates will be provided as a stream of edge modifications.
*   **Time Limit:** Given the real-time nature of the application, the route planning algorithm must find a near-optimal solution within a strict time limit (e.g., 500 milliseconds).
*   **Memory Limit:** The system has limited memory resources. Avoid excessive memory consumption, especially when handling large graphs.
*   **No Negative Cycles:** You can assume that the graph does not contain any negative cycles (cycles with a negative total travel time).

**Input:**

1.  A description of the city graph, including nodes and edges with their initial distance, estimated travel time, and uncertainty factor.
2.  A stream of updates to the edge properties (distance, estimated travel time, uncertainty factor).
3.  A series of route planning requests, each specifying a source location and a destination location.

**Output:**

For each route planning request, output the sequence of nodes representing the *optimal* route (i.e., the route with the minimum Risk-Adjusted Travel Time) from the source to the destination. If no route exists, output "No Route Found".

**Judging Criteria:**

The solution will be judged based on the following criteria:

*   **Correctness:** The route returned must be a valid path from the source to the destination.
*   **Optimality:** The Risk-Adjusted Travel Time of the route must be as close as possible to the true optimum. Solutions that consistently find near-optimal routes will be ranked higher.
*   **Performance:** The route planning algorithm must meet the specified time limit, even under heavy load (frequent updates and route planning requests).
*   **Memory Usage:** The solution must not exceed the allowed memory limit.
*   **Scalability:** The solution should gracefully handle large graphs and a high volume of updates and route planning requests.

This problem challenges you to combine graph algorithms, data structure design, and optimization techniques to build a practical and efficient route planning system in a dynamic environment. Good luck!
