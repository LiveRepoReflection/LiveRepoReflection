## Project Name:

`OptimalRoutePlanner`

## Question Description:

You are tasked with designing an optimal route planning system for a delivery company operating in a large city. The city is represented as a directed graph where nodes are locations and edges are roads. Each road has a travel time (in minutes), a toll cost (in USD), and a reliability score (a floating-point number between 0 and 1, representing the probability of successfully traversing the road without delays).

The delivery company has a fleet of trucks with varying capacities and operational costs. Each truck has a maximum weight capacity (in kg) and a cost per minute of operation (in USD/minute).

Given a set of delivery requests, each with a source location, a destination location, a weight (in kg), and a required delivery time window (start and end time in minutes from the start of the day), your system must determine the optimal route for each delivery request while minimizing the total cost.

The total cost is calculated as follows:

`Total Cost = Travel Time * Truck Cost per Minute + Toll Costs + Penalty Cost`

A penalty cost is incurred if the delivery is outside the required delivery time window. The penalty cost is calculated as:

`Penalty Cost = Late Delivery Cost per Minute * (Actual Delivery Time - Required Delivery End Time) + Early Delivery Waiting Cost per Minute * (Required Delivery Start Time - Actual Delivery Time)`

If a delivery is on time, the penalty cost is zero. Assume that `Late Delivery Cost per Minute` and `Early Delivery Waiting Cost per Minute` are provided as constant values.

**Constraints:**

1.  The number of locations (nodes) in the city graph can be up to 1000.
2.  The number of roads (edges) in the city graph can be up to 5000.
3.  The number of delivery requests can be up to 100.
4.  Truck fleet size can be up to 10.
5.  Travel time for each road can be between 1 and 60 minutes.
6.  Toll cost for each road can be between 0 and 10 USD.
7.  Weight of each delivery request can be between 1 and 500 kg.
8.  Delivery time window for each request can be any time during the day (0 to 1440 minutes).
9.  Truck capacity can be between 500 and 2000 kg.
10. Truck cost per minute can be between 0.1 and 0.5 USD/minute.
11. Reliability score for each road must be considered. If the product of reliabilities along a chosen route is below a certain threshold (provided as input), the delivery is considered unsuccessful, and a large fixed penalty is applied to the total cost.

**Optimization Requirements:**

Your solution should aim to minimize the total cost across all delivery requests. This includes optimizing route selection, truck assignment, and delivery scheduling.

**Input:**

The input will be provided in the following format:

1.  **City Graph:** A list of nodes and a list of edges. Each edge will contain source node ID, destination node ID, travel time, toll cost, and reliability score.
2.  **Truck Fleet:** A list of trucks, each with a capacity and cost per minute.
3.  **Delivery Requests:** A list of delivery requests, each with a source location ID, destination location ID, weight, required delivery start time, and required delivery end time.
4.  **Penalty Costs:** `Late Delivery Cost per Minute`, `Early Delivery Waiting Cost per Minute`, and `Unsuccessful Delivery Penalty`.
5.  **Reliability Threshold:** The minimum product of reliabilities for a successful delivery route.

**Output:**

Your program should output the total minimum cost for all delivery requests.

**Judging Criteria:**

The solutions will be judged based on the following criteria:

1.  **Correctness:** The solution must correctly compute the total cost for all delivery requests, considering all constraints and penalties.
2.  **Optimality:** The solution should aim to minimize the total cost as much as possible. The solutions will be ranked based on the total cost, with lower costs being preferred.
3.  **Efficiency:** The solution must be efficient enough to handle large input sizes within a reasonable time limit (e.g., 5 minutes).
4.  **Code Quality:** The code should be well-structured, readable, and maintainable.

This problem requires a combination of graph algorithms (shortest path with multiple constraints), dynamic programming (for optimal truck assignment and scheduling), and careful handling of edge cases and constraints. Be ready to optimize your solution to achieve the best possible score. Good luck!
