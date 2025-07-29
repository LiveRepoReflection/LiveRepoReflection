## Question: Optimal Network Design for Content Delivery

### Question Description

A global content delivery network (CDN) provider, "FastLane," is facing increasing demand and needs to optimize its network infrastructure. FastLane has a set of data centers distributed across the globe. Each data center has a certain capacity (measured in Gbps) and incurs a specific operational cost per Gbps of traffic served.

FastLane serves content requests from a large number of geographically dispersed users. Each user request has a specific bandwidth demand (in Mbps) and a latency requirement (in milliseconds).  A request can be served by any of the data centers, but the latency between a user and a data center depends on their geographic locations.

Your task is to design an algorithm that optimally assigns user requests to data centers, considering data center capacity, operational costs, and latency constraints, while minimizing the total operational cost for FastLane.

**Input:**

*   `data_centers`: A list of tuples, where each tuple represents a data center and contains the following information: `(data_center_id, capacity_gbps, operational_cost_per_gbps)`. `data_center_id` is a unique integer identifier.
*   `user_requests`: A list of tuples, where each tuple represents a user request and contains the following information: `(request_id, user_location, bandwidth_demand_mbps, latency_requirement_ms)`. `request_id` is a unique integer identifier, and `user_location` is a tuple `(latitude, longitude)`.
*   `latency_matrix`: A dictionary where keys are tuples of `(user_location, data_center_id)` and values are the latency in milliseconds between that user location and data center.

**Output:**

A dictionary where keys are `data_center_id` and values are lists of `request_id` assigned to that data center. If a request cannot be served due to capacity or latency constraints, it should **not** be included in the output.

**Constraints:**

*   Data center capacity is a hard constraint: the total bandwidth demand assigned to a data center cannot exceed its capacity. Convert Mbps to Gbps as needed (1000 Mbps = 1 Gbps).
*   Latency requirement is a hard constraint: a request can only be assigned to a data center if the latency between the user and the data center is less than or equal to the user's latency requirement.
*   Minimize the total operational cost: The algorithm should strive to assign requests in a way that minimizes the overall cost for FastLane. This is calculated as the sum of (operational cost per Gbps * bandwidth served in Gbps) across all data centers.
*   You must serve as many requests as possible, given the constraints and cost minimization goal.
*   The number of data centers and user requests can be large (up to 10,000 each).
*   Assume all numerical inputs (capacity, bandwidth, latency, cost) are positive.
*   If multiple solutions with the same minimal total cost exist, any of those solutions is acceptable.
*   Your solution should be efficient and have a reasonable runtime for large input sizes. Naive brute-force approaches will likely time out.
*   You should handle edge cases gracefully, such as empty input lists.

**Example:**

Let's say you have one data center, two user requests, and a latency matrix:

```python
data_centers = [(1, 1.0, 10.0)]  # (data_center_id, capacity_gbps, operational_cost_per_gbps)
user_requests = [(101, (37.7749, -122.4194), 200, 50),  # (request_id, user_location, bandwidth_demand_mbps, latency_requirement_ms)
                 (102, (34.0522, -118.2437), 300, 100)]
latency_matrix = {((37.7749, -122.4194), 1): 30,  # (user_location, data_center_id): latency_ms
                  ((34.0522, -118.2437), 1): 60}
```

A possible optimal output could be:

```python
{1: [101, 102]}  # Data center 1 serves requests 101 and 102
```

Because both requests can be served within the data center capacity and latency requirements, and this assignment maximizes the number of served requests (which is implicitly desired). The total bandwidth used is 0.5 Gbps, well within the 1.0 Gbps capacity.

**Scoring:**

Solutions will be evaluated based on their correctness (satisfying all constraints) and optimality (minimizing the total operational cost). Solutions that are more efficient and scale better to large input sizes will be favored. Solutions not returning the minimal operational cost might receive partial points.
