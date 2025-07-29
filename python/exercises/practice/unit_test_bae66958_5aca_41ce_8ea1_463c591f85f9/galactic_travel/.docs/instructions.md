## Project Name

`IntergalacticTravelPlanner`

## Question Description

You are tasked with designing an intergalactic travel planner for a futuristic space tourism company. The company offers trips between various planets and space stations connected by wormholes. However, the properties of these wormholes are peculiar:

*   **Directed:** Each wormhole allows travel in only one direction.
*   **Time-Varying Travel Time:** The travel time through a wormhole depends on the departure time. A wormhole has a schedule specifying travel times for different departure time windows.
*   **Limited Capacity:** Each wormhole has a maximum number of travelers it can accommodate simultaneously.

Your goal is to write a function that finds the *earliest* arrival time at a destination planet, given a starting planet, a departure time window, a destination planet, the wormhole network, and the number of travelers.

**Input:**

*   `start_planet`: A string representing the starting planet (e.g., "Earth").
*   `departure_time_window`: A tuple `(earliest_departure_time, latest_departure_time)` representing the allowed departure time window from the starting planet (inclusive). Time is represented as an integer.
*   `destination_planet`: A string representing the destination planet (e.g., "Mars").
*   `num_travelers`: An integer representing the number of travelers.
*   `wormhole_network`: A dictionary representing the wormhole network. The keys are planet/station names (strings). The values are dictionaries where keys are destination planet/station names (strings), and the values are lists of wormhole schedules. Each schedule is a dictionary with the following keys:

    *   `capacity`: An integer representing the maximum capacity of the wormhole.
    *   `schedule`: A list of tuples `(start_time, end_time, travel_time)`. This means that if you depart from the origin at a time between `start_time` and `end_time` (inclusive), the travel time will be `travel_time`. This list is sorted by start time, is non-overlapping and covers all possible departure times.

**Output:**

*   Return the earliest possible arrival time at the `destination_planet` as an integer.
*   If no path exists or it's impossible to reach the destination within the given constraints, return `None`.

**Constraints:**

*   The number of planets and space stations will be less than or equal to 50.
*   The number of wormholes from each location will be less than or equal to 10.
*   The number of time windows in each wormhole's schedule will be less than or equal to 20.
*   `0 <= earliest_departure_time <= latest_departure_time <= 10000`.
*   `1 <= travel_time <= 1000`.
*   `1 <= capacity <= 1000`.
*   You must consider the capacity of each wormhole. If the wormhole is already at full capacity at your desired departure time, you cannot use that wormhole at that time.
*   Assume that waiting time at planets/stations is negligible.
*   Optimize for finding the *earliest* arrival time. A brute-force solution exploring all possible paths will likely time out.
* The wormhole network may contain cycles.

**Example:**

```python
wormhole_network = {
    "Earth": {
        "StationAlpha": [
            {"capacity": 10, "schedule": [(0, 100, 10)]},
            {"capacity": 5, "schedule": [(0, 50, 15), (51, 100, 20)]},
        ]
    },
    "StationAlpha": {
        "Mars": [
            {"capacity": 20, "schedule": [(0, 100, 30)]}
        ]
    },
    "Mars": {}
}

start_planet = "Earth"
departure_time_window = (0, 50)
destination_planet = "Mars"
num_travelers = 7

# Expected Output: 40 (Depart Earth at time 10 using the first wormhole to StationAlpha (travel time 10), arrive at StationAlpha at time 20. Depart StationAlpha immediately to Mars using the wormhole, arrive at Mars at time 50. Another possibility would be to depart from Earth at time 30 using the second wormhole (capacity 5) so you must use the first one.)
```

This problem requires careful consideration of graph traversal, dynamic programming (or a similar optimization technique), and efficient handling of time-varying constraints and capacity limitations. Good luck!
