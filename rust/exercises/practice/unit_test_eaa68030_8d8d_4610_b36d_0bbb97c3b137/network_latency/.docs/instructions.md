## Project Name

`Global-Network-Latency-Optimization`

## Question Description

You are tasked with optimizing network latency across a globally distributed system. The system consists of a set of servers located in different geographical regions. Each server has a unique ID (an integer) and a geographical location (latitude and longitude).

Data needs to be transferred between servers. The latency between any two servers is determined by two factors:

1.  **Geographical Distance:**  The great-circle distance between the servers' locations. You can assume the Earth is a perfect sphere with a radius of 6371 kilometers.  Implement the Haversine formula for distance calculation.

2.  **Network Congestion:** Each server has a congestion level, represented by an integer between 0 (no congestion) and 10 (maximum congestion). The network congestion increases the base latency calculated above between the two servers. The congestion penalty is calculated by taking the product of the two servers congestion level and multiply it by a constant factor of 10 milliseconds.

Your goal is to design an algorithm that, given a set of servers and a series of data transfer requests, minimizes the overall latency.  You need to implement a function that determines the optimal path for each data transfer request, considering both geographical distance and network congestion. Data transfer requests are processed in the given order sequentially.

Specifically, you are given:

*   `servers`: A `Vec<(usize, f64, f64, u8)>`, where each tuple represents a server with its ID, latitude, longitude, and congestion level, respectively.  Latitude and longitude are in degrees.
*   `requests`: A `Vec<(usize, usize, u32)>`, where each tuple represents a data transfer request from a source server (ID), to a destination server (ID), and the size of the data being transferred in bytes (which only affects the output total latency value).

Your task is to implement a function `optimize_network_latency` that takes the `servers` and `requests` as input and returns the total latency (in milliseconds) for all data transfer requests, considering the optimal path for each request.

**Constraints:**

*   The number of servers will be between 2 and 100.
*   The number of requests will be between 1 and 1000.
*   Server IDs are unique and within the range of `0..servers.len() - 1`
*   Congestion levels will be between 0 and 10 inclusive.
*   Data size will be between 1 and 1,000,000 bytes.
*   Latency must be calculated in milliseconds and rounded up to the nearest integer.

**Optimization Requirements:**

*   Your solution should minimize the total latency across all data transfer requests.
*   Consider that finding the absolute shortest path for each request might not be globally optimal due to network congestion changes after each request.
*   You must take into account that when data is transferred from one server to the other, congestion level of BOTH servers increase by 1, but cannot exceed 10.

**Algorithm Considerations:**

*   For each request, use Dijkstra's algorithm (or similar shortest path algorithm) to find the optimal path between the source and destination servers, considering both distance and congestion.
*   After each data transfer, update the congestion levels of the servers involved.

**Example:**

Let's say you have three servers:

*   Server 0: (0, 40.7128, -74.0060, 2) (New York)
*   Server 1: (1, 34.0522, -118.2437, 5) (Los Angeles)
*   Server 2: (2, 51.5074, 0.1278, 1) (London)

And one request:

*   Request: (0, 2, 10000) (Transfer 10000 bytes from New York to London)

Your algorithm should find the path from New York to London with the lowest latency, considering the distance and congestion.  After the transfer, the congestion levels of New York and London should be updated.

**Bonus:**

*   Consider using a heap-based priority queue for Dijkstra's algorithm to improve performance.
*   Experiment with different strategies for updating congestion levels (e.g., increasing congestion on intermediate nodes as well).
