## Question: Optimal Train Routing

**Problem Description:**

You are tasked with designing an optimal train routing system for a large, complex railway network. The network consists of `N` stations, numbered from `0` to `N-1`, and `M` bidirectional tracks connecting these stations. Each track has a specific *capacity* representing the maximum number of trains that can traverse it simultaneously and a *transit time* representing the time it takes for a train to travel from one station to another along the track.

Given a set of `K` trains, each with a designated *origin station*, a *destination station*, and a *departure time*, your goal is to find the optimal route for each train to minimize the overall *weighted average arrival time* across all trains.

**Input:**

*   `N`: The number of stations (1 <= N <= 1000).
*   `M`: The number of tracks (1 <= M <= 5000).
*   A list of `M` tuples, each representing a track: `(station1, station2, capacity, transit_time)`. `station1` and `station2` are integers representing the stations connected by the track. `capacity` is a positive integer (1 <= capacity <= 100), and `transit_time` is a positive integer (1 <= transit_time <= 100).
*   `K`: The number of trains (1 <= K <= 500).
*   A list of `K` tuples, each representing a train: `(origin_station, destination_station, departure_time, weight)`. `origin_station` and `destination_station` are integers representing the origin and destination stations for the train. `departure_time` is a non-negative integer representing the time the train departs from the origin station. `weight` is a positive integer (1 <= weight <= 1000).

**Output:**

A list of `K` lists, where each inner list represents the optimal route for the corresponding train. Each route should be a list of station numbers, starting with the origin station and ending with the destination station. If no route exists for a train, return an empty list for that train.

**Constraints and Optimization Requirements:**

1.  **Capacity Constraints:** At any given time, the number of trains traversing a track cannot exceed its capacity. If a train's arrival at a track would violate this constraint, the train must wait at the preceding station until the track has sufficient capacity. Waiting time should also be accounted for when calculating arrival times.

2.  **Optimal Routing:** The routes you choose must minimize the overall weighted average arrival time of all trains. The weighted average arrival time is calculated as:

    ```
    (sum of (arrival_time_i * weight_i) for all trains i) / (sum of weight_i for all trains i)
    ```

3.  **Time Complexity:** The algorithm must be efficient enough to handle reasonably large networks and train schedules within a given time limit (e.g., a few seconds).

4.  **Tie-Breaking:** If multiple routes result in the same minimal weighted average arrival time, any of those routes is considered a valid solution.

5.  **Realistic Scenario:** The railway network can have cycles, multiple tracks between stations (parallel tracks with different capacities/transit times), and isolated stations.

6.  **Dynamic Track Availability:** After a train passes a track, the track's capacity is immediately available for other trains to use.

7.  **No Train Overtaking:** Trains cannot overtake each other on the same track. They must maintain their relative order of entry onto the track.
