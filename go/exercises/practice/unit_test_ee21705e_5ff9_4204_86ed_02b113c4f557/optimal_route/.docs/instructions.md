## Project Name

`OptimalRoutePlanner`

## Question Description

You are tasked with designing an optimal route planning service for a delivery company operating in a large, densely populated city. The city's road network can be represented as a directed graph, where intersections are nodes and roads connecting them are directed edges. Each road has a travel time (in minutes) and a toll cost (in USD).

The delivery company has `N` delivery trucks stationed at different depots within the city. Each truck has a list of delivery locations it needs to visit, in a specific order. The goal is to minimize the total cost for each truck, considering both travel time and toll costs.

**Input:**

*   A directed graph representing the city's road network. The graph is provided as a list of edges, where each edge is a tuple `(source_node, destination_node, travel_time, toll_cost)`. Nodes are represented by unique integer IDs.
*   A list of truck routes. Each truck route is a tuple `(truck_id, start_depot, [delivery_location_1, delivery_location_2, ..., delivery_location_k])`, where `truck_id` is a unique integer ID, `start_depot` is the integer ID of the truck's starting depot, and the list of delivery locations represents the order in which the truck must visit the locations.
*   A maximum acceptable travel time `max_travel_time` (in minutes) for each truck.
*   A weight factor `time_toll_weight` to indicate the trade-off between travel time and toll cost. The higher the weight, the more important travel time is compared to the toll cost.

**Output:**

For each truck, output the optimal route and its associated total cost. The optimal route is the sequence of nodes (intersections) the truck should visit, including the start depot and all delivery locations, in the specified order, such that the total cost is minimized. The total cost is calculated as:

`Total Cost = Total Travel Time + (time_toll_weight * Total Toll Cost)`

If a truck cannot complete its route within the `max_travel_time`, output "INCOMPLETE" for that truck.

**Constraints:**

*   The number of nodes (intersections) in the city graph can be up to 10,000.
*   The number of edges (roads) in the city graph can be up to 50,000.
*   The travel time for each road is a positive integer between 1 and 60 minutes.
*   The toll cost for each road is a non-negative integer between 0 and 10 USD.
*   The number of trucks can be up to 100.
*   The number of delivery locations for each truck can be up to 10.
*   The `max_travel_time` is a positive integer between 60 and 1440 minutes (24 hours).
*   The `time_toll_weight` is a floating-point number between 0.0 and 1.0.
*   Trucks must visit delivery locations in the exact order specified.
*   A truck can travel between two delivery locations through the same intermediate node multiple times.
*   There exists at least one path between any two nodes in the graph.

**Example:**

```
Graph Edges:
[(1, 2, 10, 2), (1, 3, 15, 1), (2, 4, 20, 3), (3, 4, 5, 1)]

Truck Routes:
[(101, 1, [4])]

max_travel_time = 40
time_toll_weight = 0.5

Output:
Truck 101: Route [1, 3, 4], Total Cost 21.0
```

**Explanation:**

For truck 101, there are two possible routes: 1 -> 2 -> 4 and 1 -> 3 -> 4.

*   Route 1 -> 2 -> 4: Travel Time = 10 + 20 = 30, Toll Cost = 2 + 3 = 5, Total Cost = 30 + (0.5 \* 5) = 32.5
*   Route 1 -> 3 -> 4: Travel Time = 15 + 5 = 20, Toll Cost = 1 + 1 = 2, Total Cost = 20 + (0.5 \* 2) = 21.0

The optimal route is 1 -> 3 -> 4, with a total cost of 21.0. The travel time of 20 is also less than the `max_travel_time` of 40.

**Challenge:**

Design an efficient algorithm to find the optimal route for each truck, considering the trade-off between travel time and toll costs and the `max_travel_time` constraint. Optimize your code for performance, as the input graph and truck routes can be large. Consider using appropriate data structures and algorithms to achieve the best possible time complexity. Pay close attention to edge cases and ensure your solution handles them correctly.
