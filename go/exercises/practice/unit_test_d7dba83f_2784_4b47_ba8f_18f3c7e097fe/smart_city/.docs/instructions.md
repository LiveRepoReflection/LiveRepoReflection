## Question: Interconnected Smart City Simulation

### Question Description

You are tasked with building a simulation core for a futuristic, interconnected smart city. The city consists of `N` buildings and `M` bidirectional communication channels. Each building houses various sensors and actuators that generate and consume data. The communication channels have varying bandwidth capacities and latencies, forming a complex network.

The city's central AI needs to optimize data flow to ensure critical services operate smoothly under varying conditions. The critical service is called "Smart Emergency Response System (SERS)", which relies on data streamed from buildings to the Central AI to respond to emergencies.

Each building can generate different types of data, which are defined with a data type and a criticality score. `criticality_score` is an integer between `1` and `10` (inclusive), where `10` is the most critical and `1` is the least critical. Higher the criticality score, the higher the impact on the SERS performance.

Your task is to implement a system that efficiently routes data from source buildings to the Central AI, maximizing the total criticality score of the delivered data within the network's bandwidth and latency constraints.

**Specific Requirements:**

1.  **Data Prioritization:** The system should prioritize data with higher criticality scores, ensuring that the most important information reaches the Central AI, within the bandwidth and latency limitations.

2.  **Dynamic Bandwidth Allocation:** The system must dynamically allocate bandwidth across different communication channels, taking into account their capacities and latencies.  If a communication channel's bandwidth is exhausted, lower criticality data should be dropped to accommodate higher criticality data.

3.  **Latency Constraints:** Each type of data has a maximum allowed latency.  Data exceeding this latency is considered invalid and should not be included in the total criticality score calculation. Latency is defined as the sum of latencies of the channels that data traverse from the source building to the Central AI.

4.  **Fault Tolerance:** The system should gracefully handle scenarios where communication channels fail (bandwidth becomes 0). In case of a communication channel failure, the system should reroute data through alternative paths, if available, to maintain service continuity, considering bandwidth and latency constraints.

5.  **Optimization Objective:** Maximize the total criticality score of the data successfully delivered to the Central AI within the given bandwidth and latency constraints.

6.  **Central AI:** The Central AI is always located at building with ID `0`.

**Input:**

*   `N`: The number of buildings in the city (buildings are numbered from 0 to N-1).
*   `M`: The number of communication channels.
*   `channels`: A list of tuples, where each tuple represents a communication channel in the format `(source_building_id, destination_building_id, bandwidth_capacity, latency)`. `bandwidth_capacity` and `latency` are integers.
*   `data_sources`: A list of tuples, where each tuple represents a data source in the format `(building_id, data_type, criticality_score, max_latency, data_size)`. `building_id` is the ID of the building generating the data. `data_type` is a string representing the type of data.  `criticality_score`, `max_latency`, and `data_size` are integers.
*   `simulation_time`: An integer representing the duration of the simulation in discrete time steps. Bandwidth consumption and data transmission are considered instantaneous within each time step.

**Output:**

An integer representing the maximum total criticality score of the data successfully delivered to the Central AI over the entire `simulation_time`.

**Constraints:**

*   `1 <= N <= 100`
*   `1 <= M <= 500`
*   `1 <= bandwidth_capacity <= 100`
*   `1 <= latency <= 10`
*   `1 <= criticality_score <= 10`
*   `1 <= max_latency <= 50`
*   `1 <= data_size <= 50`
*   `1 <= simulation_time <= 100`
*   Multiple data sources can originate from the same building.
*   The network is guaranteed to be connected.

**Example:**

Let's say we have a simplified city with 3 buildings, 2 channels, and a single data source.

```
N = 3
M = 2
channels = [(1, 0, 20, 5), (2, 1, 15, 3)]
data_sources = [(2, "SensorData", 8, 10, 5)]
simulation_time = 1
```

Here, building 2 generates "SensorData" with a criticality score of 8. The data must reach the Central AI (building 0) within a latency of 10.

The path from building 2 to building 0 is 2 -> 1 -> 0, with a total bandwidth of min(15, 20) = 15 and a total latency of 3 + 5 = 8.

Since the data size is 5 and the bandwidth is 15, the data can be transmitted. The latency is 8, which is less than the max_latency of 10. Therefore, the data is successfully delivered.

The output in this case would be `8 * 1 = 8` (criticality score * simulation time).

**Challenge:**

The main challenge lies in efficiently exploring the possible data routing paths, prioritizing data flows based on criticality, managing bandwidth allocation, and respecting latency constraints, all while simulating channel failures, to maximize the overall criticality score within the given time limit. The solver needs to consider multiple valid solutions and their tradeoffs between the highest criticality and the lowest latency to ensure the most efficient path is chosen.
