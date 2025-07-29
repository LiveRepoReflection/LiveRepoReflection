## Question: Scalable Route Optimization for a Delivery Network

**Question Description:**

You are tasked with optimizing the delivery routes for a large-scale delivery network. The network consists of `N` delivery hubs and `M` delivery points (customers). Each delivery hub has a fleet of delivery vehicles with limited capacity. Each delivery point has a specific demand for goods.

**Input:**

1.  `hubs`: A list of tuples representing the delivery hubs. Each tuple contains:
    *   `hub_id` (int): A unique identifier for the hub (0-indexed).
    *   `location` (tuple of floats): (latitude, longitude) coordinates of the hub.
    *   `capacity` (int): The total carrying capacity of all vehicles at this hub.
    *   `vehicles` (int): The number of vehicles available at the hub.

2.  `delivery_points`: A list of tuples representing the delivery points. Each tuple contains:
    *   `point_id` (int): A unique identifier for the delivery point (0-indexed).
    *   `location` (tuple of floats): (latitude, longitude) coordinates of the delivery point.
    *   `demand` (int): The quantity of goods required at this point.

3.  `max_vehicle_capacity`: an integer representing the maximum capacity of a single vehicle.

**Constraints:**

*   `1 <= N <= 100` (Number of hubs)
*   `1 <= M <= 10,000` (Number of delivery points)
*   `1 <= capacity <= 1,000,000` (Hub capacity)
*   `1 <= vehicles <= 100` (Number of vehicles per hub)
*   `1 <= demand <= 1,000` (Demand at each delivery point)
*   `1 <= max_vehicle_capacity <= 5000` (Maximum capacity of a single vehicle)
*   The total demand of all delivery points might exceed the total capacity of all hubs. In such cases, not all delivery points can be served.
*   The distance between any two locations (hub or delivery point) can be calculated using the Haversine formula (provided below).
*   Each vehicle must start and end its route at the same hub.
*   A delivery point can only be served by a single vehicle.  Splitting demand across multiple vehicles is not allowed.
*   A vehicle's total load for a single route must not exceed `max_vehicle_capacity`.
*   All hubs have the same type of vehicles, hence the same `max_vehicle_capacity`.

**Output:**

A dictionary representing the optimized delivery routes. The keys are the `hub_id`'s, and the values are lists of routes for each hub. Each route is a list of `point_id`'s representing the delivery points served by that route, in the order they should be visited.

```python
{
  0: [[1, 2, 3], [4, 5]],  # Hub 0: Route 1 serves points 1, 2, 3; Route 2 serves points 4, 5
  1: [[6, 7, 8, 9]]      # Hub 1: Route 1 serves points 6, 7, 8, 9
}
```

**Objective:**

Minimize the total travel distance across all routes and all hubs while satisfying all constraints.  If not all delivery points can be served due to capacity constraints, prioritize serving as many delivery points as possible while minimizing the total distance for those served.

**Haversine Formula (Distance Calculation):**

```python
import math

def haversine(coord1, coord2):
  """
  Calculate the distance between two points on Earth using the Haversine formula.
  """
  lat1, lon1 = coord1
  lat2, lon2 = coord2
  R = 6371  # Radius of Earth in kilometers

  lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

  dlat = lat2 - lat1
  dlon = lon2 - lon1
  a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
  c = 2 * math.asin(math.sqrt(a))

  return R * c
```

**Example:**

```python
hubs = [
    (0, (37.7749, -122.4194), 1000, 2),  # Hub 0: San Francisco, capacity 1000, 2 vehicles
    (1, (34.0522, -118.2437), 500, 1)   # Hub 1: Los Angeles, capacity 500, 1 vehicle
]

delivery_points = [
    (0, (37.7833, -122.4090), 100),  # Point 0: Demand 100
    (1, (37.7950, -122.4028), 150),  # Point 1: Demand 150
    (2, (37.7730, -122.4312), 200),  # Point 2: Demand 200
    (3, (34.0600, -118.2300), 250),  # Point 3: Demand 250
    (4, (34.0400, -118.2500), 300)   # Point 4: Demand 300
]

max_vehicle_capacity = 400
```

**Grading Criteria:**

*   **Correctness:**  The solution must produce valid routes that satisfy all constraints (capacity limits, vehicle limits, single vehicle service, etc.).
*   **Optimality:** The solution will be evaluated based on the total travel distance of the routes.  Solutions with shorter total distances will receive higher scores.
*   **Efficiency:** The solution must be able to handle large input sizes (up to the specified constraints) within a reasonable time limit (e.g., a few minutes).
*   **Scalability:**  The chosen approach should ideally be scalable to even larger problem instances if resources permit.

**Note:** This is a complex optimization problem.  Finding the absolute optimal solution may be computationally intractable for larger inputs.  Focus on developing a good heuristic or approximation algorithm that provides near-optimal solutions within the given time and resource constraints.  Consider approaches like:

*   Greedy algorithms
*   Simulated annealing
*   Genetic algorithms
*   Clustering algorithms (e.g., k-means) followed by route optimization for each cluster (e.g., using a Traveling Salesperson Problem (TSP) solver).

You are free to use any standard Python libraries, but external packages that directly solve vehicle routing problems (VRP) are prohibited. You are expected to implement the core logic of the route optimization algorithm yourself.
