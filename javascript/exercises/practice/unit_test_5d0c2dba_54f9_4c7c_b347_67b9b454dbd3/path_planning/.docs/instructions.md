## Project Name

`Autonomous Vehicle Path Planning`

## Question Description

You are tasked with developing the path planning module for an autonomous vehicle navigating a complex urban environment. The environment is represented as a directed graph where nodes represent intersections and edges represent road segments connecting them. Each road segment has a length (distance in meters) and a set of traffic signals associated with it. The vehicle must navigate from a given start intersection to a given destination intersection efficiently and safely, obeying traffic laws and considering dynamic factors.

**Graph Representation:**

The environment is represented as a directed graph. Each node (intersection) is identified by a unique integer ID. Each edge (road segment) is defined by:

*   `source`: Integer ID of the starting intersection.
*   `destination`: Integer ID of the ending intersection.
*   `length`: Length of the road segment in meters (positive integer).
*   `speed_limit`: Speed limit of the road segment in km/h (positive integer).
*   `traffic_signals`: An array of traffic signal objects along the road segment.  Each traffic signal object has the following attributes:
    *   `position`: Distance from the source intersection in meters (positive integer, must be less than `length`).
    *   `cycle`: An array of strings representing the traffic light cycle. For example: `["red", "red", "green", "yellow"]`.
    *   `durations`: An array of numbers representing the duration of each traffic light state in seconds, corresponding to the `cycle` array. For example: `[30, 3, 30, 3]`. (positive integers).
    *   `offset`: The time (in seconds) from the start of simulation that the cycle begins. (non-negative integers).

**Objective:**

Implement a function that finds the optimal path from a given `start` intersection to a given `destination` intersection. The optimality criteria is based on a weighted combination of travel time and risk, defined as follows:

*   **Travel Time:** The total time taken to traverse the path, considering road segment lengths, speed limits, and waiting times at traffic signals. The travel time calculation must consider speed limits and calculate travel time accurately down to the second.
*   **Risk:** The sum of risk scores associated with each road segment in the path. The risk score for each road segment is calculated as: `risk_factor * (number_of_lane_changes + congestion_level)`, where:
    *   `number_of_lane_changes` is estimated based on the road segment's characteristics (assume a constant value of 2 for each road segment for simplicity).
    *   `congestion_level` is a dynamically changing integer value (between 0 and 10, inclusive) associated with each road segment. This value is provided as input to your function.
    *   `risk_factor` is a constant value provided as input to your function.

The overall cost of a path is calculated as:

`cost = weight_time * travel_time + weight_risk * risk`

where `weight_time` and `weight_risk` are input parameters representing the relative importance of travel time and risk, respectively.

**Function Signature:**

```javascript
/**
 * Finds the optimal path from start to destination in a graph.
 *
 * @param {number} start The starting intersection ID.
 * @param {number} destination The destination intersection ID.
 * @param {object} graph A graph represented as an adjacency list where keys are intersection IDs
 *                       and values are arrays of objects representing outgoing edges.
 *                       Each edge object has the following properties:
 *                       { destination: number, length: number, speed_limit: number, traffic_signals: [] }
 * @param {object} congestionLevels An object where keys are tuples of (source, destination) intersection IDs
 *                                  representing road segments and values are congestion levels (integers between 0 and 10).
 * @param {number} riskFactor A constant factor to multiply the risk score (positive number).
 * @param {number} weightTime The weight for travel time in the cost function (positive number).
 * @param {number} weightRisk The weight for risk in the cost function (positive number).
 * @param {number} currentTime The current time in seconds from start of simulation (non-negative integer). Used to calculate traffic light state.
 *
 * @returns {Array<number> | null} An array of intersection IDs representing the optimal path from start to destination,
 *                                 or null if no path exists.
 */
function findOptimalPath(start, destination, graph, congestionLevels, riskFactor, weightTime, weightRisk, currentTime) {
  // Your code here
}
```

**Constraints:**

*   The graph can be large (up to 1000 intersections and 5000 road segments).
*   Road segments can have multiple traffic signals.
*   The traffic signal cycle durations can vary significantly.
*   Congestion levels can change dynamically, affecting path costs.
*   The algorithm must be efficient enough to find a path within a reasonable time frame (e.g., 1 second).  Consider using appropriate data structures and algorithmic optimizations.
*   You must handle the case where no path exists between the start and destination.
*   You must handle edge cases such as invalid input parameters (e.g., negative lengths, invalid congestion levels).
*   The optimal path must minimize the cost function as described above.
*   Assume speeds lower than 1 km/h are equivalent to 0 km/h.

**Assumptions:**

*   The vehicle travels at the speed limit on each road segment (unless stopped by a traffic signal).
*   The vehicle can instantaneously accelerate and decelerate to the speed limit.
*   Lane changes occur instantly at the beginning of each road segment.
*   The graph is strongly connected (there is a path between any two nodes, although not necessarily a direct edge).

**Example:**

```javascript
const graph = {
  1: [{ destination: 2, length: 1000, speed_limit: 50, traffic_signals: [] }],
  2: [{ destination: 3, length: 500, speed_limit: 30, traffic_signals: [] }],
  3: []
};

const congestionLevels = {
  '1,2': 5,
  '2,3': 2
};

const riskFactor = 1.0;
const weightTime = 0.5;
const weightRisk = 0.5;
const currentTime = 0;

const optimalPath = findOptimalPath(1, 3, graph, congestionLevels, riskFactor, weightTime, weightRisk, currentTime);

console.log(optimalPath); // Expected output: [1, 2, 3] (or equivalent based on cost calculation)
```

**Judging Criteria:**

Your solution will be judged based on:

*   **Correctness:** The algorithm must find a valid path (if one exists) and calculate the cost accurately.
*   **Efficiency:** The algorithm must be efficient enough to handle large graphs within a reasonable time frame.
*   **Code Quality:** The code must be well-structured, readable, and maintainable.
*   **Handling Edge Cases:** The algorithm must handle invalid input and edge cases gracefully.
*   **Optimization:** The ability to minimize the cost function based on the given weights.
