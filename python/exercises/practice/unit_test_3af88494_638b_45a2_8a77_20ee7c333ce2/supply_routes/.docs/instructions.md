## The Disrupted Supply Chain

**Question Description:**

A global logistics company, "OmniFlow," manages a complex supply chain network connecting numerous warehouses, factories, and distribution centers across the world. Due to a series of unexpected geopolitical events, certain transportation routes within OmniFlow's network have been disrupted.

The network can be represented as a weighted, directed graph where:

*   Nodes represent locations (warehouses, factories, distribution centers). Each location has a name.
*   Directed edges represent transportation routes between locations. Each route has a cost associated with it (representing transportation time, fuel consumption, etc.).
*   A subset of edges represents "disrupted routes," which are now unusable.

OmniFlow needs to re-evaluate its shipping strategies to minimize the cost of transporting goods from several origin locations to several destination locations, avoiding all disrupted routes.

Your task is to write a function that takes the following inputs:

1.  **`graph`:** A dictionary representing the graph. The keys are location names (strings), and the values are dictionaries mapping neighboring location names (strings) to their associated costs (integers).  For example:
    ```python
    graph = {
        "WarehouseA": {"Factory1": 10, "DistributionCenterX": 15},
        "Factory1": {"DistributionCenterX": 5, "WarehouseB": 12},
        "DistributionCenterX": {"WarehouseB": 8},
        "WarehouseB": {}
    }
    ```

2.  **`disrupted_routes`:** A list of tuples, where each tuple represents a disrupted route in the form `(origin_location, destination_location)`. For example:
    ```python
    disrupted_routes = [("WarehouseA", "Factory1"), ("Factory1", "WarehouseB")]
    ```

3.  **`origins`:** A list of origin location names (strings).

4.  **`destinations`:** A list of destination location names (strings).

The function should return a dictionary where:

*   Keys are tuples representing all possible origin-destination pairs, in the form `(origin_location, destination_location)`. The order of the `origin_location` and `destination_location` must match the order they appear in the inputs `origins` and `destinations`. If `origins` is `["A", "B"]` and `destinations` is `["X", "Y"]`, the keys must be `("A", "X")`, `("A", "Y")`, `("B", "X")`, and `("B", "Y")`.
*   Values are the minimum cost to transport goods from the origin to the destination, considering the disrupted routes. If no path exists between an origin and destination, the value should be `float('inf')`.

**Constraints and Requirements:**

*   The graph can be large (up to 10,000 nodes and 100,000 edges).
*   The number of disrupted routes can be significant (up to 10,000).
*   The number of origin and destination locations can be up to 100.
*   The cost of each route is a non-negative integer.
*   You must avoid using disrupted routes.
*   The function must be efficient and have a reasonable time complexity, especially considering the size of the graph. Inefficient solutions will likely time out.
*   The graph might contain cycles.
*   Location names are unique.
*   Consider potential integer overflow issues when calculating costs, though preventing it entirely is not required. Reasonable overflow prevention is considered a plus.

**Example:**

```python
graph = {
    "WarehouseA": {"Factory1": 10, "DistributionCenterX": 15},
    "Factory1": {"DistributionCenterX": 5, "WarehouseB": 12},
    "DistributionCenterX": {"WarehouseB": 8},
    "WarehouseB": {}
}
disrupted_routes = [("WarehouseA", "Factory1")]
origins = ["WarehouseA", "Factory1"]
destinations = ["WarehouseB", "DistributionCenterX"]

result = solve(graph, disrupted_routes, origins, destinations)

# Expected Output:
# {
#   ("WarehouseA", "WarehouseB"): 23,  # WarehouseA -> DistributionCenterX -> WarehouseB (15 + 8)
#   ("WarehouseA", "DistributionCenterX"): 15, # WarehouseA -> DistributionCenterX (15)
#   ("Factory1", "WarehouseB"): 12, # Factory1 -> WarehouseB (12)
#   ("Factory1", "DistributionCenterX"): 5 # Factory1 -> DistributionCenterX (5)
# }

```
