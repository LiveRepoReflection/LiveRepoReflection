## Question: Decentralized Autonomous Drone Swarm (DADS) Coordinator

**Description:**

You are tasked with designing the core coordination algorithm for a Decentralized Autonomous Drone Swarm (DADS). This swarm operates in a challenging, dynamic environment where communication is unreliable and drones can fail unexpectedly. The swarm's primary goal is to explore an unknown area, mapping points of interest (POIs) efficiently while maintaining swarm cohesion and minimizing redundant exploration.

Each drone in the swarm has limited computational power and memory. They can communicate with other drones within a limited range, but messages can be lost or delayed. Drones are identified by unique integer IDs.

Your task is to implement a function that allows each drone to decide its next action based on its local view of the swarm and its environment. The action space is simplified to choosing a target location on a 2D grid.

**Input:**

Your function will receive the following inputs:

*   `drone_id` (int): The unique ID of the drone making the decision.
*   `current_location` (tuple of ints): The (x, y) coordinates of the drone's current location.
*   `communication_range` (int): The maximum distance within which drones can communicate reliably.
*   `known_drones` (dict): A dictionary where the key is the drone ID (int) and the value is a tuple representing the last known (x, y) location of that drone. This represents the drone's local view of the swarm. Note that this information might be stale or incomplete.
*   `explored_areas` (set of tuples): A set of (x, y) coordinates representing areas that this drone has already explored.
*   `poi_candidates` (list of tuples): A list of (x, y) coordinates representing potential Points of Interest that the drone has identified. This list is drone-specific and changes over time.
*   `global_bounds` (tuple of tuples): A tuple defining the exploration area boundaries: `((min_x, min_y), (max_x, max_y))`.  Drones cannot leave this area.
*   `battery_level` (float): A number between 0.0 and 1.0 representing the drone's remaining battery capacity. Moving to a new location costs battery (as defined in the constraints).

**Output:**

Your function must return a tuple representing the (x, y) coordinates of the drone's next target location. The location must be within the `global_bounds`. If the drone cannot find a valid location, it should return its `current_location`.

**Constraints:**

1.  **Decentralization:** The decision-making process MUST be based solely on the drone's local information (the inputs provided). No global state or centralized coordination is allowed.
2.  **Swarm Cohesion:** Drones should aim to maintain a reasonable distance from each other to avoid clustering, but also avoid becoming isolated. Define a minimum and maximum acceptable distance between drones.
3.  **Efficient Exploration:** Drones should prioritize exploring unknown areas. They should avoid revisiting already `explored_areas` as much as possible.
4.  **POI Prioritization:** Drones should prioritize visiting `poi_candidates`, but not at the expense of efficient exploration or swarm cohesion.
5.  **Boundary Awareness:** The drone MUST stay within the `global_bounds`.
6.  **Battery Management:**  Moving to a new location consumes battery power. The cost is proportional to the distance travelled. Moving one unit in either x or y direction costs 0.001 battery. Drones cannot move if their `battery_level` is insufficient. The drone should return to its current location if it cannot reach any other location due to low battery.
7.  **Communication Unreliability:** The `known_drones` information is not guaranteed to be up-to-date or complete. Drones must be robust to missing or stale information.
8.  **Drone Failure:** Other drones might fail at any moment. Your algorithm should be able to handle changes in the `known_drones` list.
9.  **Optimization:** The solution should be as efficient as possible, considering the limited computational resources of each drone. Avoid computationally expensive operations where possible. The code should execute within a time limit.

**Judging Criteria:**

Your solution will be evaluated based on the following criteria:

*   **Coverage:** How much of the exploration area is covered by the swarm.
*   **Cohesion:** How well the swarm maintains its structure and avoids clustering or isolation.
*   **POI Discovery:** How many POIs are successfully visited by the swarm.
*   **Resource Efficiency:** How efficiently the drones use their battery power.
*   **Robustness:** How well the swarm adapts to drone failures and communication unreliability.
*   **Computational Efficiency:** How quickly the algorithm executes given the limitations of each drone.

This problem requires a combination of pathfinding, resource management, and distributed decision-making. Good luck!
