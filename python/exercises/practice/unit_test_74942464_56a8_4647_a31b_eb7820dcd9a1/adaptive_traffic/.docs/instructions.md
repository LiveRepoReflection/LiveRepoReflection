## Project Name

`AdaptiveTrafficControl`

## Question Description

You are tasked with designing an adaptive traffic control system for a city. The city's road network is represented as a directed graph where nodes are intersections and edges are roads connecting them. Each road has a capacity, representing the maximum number of vehicles that can traverse it per unit time.

The traffic demand between any two intersections varies throughout the day. You are given a series of time intervals, each with a specific traffic demand pattern. A traffic demand pattern consists of a matrix where `demand[i][j]` represents the number of vehicles that need to travel from intersection `i` to intersection `j` during that time interval.

Your system needs to dynamically adjust traffic light timings at each intersection to minimize the overall congestion in the network. Congestion on a road is defined as the ratio of the actual traffic flow on that road to its capacity. The overall congestion in the network is the sum of congestion on all roads.

**Specifically, you need to implement a function that takes the following inputs:**

*   `graph`: A dictionary representing the road network. Keys are the source intersections (nodes), and values are dictionaries representing outgoing roads. For each outgoing road, the key is the destination intersection (node), and the value is the road's capacity.
    ```python
    graph = {
        0: {1: 100, 2: 50},  # From intersection 0 to 1 (capacity 100) and 0 to 2 (capacity 50)
        1: {2: 75},          # From intersection 1 to 2 (capacity 75)
        2: {}                # No outgoing roads from intersection 2
    }
    ```
*   `demands`: A list of traffic demand patterns. Each demand pattern is a matrix (list of lists) where `demands[t][i][j]` represents the traffic demand from intersection `i` to intersection `j` during time interval `t`.
    ```python
    demands = [
        [[0, 60, 20], [0, 0, 30], [0, 0, 0]],  # Time interval 0: demands[0][i][j]
        [[0, 40, 10], [0, 0, 20], [0, 0, 0]]   # Time interval 1: demands[1][i][j]
    ]
    ```
*   `max_green_time`: An integer representing the maximum green light time allowed at each intersection. This constraint influences the possible traffic flow control at each intersection.
*   `time_limit`: The maximum time in seconds allowed for your function to run. Solutions exceeding this limit will be terminated. This constraint is critical for optimizing algorithmic efficiency.

**Your function should return:**

*   A list of traffic flow assignments for each time interval. Each traffic flow assignment is a dictionary where keys are tuples representing roads (source intersection, destination intersection), and values are the actual traffic flow on that road during that time interval.

    ```python
    [
        {(0, 1): 60, (0, 2): 20, (1, 2): 30},  # Traffic flows during time interval 0
        {(0, 1): 40, (0, 2): 10, (1, 2): 20}   # Traffic flows during time interval 1
    ]
    ```

**Constraints:**

*   The graph can have up to 50 intersections.
*   The number of time intervals can be up to 20.
*   Road capacities are integers between 1 and 1000.
*   Traffic demands are integers between 0 and 500.
*   `max_green_time` is an integer between 10 and 60 seconds.
*   `time_limit` is an integer between 10 and 60 seconds.
*   You **must** find a flow assignment that satisfies the road capacities. Total flow on each road must be less than or equal to the road's capacity.
*   All traffic demand must be satisfied if possible. If the network does not have the capacity to satisfy all demand, you should prioritize satisfying as much demand as possible while minimizing congestion.

**Scoring:**

Your solution will be evaluated based on the following criteria:

1.  **Correctness:** The traffic flow assignments must be feasible (respect road capacities) and satisfy the demands as much as possible.
2.  **Congestion Minimization:** The lower the overall congestion in the network, the better.
3.  **Efficiency:** Your solution must run within the given `time_limit`. Solutions that time out will receive a score of 0.

This problem requires you to combine graph algorithms (specifically, flow algorithms), optimization techniques, and system design considerations to create a practical and efficient traffic control system. Be prepared to explore different approaches and trade-offs to achieve the best possible solution. You will likely need to use advanced techniques to optimize performance and avoid exceeding the time limit for larger problem instances.
