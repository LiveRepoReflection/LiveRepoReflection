Okay, here's a challenging coding problem designed to test a variety of skills, inspired by your request for a "Hard" level LeetCode-style problem.

## Problem: Optimal Traffic Flow Rescheduling

**Question Description:**

A major metropolitan area's traffic management system is experiencing a critical failure due to a cyberattack. The system controls traffic light timings across the city, and now all lights are stuck in a fixed, suboptimal cycle. You are tasked with developing an algorithm to reschedule the traffic light timings in real-time to minimize congestion and maximize traffic flow during peak hours.

The city's road network is represented as a directed graph where:

*   **Nodes:** Represent intersections with traffic lights.
*   **Edges:** Represent road segments between intersections. Each edge has a `length` (in meters) and a `speed_limit` (in km/h).

You are given the following inputs:

1.  `graph`: A dictionary representing the road network. Keys are intersection IDs (integers), and values are dictionaries. Each inner dictionary represents outgoing edges from that intersection, structured as:

    ```python
    graph = {
        1: {  # Intersection ID
            2: {"length": 500, "speed_limit": 50},  # Destination: {length: meters, speed_limit: km/h}
            3: {"length": 800, "speed_limit": 60}
        },
        2: {
            4: {"length": 1200, "speed_limit": 40}
        },
        # ... more intersections and edges
    }
    ```

2.  `demand`: A dictionary representing the expected traffic flow between origin-destination pairs during peak hours. Keys are tuples `(origin_intersection, destination_intersection)`, and values are the number of vehicles per hour expected to travel between those intersections.

    ```python
    demand = {
        (1, 4): 300, # 300 vehicles per hour from intersection 1 to 4
        (2, 5): 200,
        # ... more origin-destination pairs
    }
    ```

3.  `light_cycles`: A dictionary where the key is the intersection ID and the value is a list of integers representing the cycle length of the traffic light at that intersection. You need to optimize the red and green intervals for each traffic light. The total cycle length is the sum of red and green intervals. Assume there are 2 phases, Red and Green.

    ```python
    light_cycles = {
        1: [30, 30],  # Intersection 1 has a 60-second cycle (30 seconds red, 30 seconds green).
        2: [40, 20],  # Intersection 2 has a 60-second cycle (40 seconds red, 20 seconds green).
        # ... more intersections
    }
    ```

4.  `optimization_target`: A string indicating the optimization target. It can be one of the following: `"travel_time"` or `"throughput"`.
    * If `optimization_target` is `"travel_time"`, you should minimize the total travel time for all vehicles based on the demand.
    * If `optimization_target` is `"throughput"`, you should maximize the number of vehicles that can reach their destination within a set time limit. You can assume the time limit to be 3600 seconds (1 hour).

**Your Task:**

Write a function `optimize_traffic_flow(graph, demand, light_cycles, optimization_target)` that takes the graph, demand, initial light cycles, and optimization target as input. The function should return a new `light_cycles` dictionary with optimized red and green intervals for each intersection.

**Constraints and Considerations:**

*   **Cycle Length:** The total cycle length (sum of red and green intervals) for each traffic light must remain constant. You cannot change the total cycle length, only the distribution of red and green time.
*   **Integer Values:** Red and green intervals must be non-negative integers.
*   **Realistic Intervals:**  The red and green times must be at least 5 seconds long ( to avoid very short changes that may cause more interruption.)
*   **Optimization:** Finding the globally optimal solution is likely intractable. Focus on developing a reasonably efficient heuristic or approximation algorithm that provides significant improvement over the initial light cycles. Consider gradient-based or heuristic search.
*   **Edge Cases:** Handle cases where there is no demand between certain origin-destination pairs, or where the graph is disconnected.
*   **Efficiency:** The algorithm should be reasonably efficient. Consider the time complexity of your solution, as the city's traffic management system needs to react quickly.
*   **Real-World Modeling:**  Think about how traffic lights affect traffic flow.  Longer red times can cause queues to build up, increasing travel time.  Shorter green times might not allow enough vehicles to pass through before the light turns red again. You will need to create a model to represent this.

**Further Considerations for Increased Difficulty (Optional):**

*   **Dynamic Demand:** The `demand` changes over time.  Implement a mechanism to re-optimize the light cycles periodically based on updated demand data.
*   **Accidents/Road Closures:**  The `graph` can be modified (edges removed) to simulate accidents or road closures.  Your algorithm should be able to adapt to these changes.
*   **Multi-Objective Optimization:**  Simultaneously optimize for both travel time and throughput, perhaps by introducing a weighting factor.
*   **Limited Resources:** Assume you have limited computational resources and memory. Your algorithm should be efficient and memory-conscious.

This problem requires a combination of graph algorithms, optimization techniques, and a good understanding of traffic flow dynamics. Good luck!
