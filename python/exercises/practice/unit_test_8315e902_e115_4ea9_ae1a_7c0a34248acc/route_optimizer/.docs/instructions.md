## Project Name

`OptimalRoutePlanner`

## Question Description

You are tasked with designing an optimal route planning system for a delivery service operating in a large city. The city is represented as a graph where:

*   Nodes represent intersections or delivery locations. Each node has a unique ID (an integer) and geographical coordinates (latitude and longitude).
*   Edges represent roads connecting the nodes. Each edge has a weight representing the travel time (in minutes) between the connected nodes. Note roads are bidirectional, meaning edge(A,B) = edge(B,A).

You are given a set of delivery orders. Each delivery order specifies:

*   A source node (the depot where the delivery starts).
*   A destination node (the customer's location).
*   A delivery time window (a start time and an end time, in minutes from the start of the day). The delivery must be completed within this window.
*   A priority level (an integer, higher value means higher priority).

Your system must determine an optimal delivery route that minimizes the total lateness across all delivery orders. Lateness for a delivery is defined as the amount of time by which the delivery exceeds its delivery time window's end time. If a delivery is completed within its time window, its lateness is 0.

**Constraints and Requirements:**

*   **Large-Scale Graph:** The city graph can be very large (up to 10,000 nodes and 50,000 edges).
*   **Many Orders:** You may need to handle a large number of delivery orders (up to 1,000).
*   **Time Windows:** The delivery time windows are non-overlapping and can vary in size.
*   **Priority:** Higher-priority orders should be given preference in minimizing lateness. You should aim to minimize the lateness of high priority orders first.
*   **Optimization:** The solution must be efficient and scalable. Brute-force approaches will not be feasible. You should explore using heuristics or approximation algorithms.
*   **Realistic Travel Times:** Assume travel times between nodes can vary significantly, and some routes might be much faster than others.
*   **Output:** Your function should return an ordered list of delivery order IDs representing the sequence in which the deliveries should be performed. The order of the delivery order IDs must ensure the lowest total lateness across all delivery orders.
*   **Time Complexity:** Solutions must provide a relatively efficient time complexity to pass.

**Input Format:**

Your function will receive the following inputs:

*   `nodes`: A list of tuples, where each tuple represents a node in the form `(node_id, latitude, longitude)`.
*   `edges`: A list of tuples, where each tuple represents an edge in the form `(node_id_1, node_id_2, travel_time)`.
*   `orders`: A list of tuples, where each tuple represents a delivery order in the form `(order_id, source_node, destination_node, start_time, end_time, priority)`.

**Example:**

```python
nodes = [(1, 37.7749, -122.4194), (2, 37.7833, -122.4167), (3, 37.7900, -122.4000)]
edges = [(1, 2, 5), (2, 3, 10), (1, 3, 15)]
orders = [(101, 1, 3, 60, 75, 5), (102, 2, 1, 30, 40, 10)]
```

**Goal:**

Implement a function `optimal_route_plan(nodes, edges, orders)` that returns a list of delivery order IDs representing the optimized delivery route.
