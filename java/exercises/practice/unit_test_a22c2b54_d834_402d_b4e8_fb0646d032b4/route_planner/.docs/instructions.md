## Project Name

`OptimalRoutePlanner`

## Question Description

You are tasked with designing an optimal route planning service for a delivery company operating in a large, dynamic city. The city is represented as a weighted, directed graph where nodes represent delivery locations and edges represent roads connecting them. Each road has a traversal time associated with it (the weight of the edge).

The delivery company has a central depot and a fleet of delivery vehicles. Each vehicle starts at the depot, delivers a set of packages to a predefined set of destinations, and returns to the depot.

Due to traffic fluctuations, the traversal time of each road changes throughout the day. These changes are provided as a stream of updates. Each update specifies a road (source node, destination node) and its new traversal time at a specific timestamp.

Your service must efficiently handle the following two types of requests:

1.  **`updateRoute(source, destination, timestamp, newTraversalTime)`**:  This request updates the traversal time of the road from `source` to `destination` to `newTraversalTime` at the given `timestamp`.  Multiple updates for the same road may exist at different timestamps.

2.  **`getOptimalDeliveryRoute(startLocation, endLocation, startTime)`**:  This request calculates the shortest (fastest) route from `startLocation` to `endLocation`, considering the time-dependent traversal times.  The route must be optimal at `startTime`.  You should assume that the traversal time of a road remains constant from the last update up to any future time (until a newer update changes it). If no update exists for a specific road before `startTime`, use a default traversal time of `Integer.MAX_VALUE`.

**Constraints:**

*   The city graph can contain up to 10,000 nodes and 100,000 edges.
*   Traversal times are non-negative integers.
*   The number of `updateRoute` requests can be up to 1,000,000.
*   The number of `getOptimalDeliveryRoute` requests can be up to 100,000.
*   `startLocation` and `endLocation` are always valid nodes in the graph.
*   All `timestamp` values are non-negative integers and fit within a standard integer data type.
*   The `startTime` in `getOptimalDeliveryRoute` requests is always greater than or equal to the timestamps of existing `updateRoute` requests.
*   Self-loops and parallel edges are allowed in the graph.
*   The graph is not guaranteed to be strongly connected.

**Optimization Requirements:**

*   The `getOptimalDeliveryRoute` request must be processed as quickly as possible. Consider using efficient algorithms and data structures to minimize the response time.
*   Memory usage should be optimized, especially considering the large number of updates that may be stored.

**Considerations:**

*   The time-dependent nature of the edge weights adds significant complexity.
*   The need to efficiently query for the most recent edge weight update before a given timestamp requires careful data structure selection.
*   The scale of the graph and the number of requests necessitates highly optimized algorithms and data structures.

This problem requires a combination of graph algorithms, data structure expertise, and optimization techniques to achieve an efficient and scalable solution. You need to select a suitable shortest path algorithm that can handle time-dependent edge weights and design efficient data structures for storing and querying the route updates.
