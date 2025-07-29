## Question: Decentralized Collaborative Pathfinding

### Problem Description

Imagine a large, distributed system of autonomous agents (robots, drones, etc.) navigating a complex and dynamic environment represented as a grid. Each agent needs to find a path from its starting location to its designated target location.  However, direct communication between all agents is impossible due to network constraints, limited bandwidth, and security concerns. Instead, agents can only communicate locally within a limited radius.

Your task is to design and implement a decentralized collaborative pathfinding algorithm that allows agents to find optimal or near-optimal paths while adhering to these constraints:

1.  **Decentralization:** Each agent operates independently, making decisions based only on its local perception of the environment and limited communication with nearby agents. No central authority or global knowledge is available.

2.  **Limited Communication:** Agents can only directly communicate with other agents within a fixed radius (communication range).  This communication can involve exchanging path information, obstacle detections, or other relevant data.

3.  **Dynamic Environment:** The environment is not static. Obstacles can appear or disappear dynamically. Other agents' movements also create dynamic obstacles. Agents must be able to adapt their paths in real-time to these changes.

4.  **Collision Avoidance:** Paths should be collision-free. Agents must avoid colliding with static obstacles, other agents, and dynamically appearing obstacles. Collisions should be avoided at all costs. Soft penalties are not enough.

5.  **Path Optimality:** While finding a guaranteed shortest path might be computationally infeasible in this decentralized setting, your algorithm should strive to find paths that are as close to optimal as possible in terms of path length or travel time.

6.  **Scalability:** The algorithm should be scalable to a large number of agents. The computational complexity of an agent's decision-making process should not increase dramatically as the number of agents in the system grows.

7. **Real-time constraints:** Each agent has a limited time budget for each decision making cycle. If the agent can't find a reasonable path during its time budget, it must decide anyway with the best result so far.

### Input

*   **Grid Dimensions:** `width` and `height` representing the dimensions of the grid.
*   **Agent Count:** `n` representing the number of agents in the system.
*   **Agent Configurations:** A list of tuples, where each tuple `(start_x, start_y, target_x, target_y)` represents the starting and target coordinates for an agent.
*   **Static Obstacles:** A set of coordinate tuples `(x, y)` representing the locations of static obstacles on the grid.
*   **Communication Range:** `communication_range` representing the maximum distance between two agents for direct communication.
*   **Decision Time Budget:** `time_budget` representing the maximum time each agent can take to make a decision at each step.
*   **Simulation Steps:** `max_steps` representing the maximum number of simulation steps.

### Output

A list of lists, where each inner list represents the path taken by each agent.  Each path is a list of coordinate tuples `(x, y)` representing the agent's movement over time. If an agent fails to reach its destination within the specified `max_steps`, its path should be the path it took until that point.

### Constraints

*   1 <= `width`, `height` <= 500
*   1 <= `n` <= 200
*   0 <= `start_x`, `start_y`, `target_x`, `target_y` < `width` and `height`
*   0 <= `communication_range` <= `sqrt(width^2 + height^2)`
*   1 <= `time_budget` <= 100 milliseconds (realistic time for calculations and communications)
*   1 <= `max_steps` <= 1000
*   Agents cannot occupy the same grid cell at the same time.
*   All agents start at step 0.

### Evaluation Criteria

Your solution will be evaluated based on the following criteria:

*   **Correctness:** All agents must eventually reach their destination without collisions.
*   **Path Optimality:** The average path length of all agents should be minimized.
*   **Scalability:** The execution time of your algorithm should not scale poorly as the number of agents increases.
*   **Robustness:** The algorithm should be robust to dynamic changes in the environment (appearance/disappearance of obstacles).
*   **Efficiency:** The algorithm should be computationally efficient, respecting the `time_budget` constraint.
*   **Decentralization:** The algorithm must truly be decentralized, with agents making decisions based only on local information.

This problem requires a combination of pathfinding algorithms (A\*, Dijkstra, etc.), distributed systems concepts, collision avoidance techniques, and optimization strategies. Good luck!
