## Project Name

`TrafficOptimization`

## Question Description

You are tasked with designing an intelligent traffic management system for a city. The city's road network can be represented as a directed graph, where nodes represent intersections and edges represent road segments connecting them. Each road segment has a *capacity*, representing the maximum number of vehicles that can traverse it per unit of time, and a *base travel time*, representing the time it takes to traverse the segment under ideal (low traffic) conditions.

The system receives real-time traffic updates. These updates provide the *current traffic flow* on each road segment (number of vehicles traversing it per unit of time). Based on the current traffic flow, the actual travel time on each road segment increases according to a given formula:

`actual_travel_time = base_travel_time * (1 + (current_traffic_flow / capacity)^2)`

The system needs to answer two types of queries efficiently:

1.  **Shortest Path Query:** Given a source intersection and a destination intersection, find the shortest path between them based on the *current* travel times. You need to minimize the total travel time along the path.

2.  **Traffic Rerouting Recommendation:** Given a specific origin-destination pair and a percentage threshold `p`, suggest a set of rerouting recommendations to minimize the overall travel time in the network. You should identify a subset of vehicles currently traveling from the origin to the destination, and suggest alternative paths for them. The total flow rerouted should be at least `p` percent of the original flow from the origin to the destination. The metric to minimize is the sum of `actual_travel_time * current_traffic_flow` across all edges in the network. This represents the total time spent by all vehicles on the roads. This needs to be calculated both before and after rerouting.

**Constraints:**

*   The city's road network can be large, with up to 10,000 intersections and 50,000 road segments.
*   The number of shortest path queries can be very high. These queries need to be answered as quickly as possible.
*   The traffic rerouting recommendation algorithm must be efficient. An optimal solution is not required, but the algorithm must provide a reasonable improvement in overall network travel time within a limited time budget (e.g., 5 seconds).
*   The `current_traffic_flow` on each road segment is always less than or equal to its `capacity`.
*   Consider the fact that rerouting vehicles on one route might adversely affect other routes, so you need to reroute in a way that minimizes overall network travel time.
*   Assume that vehicles will follow the suggested rerouting recommendations.
*   You can assume that the percentage threshold `p` is always a reasonable value, and there is always a way to reroute at least `p` percent of the original traffic between the origin and destination.

**Implementation Details:**

*   You need to implement the core algorithms and data structures to represent the road network, calculate travel times, find shortest paths, and generate traffic rerouting recommendations.
*   Pay close attention to algorithmic efficiency and data structure choices to meet the performance requirements.
*   Consider using appropriate optimization techniques to improve the performance of your traffic rerouting recommendation algorithm.
*   Your solution should be able to handle both shortest path queries and traffic rerouting recommendations efficiently, even under heavy traffic conditions.

**Bonus:**

*   Implement a mechanism to handle dynamic updates to the road network (e.g., road closures, capacity changes).
*   Consider different traffic rerouting strategies and compare their performance.
*   Implement a visualization of the city's road network and the traffic flow.
