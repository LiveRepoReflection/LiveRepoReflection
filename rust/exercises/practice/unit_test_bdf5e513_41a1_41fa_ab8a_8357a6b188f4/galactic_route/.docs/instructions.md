Okay, here's a challenging Rust coding problem, designed to test a range of skills and encourage efficient solutions.

**Problem:**

**Intergalactic Route Optimization**

**Description:**

You are tasked with optimizing intergalactic travel routes for a newly formed Galactic Trade Federation. The galaxy is represented as a graph where:

*   **Nodes:** Represent star systems. Each star system has a unique ID (an integer), a resource production capacity (an integer), and a security risk level (an integer).
*   **Edges:** Represent wormholes connecting star systems. Each wormhole has a traversal cost (an integer) and a stability rating (a floating-point number between 0.0 and 1.0, inclusive).

The Federation wants to establish a trade route between a designated origin star system and a destination star system. The goal is to find the *most reliable* route that also satisfies a minimum resource transport requirement.

**Reliability of a Route:** The reliability of a route is the *product* of the stability ratings of all wormholes used in the route.  A higher reliability is better.

**Constraints:**

1.  **Minimum Resource Transport:** The route must be able to transport a minimum amount of resources. This is determined by the *minimum* resource production capacity of all star systems along the route (including the origin and destination). If this minimum capacity is less than the given resource requirement, the route is invalid, regardless of its reliability.

2.  **Security Threshold:** The Federation has a maximum acceptable total security risk. The total security risk of a route is the *sum* of the security risk levels of all star systems along the route (including the origin and destination). If the total risk exceeds the given threshold, the route is invalid.

3.  **Wormhole Usage Limit:** Due to energy constraints, a wormhole cannot be used more than once in a route.

4.  **Origin and Destination:** The route must start at the designated origin star system and end at the designated destination star system. The origin and destination star systems are distinct.

5.  **Graph Size:** The galaxy can contain up to 10,000 star systems and 50,000 wormholes.

6.  **Optimization:** The solution *must* be efficient. Brute-force approaches will likely time out.  Consider data structures and algorithms carefully. You will be judged on both correctness and performance.

**Input:**

*   A graph representation of the galaxy. This could be provided in various formats (e.g., adjacency list, adjacency matrix).  You should design your solution to handle a reasonable and well-documented input format.
*   The ID of the origin star system.
*   The ID of the destination star system.
*   The minimum resource transport requirement (an integer).
*   The maximum acceptable security risk (an integer).

**Output:**

*   The *maximum reliability* achievable for a valid route between the origin and destination, satisfying all constraints.
*   If no valid route exists, return 0.0.

**Example Scenario:**

Imagine a galaxy with several star systems, each producing different resources and posing varying security risks. Wormholes connect these systems, with some being more stable than others. The Federation needs to find the most reliable route for transporting a specific resource between two systems while staying within the security risk tolerance.

**Evaluation:**

Your solution will be evaluated on:

*   **Correctness:** Does it produce the correct maximum reliability for various test cases?
*   **Performance:** How efficiently does it find the optimal route, especially for large galaxies?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?
*   **Error Handling:** Does it gracefully handle invalid inputs or impossible scenarios?

**Hints:**

*   Consider using graph traversal algorithms like Dijkstra's or A\* search, but adapt them to handle the reliability calculation, resource transport requirement, and security risk threshold.  You will likely need a modified version.
*   Think about pruning the search space to avoid exploring paths that are clearly invalid or less promising.
*   Explore suitable data structures for efficient graph representation and priority queue implementation.
*   Be mindful of potential floating-point precision issues when calculating reliability.

This problem requires careful algorithm design, efficient implementation, and attention to detail. Good luck!
