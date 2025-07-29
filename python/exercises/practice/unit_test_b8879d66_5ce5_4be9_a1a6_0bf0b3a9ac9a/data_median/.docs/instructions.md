Okay, I'm ready to design a challenging programming competition problem. Here it is:

### Project Name

```
distributed-data-aggregation
```

### Question Description

You are designing a distributed system for real-time data aggregation.  Imagine a network of sensors continuously generating numerical data. Your task is to implement a mechanism to efficiently calculate the median of all sensor readings across the entire network at any given point in time.

The system consists of the following:

*   **Sensor Nodes:** A large number of sensor nodes, each producing a stream of numerical data (integers) at varying rates. The values are not necessarily unique.
*   **Aggregation Servers:** A smaller number of aggregation servers that collect data from the sensor nodes. Each sensor node is assigned to a specific aggregation server. The assignment is fixed.
*   **Central Server:** A single central server responsible for computing the global median based on the aggregated data received from the aggregation servers.

Your goal is to implement a system that efficiently calculates the running median of all sensor data, subject to the following constraints:

1.  **Real-Time Requirements:** The system must provide a reasonably up-to-date estimate of the median with minimal latency.  The central server needs to be able to return a median value at any time.
2.  **Limited Bandwidth:**  Communication between sensor nodes and aggregation servers, and between aggregation servers and the central server, is bandwidth-constrained.  Minimize the amount of data transmitted.
3.  **Scalability:** The system must be able to handle a large number of sensor nodes and aggregation servers.
4.  **Fault Tolerance:** The system should be reasonably resilient to the failure of individual sensor nodes.  The median calculation should still be accurate, even with some missing data.
5.  **Data Distribution:** The data distribution across sensors can be anything.
6.  **Memory Constraints:** Both Aggregation Servers and the Central Server have limited memory.

**Input:**

You will be provided with the following information:

*   `num_sensors`: The total number of sensor nodes in the system.
*   `num_aggregation_servers`: The number of aggregation servers.
*   `sensor_server_mapping`: A list (or dictionary) that maps each sensor node to its assigned aggregation server (0-indexed).  e.g., `sensor_server_mapping[i]` gives the ID of the aggregation server for sensor `i`.
*   A continuous stream of data from each sensor node.  You'll need to simulate this data stream in your testing.

**Output:**

Your code should implement a function that, when called by the central server, returns the current estimate of the global median of all sensor readings.

**Specific Requirements:**

*   Implement the data structures and algorithms used by the sensor nodes, aggregation servers, and central server.
*   Focus on minimizing the communication overhead between the different components.
*   Consider the trade-offs between accuracy, latency, and bandwidth usage.
*   Your solution should be efficient enough to handle a large dataset.
*   You can use any appropriate data structures and algorithms, but you must justify your choices in comments.
*   You may use external libraries for basic data structures (e.g., heaps, sorted lists), but you should avoid libraries that directly compute the median. You are expected to implement the distribution and aggregation strategies.
*   The median should be calculated to a reasonable degree of precision. An exact median is not required, especially given the real-time and bandwidth constraints.

**Judging Criteria:**

*   **Correctness:** The accuracy of the calculated median.
*   **Efficiency:** The communication overhead (amount of data transmitted).
*   **Scalability:** How well the solution scales with the number of sensors and aggregation servers.
*   **Latency:** The time it takes to calculate and return the median.
*   **Code Quality:** Clarity, organization, and documentation of the code.
*   **Justification:** Explanation of the design choices and trade-offs made.

This problem requires a good understanding of distributed systems, data structures, algorithms, and optimization techniques. Good luck!
