## Problem: Adaptive Traffic Signal Control

### Question Description

A major city is experiencing severe traffic congestion, and the current fixed-time traffic signal system is proving inadequate. You are tasked with designing an adaptive traffic signal control system to optimize traffic flow at a critical intersection.

The intersection consists of four approaches (North, South, East, and West), each with dedicated lanes for through traffic, left turns, and right turns. Sensors are embedded in each lane to provide real-time traffic data, including queue lengths (number of vehicles waiting) and arrival rates (vehicles per second).

Your system must dynamically adjust the signal timings (green light duration for each approach) to minimize the average waiting time of vehicles at the intersection.

**Specifically, you need to implement a function that takes the current state of the intersection as input and returns an optimized signal timing plan.**

**Input:**

The input will be a data structure representing the intersection state. This structure will contain the following information for each approach (North, South, East, West):

-   `approach_name`: A string representing the approach (e.g., "North").
-   `through_queue`: An integer representing the queue length for through traffic.
-   `left_queue`: An integer representing the queue length for left turns.
-   `right_queue`: An integer representing the queue length for right turns.
-   `through_arrival_rate`: A float representing the arrival rate (vehicles/second) for through traffic.
-   `left_arrival_rate`: A float representing the arrival rate (vehicles/second) for left turns.
-   `right_arrival_rate`: A float representing the arrival rate (vehicles/second) for right turns.

You can represent the intersection state as a list of dictionaries, where each dictionary represents an approach. For example:

```python
intersection_state = [
    {
        "approach_name": "North",
        "through_queue": 50,
        "left_queue": 20,
        "right_queue": 10,
        "through_arrival_rate": 0.8,
        "left_arrival_rate": 0.3,
        "right_arrival_rate": 0.2,
    },
    {
        "approach_name": "South",
        "through_queue": 40,
        "left_queue": 15,
        "right_queue": 12,
        "through_arrival_rate": 0.7,
        "left_arrival_rate": 0.25,
        "right_arrival_rate": 0.22,
    },
    {
        "approach_name": "East",
        "through_queue": 60,
        "left_queue": 25,
        "right_queue": 8,
        "through_arrival_rate": 0.9,
        "left_arrival_rate": 0.4,
        "right_arrival_rate": 0.15,
    },
    {
        "approach_name": "West",
        "through_queue": 35,
        "left_queue": 18,
        "right_queue": 11,
        "through_arrival_rate": 0.6,
        "left_arrival_rate": 0.35,
        "right_arrival_rate": 0.2,
    },
]
```

**Output:**

The output should be a dictionary representing the optimized signal timing plan. The dictionary should contain the green light duration (in seconds) for each approach. The keys of the dictionary should be the approach names (e.g., "North", "South", "East", "West"), and the values should be the corresponding green light durations (floats). The total cycle length (sum of green light durations) should be between `min_cycle_length` and `max_cycle_length`, inclusive.

```python
{
    "North": 30.0,
    "South": 25.0,
    "East": 35.0,
    "West": 20.0,
}
```

**Constraints and Requirements:**

1.  **Cycle Length:** The total cycle length (sum of green light durations for all approaches) must be between `min_cycle_length` and `max_cycle_length` (inclusive). These values will be provided as input parameters to your function. Typical values might be 60 and 120 seconds, respectively.

2.  **Minimum Green Time:** Each approach must have a minimum green light duration (`min_green_time`). This value will be provided as an input parameter. A typical value might be 10 seconds. This is to ensure pedestrian safety.

3.  **Inter-green Time:** The time it takes to switch from one approach to another (yellow and all-red phases) is considered negligible and does not need to be explicitly modeled.

4.  **Optimization Goal:** Minimize the average waiting time of vehicles at the intersection. You need to define a suitable objective function that estimates the average waiting time based on queue lengths and arrival rates.  Consider all lanes when calculating average waiting time.

5.  **Fairness:**  While minimizing overall waiting time is important, the solution should also strive for fairness. No single approach should be consistently starved of green time.  Implement some mechanism to ensure a reasonable distribution of green time.

6.  **Efficiency:**  The solution must be computationally efficient.  The function should return a result within a reasonable time frame (e.g., a few seconds) for a typical intersection state.  Brute-force approaches will likely be too slow.

7.  **Edge Cases:** Handle edge cases such as zero queue lengths or arrival rates gracefully.  The system should be stable even under unusual traffic conditions.

8.  **Scalability:** While the problem is focused on a 4-way intersection, the solution should be designed with scalability in mind.  Consider how the algorithm could be adapted to handle intersections with more approaches.

9. **Real-time Adaptation:** The function will be called periodically (e.g., every few seconds) with updated intersection state data. Therefore, the solution needs to be able to adapt quickly to changing traffic conditions.

**Function Signature:**

```python
def optimize_signal_timings(
    intersection_state: list[dict],
    min_cycle_length: int,
    max_cycle_length: int,
    min_green_time: int,
) -> dict[str, float]:
    """
    Optimizes traffic signal timings for a four-way intersection.

    Args:
        intersection_state: A list of dictionaries, where each dictionary represents an approach
            and contains traffic data (queue lengths, arrival rates).
        min_cycle_length: The minimum total cycle length (in seconds).
        max_cycle_length: The maximum total cycle length (in seconds).
        min_green_time: The minimum green light duration for each approach (in seconds).

    Returns:
        A dictionary representing the optimized signal timing plan, with approach names as keys
        and green light durations (in seconds) as values.
    """
    # Your code here
    pass
```

**Example:**

```python
intersection_state = [
    {
        "approach_name": "North",
        "through_queue": 50,
        "left_queue": 20,
        "right_queue": 10,
        "through_arrival_rate": 0.8,
        "left_arrival_rate": 0.3,
        "right_arrival_rate": 0.2,
    },
    {
        "approach_name": "South",
        "through_queue": 40,
        "left_queue": 15,
        "right_queue": 12,
        "through_arrival_rate": 0.7,
        "left_arrival_rate": 0.25,
        "right_arrival_rate": 0.22,
    },
    {
        "approach_name": "East",
        "through_queue": 60,
        "left_queue": 25,
        "right_queue": 8,
        "through_arrival_rate": 0.9,
        "left_arrival_rate": 0.4,
        "right_arrival_rate": 0.15,
    },
    {
        "approach_name": "West",
        "through_queue": 35,
        "left_queue": 18,
        "right_queue": 11,
        "through_arrival_rate": 0.6,
        "left_arrival_rate": 0.35,
        "right_arrival_rate": 0.2,
    },
]

min_cycle_length = 60
max_cycle_length = 120
min_green_time = 10

optimized_timings = optimize_signal_timings(
    intersection_state, min_cycle_length, max_cycle_length, min_green_time
)
print(optimized_timings)
```

**Judging Criteria:**

The solution will be judged based on the following criteria:

*   **Correctness:** The solution produces valid signal timing plans that adhere to the specified constraints (cycle length, minimum green time).
*   **Optimality:** The solution effectively minimizes the average waiting time of vehicles at the intersection.
*   **Efficiency:** The solution is computationally efficient and returns a result within a reasonable time frame.
*   **Fairness:** The solution provides a reasonably fair distribution of green time among the different approaches.
*   **Robustness:** The solution handles edge cases and unusual traffic conditions gracefully.
*   **Code Quality:** The code is well-structured, readable, and maintainable.
*   **Explanation:** A clear explanation of the algorithm and the rationale behind the design choices is provided.

This problem requires a combination of algorithmic thinking, optimization techniques, and practical considerations. Good luck!
