## Project Name

`Multi-Source Shortest Path with Time Windows`

## Question Description

You are tasked with optimizing the delivery schedule for a fleet of delivery drones operating in a city. The city is represented as a directed graph where nodes are delivery locations and edges represent routes between locations. Each location has a specific time window during which deliveries can be made. The drones can only deliver within these time windows.

You are given the following information:

*   `N`: The number of delivery locations in the city, numbered from 0 to N-1.
*   `edges`: A list of directed edges represented as tuples `(u, v, w)`, where `u` is the source location, `v` is the destination location, and `w` is the travel time (in minutes) between these locations.
*   `time_windows`: A list of time windows, one for each location. Each time window is represented as a tuple `(start_time, end_time)` where `start_time` and `end_time` are in minutes from the start of the day (minute 0). Drones can only start a delivery at a location within its time window.
*   `start_locations`: A list of starting locations for the drones. Multiple drones can start from the same location.
*   `target_location`: The target delivery location.

The goal is to find the **earliest** possible time at which a drone can arrive at the `target_location` and start its delivery, considering the travel times and time window constraints. A drone can wait at a location until the start of its time window.

**Constraints:**

*   The graph may not be fully connected. There might be locations that are unreachable from the `start_locations`.
*   Travel times are non-negative integers.
*   Time windows are non-overlapping, and `end_time` is always greater than `start_time`.
*   If no path exists to the `target_location` within the given time constraints, return -1.
*   Minimize the time complexity of your solution. Aim for an efficient algorithmic approach.
*   The number of locations `N` can be up to 1000. The number of edges can be up to 5000. Time values can be up to 1440 (24 hours). The number of start locations can be up to 100.
*   You need to handle cases where a drone arrives at a location before the `start_time` of the time window; in such cases, the drone must wait. However, a drone cannot arrive after `end_time` of the time window.
*   If there are multiple shortest paths in terms of time, you need to pick the path that allows the drone to start the delivery at the target location at the earliest possible time.

**Input Format:**

```cpp
int N; // Number of locations
vector<tuple<int, int, int>> edges; // (u, v, w) representing a directed edge from u to v with weight w
vector<pair<int, int>> time_windows; // (start_time, end_time) for each location
vector<int> start_locations; // List of starting locations
int target_location; // Target delivery location
```

**Output Format:**

```cpp
int earliest_arrival_time; // The earliest possible arrival time at the target location, or -1 if unreachable.
```

**Example:**

```cpp
N = 4;
edges = {{0, 1, 10}, {0, 2, 15}, {1, 3, 12}, {2, 3, 8}};
time_windows = {{0, 30}, {20, 50}, {10, 40}, {0, 100}};
start_locations = {0};
target_location = 3;

// One possible path is 0 -> 2 -> 3.
// - Drone starts at location 0 at time 0.
// - Arrives at location 2 at time 15.
// - Waits at location 2 until time 15 (within window [10, 40]).
// - Arrives at location 3 at time 15 + 8 = 23.
// - Starts delivery at location 3 at time 23 (within window [0, 100]).

// Another possible path is 0 -> 1 -> 3.
// - Drone starts at location 0 at time 0.
// - Arrives at location 1 at time 10.
// - Waits at location 1 until time 20 (within window [20, 50]).
// - Arrives at location 3 at time 20 + 12 = 32.
// - Starts delivery at location 3 at time 32 (within window [0, 100]).

// The earliest arrival time is 23.
earliest_arrival_time = 23;
```
