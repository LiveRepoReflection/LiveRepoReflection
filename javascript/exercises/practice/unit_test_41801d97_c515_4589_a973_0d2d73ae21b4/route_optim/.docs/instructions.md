## Project Name

```
efficient-route-planning
```

## Question Description

You are tasked with designing an efficient route planning system for a delivery service operating in a large city. The city is represented as a directed graph where nodes are delivery locations and edges represent streets connecting these locations. Each street has a traffic congestion score associated with it, representing the delay a delivery vehicle would experience when traversing that street.

Given a set of delivery orders, your system must determine the optimal route for each delivery vehicle, considering both the delivery location and the time window within which the delivery must be completed.  The goal is to minimize the total traffic congestion score for all routes, while ensuring all deliveries are completed within their respective time windows.

**Specifics:**

*   **City Representation:** The city is represented as a directed graph.  Each node in the graph has a unique ID (integer). Each edge has:
    *   `from`: The starting node ID (integer).
    *   `to`: The ending node ID (integer).
    *   `congestion`: An integer representing the traffic congestion score for that street.
*   **Delivery Orders:** Each delivery order has:
    *   `orderId`: A unique identifier for the order (string).
    *   `locationId`: The ID (integer) of the delivery location.
    *   `startTime`: The earliest time (integer, representing seconds since the start of the day) the delivery can be made.
    *   `endTime`: The latest time (integer, representing seconds since the start of the day) the delivery can be made.
*   **Delivery Vehicles:** You have a fleet of delivery vehicles, each starting from a central depot (node ID is `0`).  Each vehicle can handle one delivery order at a time. After delivering an order, the vehicle must return to the depot before starting the next delivery.
*   **Travel Time:** Assume travel time between locations is directly proportional to the traffic congestion score of the connecting street.  For simplicity, let 1 unit of congestion equal 1 second of travel time.
*   **Service Time:** Assume negligible service time at each delivery location.
*   **Objective:** Minimize the *total* traffic congestion score for all delivery routes while satisfying all time window constraints.
*   **Constraints:**
    *   All delivery orders must be fulfilled.
    *   Each delivery vehicle can only handle one delivery at a time.
    *   Deliveries must be made within the specified `startTime` and `endTime`.
    *   Vehicles must return to the depot after each delivery.
    *   Your solution should be efficient for a large number of locations, streets, and delivery orders.
*   **Input:**
    *   A list of nodes (represented by their IDs).
    *   A list of edges (represented as objects with `from`, `to`, and `congestion` properties).
    *   A list of delivery orders (represented as objects with `orderId`, `locationId`, `startTime`, and `endTime` properties).
*   **Output:**
    *   A list of routes. Each route should specify:
        *   `orderId`: The ID of the delivery order.
        *   `route`: An array of node IDs representing the path from the depot to the delivery location and back to the depot.
        *   `totalCongestion`: The sum of congestion scores for the entire route.
*   **Optimization:** The primary goal is to minimize the `totalCongestion` across all routes. Solutions will be evaluated based on their ability to find routes with lower total congestion scores while meeting all constraints.  Consider algorithmic efficiency and data structure choices to handle large datasets.

**Bonus Challenges:**

*   Handle a limited number of delivery vehicles.
*   Consider vehicle capacity (e.g., weight or volume limits) and the size of each delivery order.
*   Incorporate real-time traffic updates (dynamic congestion scores).
*   Implement a user interface to visualize the routes on a map.

Good luck!
