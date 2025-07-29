## Question: Optimal Emergency Response Routing

### Question Description

A major metropolitan area is divided into a grid of interconnected nodes. Each node represents a location, and the connections between nodes represent roads. The city is experiencing a series of emergencies, and the fire department needs a system to optimally route fire trucks from fire stations to emergency locations.

You are tasked with designing and implementing an algorithm to determine the optimal routes for fire trucks to respond to emergencies, minimizing response time.

**Specifics:**

*   **Grid Representation:** The city is represented as a weighted graph where nodes are locations (identified by unique integer IDs) and edges are roads. The weight of each edge represents the travel time (in minutes) along that road. The graph can be assumed to be undirected.

*   **Fire Stations:** There are multiple fire stations located at specific nodes within the grid. Each fire station has a limited number of fire trucks.

*   **Emergency Locations:** Emergencies occur at specific nodes in the grid. Multiple emergencies can occur simultaneously.

*   **Truck Capacity:** Each fire truck can only respond to *one* emergency at a time. Once a truck has responded to an emergency, it returns to its originating fire station.

*   **Optimization Goal:** Minimize the *maximum* response time across all emergencies. That is, find the assignment of fire trucks to emergencies that minimizes the largest response time for any single emergency. This is crucial for ensuring a fair and timely response across the city. Response time is defined as the time it takes for a truck to travel from its station to the emergency location. The return time to the station is not included in the response time calculation.

*   **Real-time Constraints:** The system needs to be able to handle updates to the graph (road closures, changes in traffic patterns that affect travel times) and new emergency reports in real-time. The routing algorithm should be efficient enough to provide near-instantaneous results for a reasonable number of emergencies.

**Input:**

Your function will receive the following inputs:

1.  `graph`: A dictionary representing the graph. Keys are node IDs (integers), and values are dictionaries representing adjacent nodes and edge weights (travel times). For example:
    ```python
    graph = {
        1: {2: 10, 3: 15},  # Node 1 is connected to node 2 with weight 10, and node 3 with weight 15
        2: {1: 10, 4: 20},
        3: {1: 15, 4: 5},
        4: {2: 20, 3: 5}
    }
    ```
2.  `fire_stations`: A dictionary representing the fire stations. Keys are node IDs (integers) representing the fire station locations, and values are the number of fire trucks available at each station. For example:
    ```python
    fire_stations = {
        1: 2,  # Fire station at node 1 has 2 trucks
        2: 1   # Fire station at node 2 has 1 truck
    }
    ```
3.  `emergencies`: A list of node IDs (integers) representing the locations of emergencies. For example:
    ```python
    emergencies = [3, 4, 3]  # Emergencies at nodes 3, 4, and 3
    ```

**Output:**

Your function must return a dictionary representing the optimal assignment of fire trucks to emergencies. Keys are emergency node IDs, and values are the fire station node IDs from which the truck should be dispatched.  Return `None` if not all emergencies can be handled by available fire trucks.

For example:
```python
{
    3: 1,  # Emergency at node 3 is handled by a truck from fire station at node 1
    4: 2,  # Emergency at node 4 is handled by a truck from fire station at node 2
    3: 1   # Emergency at node 3 is handled by a truck from fire station at node 1
}
```

**Constraints:**

*   The graph can be large (up to 10,000 nodes and 50,000 edges).
*   The number of fire stations can be up to 100.
*   The number of emergencies can be up to 1,000.
*   Travel times are positive integers.
*   You must use an efficient algorithm to find the optimal assignment.  Brute-force approaches will likely time out.
*   The graph may not be fully connected.
*   Multiple fire stations might exist at the same node ID, and the available trucks should be cumulative.
*   Multiple emergencies can occur at the same node ID.

**Evaluation:**

Your solution will be evaluated based on:

*   **Correctness:** The solution must correctly assign fire trucks to emergencies such that the maximum response time is minimized.
*   **Efficiency:** The solution must be efficient enough to handle large graphs and a reasonable number of emergencies within a time limit.
*   **Scalability:** The solution should scale well as the size of the graph and the number of emergencies increases.
*   **Handling of Edge Cases:** The solution should handle all edge cases, such as disconnected graphs, insufficient fire trucks, and multiple emergencies at the same location.

This problem requires a combination of graph algorithms, optimization techniques, and careful consideration of real-world constraints to achieve an efficient and scalable solution. Good luck!
