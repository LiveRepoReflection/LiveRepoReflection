## Question: Optimal Traffic Light Synchronization

### Question Description

You are tasked with optimizing the synchronization of traffic lights in a city to minimize the average travel time of vehicles along a major avenue. The avenue is represented as a straight line with `N` traffic lights numbered from 1 to `N`. Each traffic light has a cycle of alternating green and red phases.

**Input:**

*   `N`: The number of traffic lights along the avenue (1 <= `N` <= 1000).
*   `distances`: An array of `N-1` integers representing the distances between consecutive traffic lights. `distances[i]` is the distance between traffic light `i` and `i+1` (1 <= `distances[i]` <= 1000).
*   `cycleLengths`: An array of `N` integers representing the cycle length of each traffic light. `cycleLengths[i]` is the total time (in seconds) for one complete cycle (green + red) of traffic light `i` (1 <= `cycleLengths[i]` <= 3600).
*   `greenDurations`: An array of `N` integers representing the duration of the green phase for each traffic light. `greenDurations[i]` is the duration (in seconds) of the green phase for traffic light `i` (1 <= `greenDurations[i]` < `cycleLengths[i]`).
*   `speedLimit`: An integer representing the speed limit on the avenue in meters per second. Assume constant speed (1 <= `speedLimit` <= 30).

**Synchronization:**

You can control the initial offset (in seconds) of each traffic light. The offset determines when the cycle starts. An offset of 0 means the traffic light starts its cycle with the green phase at time 0. The offset must be an integer value.

**Objective:**

Determine the optimal offsets for each traffic light to minimize the average travel time for a single vehicle traveling from traffic light 1 to traffic light `N`. The average travel time is calculated as the total time taken to travel from traffic light 1 to traffic light `N`. The vehicle always starts at time 0 at traffic light 1.

**Constraints:**

*   The offset for each traffic light must be between 0 and `cycleLengths[i] - 1` (inclusive).
*   Assume that the vehicle accelerates instantaneously to the speed limit.
*   If a vehicle arrives at a traffic light during its green phase, it passes through without delay.
*   If a vehicle arrives at a traffic light during its red phase, it must wait until the green phase begins.
*   Your solution must be computationally efficient. Brute-force approaches will likely time out for larger inputs. Consider the trade-offs between accuracy and speed.
*   The distances are given in meters.

**Output:**

An array of `N` integers representing the optimal offsets for each traffic light that minimizes the average travel time. If multiple optimal solutions exist, return any one of them.

**Example:**

`N = 3`

`distances = [100, 200]`

`cycleLengths = [60, 60, 60]`

`greenDurations = [30, 30, 30]`

`speedLimit = 10`

A possible solution might involve offsets that allow the car to pass through all traffic lights without stopping at the red lights. The goal is to find such offsets or offsets that minimize the waiting time at red lights.

**Scoring:**

Your solution will be evaluated based on its correctness and efficiency. Test cases will include:

*   Small test cases with easily optimizable solutions.
*   Larger test cases where brute-force is not feasible, requiring more sophisticated algorithms.
*   Edge cases, such as traffic lights with very short or very long cycle lengths.
*   Cases where synchronizing all lights perfectly is impossible.

**Note:**

This problem requires a combination of algorithmic thinking, data structure knowledge, and optimization techniques.  Think about how you can efficiently explore the possible offset combinations to find the best solution within the given time constraints.  Consider techniques like dynamic programming, greedy algorithms, or heuristics. The core challenge is to balance the exploration of the offset space with the need for computational efficiency.
