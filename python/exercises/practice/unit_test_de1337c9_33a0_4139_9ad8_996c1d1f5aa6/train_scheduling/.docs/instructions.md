## Problem Title: Optimal Train Route Scheduling

### Question Description

You are developing a system for optimizing train schedules across a vast railway network. The network consists of `n` stations, numbered from 0 to `n-1`. Trains travel between stations along tracks. Each track connects two stations and has a specific travel time and a maximum capacity.

Your task is to design an algorithm that can efficiently answer queries about the fastest route between two stations, considering the capacity constraints of the tracks. Furthermore, the railway company wants to maximize the total number of passengers that can be transported between a given pair of stations within a specified time window, given the capacity constraints.

Specifically, you need to implement a system that supports the following operations:

1.  **`add_track(station1, station2, travel_time, capacity)`:** Adds a bidirectional track between `station1` and `station2` with the specified `travel_time` (in minutes) and `capacity` (number of passengers).  If the track already exists, update `travel_time` and `capacity` with the new values.

2.  **`shortest_time(start_station, end_station)`:** Returns the shortest travel time (in minutes) between `start_station` and `end_station`. If no route exists, return -1.

3.  **`max_passengers(start_station, end_station, time_window)`:** Returns the maximum number of passengers that can be transported from `start_station` to `end_station` within the specified `time_window` (in minutes). Trains can depart at any time `t` such that `0 <= t <= time_window - shortest_time(start_station, end_station)`.  Assume that once a train starts, it travels without stopping. If no route exists or the time window is smaller than the shortest possible travel time, return 0.

**Constraints:**

*   `1 <= n <= 10^4` (Number of stations)
*   `0 <= station1, station2 < n`
*   `1 <= travel_time <= 10^3`
*   `1 <= capacity <= 10^3`
*   `1 <= time_window <= 10^4`
*   The graph might not be fully connected.
*   There may be multiple routes between any two stations.
*   You should optimize for both time and space complexity, especially for the `max_passengers` operation, as it will be called frequently with different `time_window` values.

**Considerations:**

*   Think about which data structures are best suited for representing the railway network and for efficiently performing the required operations.
*   Consider different algorithmic approaches for finding the shortest path and the maximum number of passengers within the time window.
*   Pay attention to potential bottlenecks and optimize your code accordingly.  Can you precompute any information to speed up the queries?
*   Think about how to handle edge cases such as disconnected stations or invalid inputs.
*   For `max_passengers`, you don't need to find the exact number of trains; you need to find the maximum number of passengers that *could* be transported, assuming optimal scheduling.
