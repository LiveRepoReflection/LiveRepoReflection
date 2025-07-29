## Project Name

`OptimalAirTraffic`

## Question Description

You are tasked with designing an air traffic control system for a busy airspace. The airspace can be modeled as a directed graph where each node represents an airport and each directed edge represents a possible flight route between two airports. Each flight route has a specific cost associated with it, representing factors like fuel consumption, time, and air traffic congestion.

Given a set of `N` airports and `M` possible flight routes, along with real-time weather updates and dynamic airspace restrictions, your system needs to efficiently determine the optimal flight plan for `K` planes. Optimal means minimizing the total cost for each plane to reach its destination.

Here's a breakdown of the challenges and requirements:

1.  **Graph Representation:** Implement a suitable data structure to represent the airspace graph. Consider the trade-offs between memory usage and performance for graph operations.

2.  **Real-time Weather Updates:** The weather conditions along each flight route can change dynamically. You will receive a stream of weather update events, each specifying a flight route (source airport, destination airport) and a new cost value for that route. Your system must efficiently update the graph to reflect these changes.

3.  **Airspace Restrictions:** Certain flight routes might be temporarily restricted due to maintenance, emergencies, or other unforeseen circumstances. You will receive a stream of restriction events, each specifying a flight route (source airport, destination airport) that is temporarily unavailable. Your system must efficiently remove these edges from the graph and reinstate them when the restriction is lifted.

4.  **Optimal Path Finding:** For each plane, given its origin airport and destination airport, you need to find the lowest-cost path through the airspace graph, considering the current weather conditions and airspace restrictions. Efficiency is critical, as you need to determine routes for multiple planes concurrently.

5.  **Scalability and Concurrency:** The system should be able to handle a large number of airports, flight routes, planes, and real-time events. Design your solution with concurrency in mind, allowing multiple planes to be routed simultaneously and weather/restriction updates to be processed concurrently without causing race conditions or data corruption.

6.  **Fault Tolerance:** Implement mechanisms to ensure that the system remains functional even in the event of failures or unexpected errors. Consider strategies for error handling, logging, and recovery.

7.  **Optimization Requirements:** Standard shortest path algorithms (e.g., Dijkstra, Bellman-Ford) might not be efficient enough for the scale of the problem. Explore more advanced algorithms and data structures for path finding, such as A\* search with heuristics or pre-computation techniques. You need to optimize your solution to minimize the path-finding latency for each plane.

**Input:**

*   A list of airports (nodes) represented by unique integer IDs.
*   A list of initial flight routes (edges) represented by tuples of (source airport ID, destination airport ID, initial cost).
*   A stream of weather update events, each represented by a tuple of (source airport ID, destination airport ID, new cost).
*   A stream of restriction events, each represented by a tuple of (source airport ID, destination airport ID, restriction start time, restriction end time).
*   A list of plane requests, each represented by a tuple of (plane ID, origin airport ID, destination airport ID).

**Output:**

For each plane request, output the lowest-cost path from the origin airport to the destination airport, considering the current weather conditions and airspace restrictions. If no path exists, output "No path found". The path should be represented as a list of airport IDs in the order they are visited.

**Constraints:**

*   Number of airports (N): Up to 10,000
*   Number of flight routes (M): Up to 100,000
*   Number of planes (K): Up to 1,000
*   Number of weather update events: Up to 100,000
*   Number of restriction events: Up to 10,000
*   Cost of each flight route: Positive integer between 1 and 1,000
*   Time limit: 5 seconds
*   Memory limit: 2 GB

**Evaluation:**

Your solution will be evaluated based on its correctness, efficiency, scalability, and fault tolerance. The test cases will include various scenarios with different graph structures, weather patterns, airspace restrictions, and plane requests. The scoring will be based on the number of test cases passed and the average latency of path finding for each plane.
