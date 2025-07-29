## Project Name

`NetworkSim`

## Question Description

You are tasked with building a simplified network simulator to analyze the performance of a distributed system. The system consists of `N` nodes, each identified by a unique integer ID from 0 to `N-1`. Nodes communicate by sending messages to each other. The network has limited bandwidth, message processing capabilities and is prone to failures.

Your simulator should model the following:

1.  **Nodes:** Each node has a message queue (FIFO), processing capacity, and a failure probability.
2.  **Messages:** Each message has a source node ID, a destination node ID, a size (in bytes), and a creation timestamp.
3.  **Network:** The network has a total bandwidth capacity (in bytes per second) and a latency model.
4.  **Simulation Time:** The simulation progresses in discrete time steps (e.g., seconds).

**Specifically, you need to implement the following functionalities:**

*   **Initialization:** Create `N` nodes with specified processing capacities, failure probabilities, and a network with defined bandwidth and latency characteristics.
*   **Message Injection:** Allow injecting messages into the system at specific nodes and times.
*   **Message Processing:** At each time step, each node should:
    *   Process messages in its queue up to its processing capacity.  Processing a message consumes a node's processing capacity equal to the message size.
    *   Forward processed messages towards their destination.  Consider network bandwidth limitations and latency during message transmission.
*   **Node Failure:** At each time step, each node has a probability of failing. A failed node cannot process or forward messages. After a failure, a node recovers after a fixed downtime duration.
*   **Network Congestion:** If the total size of messages being transmitted through the network at a given time step exceeds the network's bandwidth, messages should be dropped randomly until the transmission volume is within the network capacity.
*   **Metrics Collection:** Track the end-to-end latency for each message (time from creation to arrival at destination).

**Input:**

*   `N`: The number of nodes in the network.
*   `nodeCapacities`: A slice of integers, where `nodeCapacities[i]` represents the message processing capacity (in bytes per second) of node `i`.
*   `failureProbabilities`: A slice of floats, where `failureProbabilities[i]` represents the probability of failure (between 0.0 and 1.0) of node `i` at each time step.
*   `downtime`: The number of simulation steps a node is unavailable after a failure.
*   `networkBandwidth`: The total network bandwidth capacity (in bytes per second).
*   `networkLatency`: The network latency (in seconds) for message transmission between any two nodes.
*   `messages`: A slice of message structs, each containing `source`, `destination`, `size`, and `creationTime`.
*   `simulationDuration`: The total duration of the simulation (in seconds).

**Output:**

A slice of floats representing the end-to-end latencies for all successfully delivered messages, or -1 if the message was dropped.

**Constraints:**

*   `1 <= N <= 1000`
*   `1 <= nodeCapacities[i] <= 10000`
*   `0.0 <= failureProbabilities[i] <= 1.0`
*   `1 <= downtime <= 10`
*   `1 <= networkBandwidth <= 100000`
*   `1 <= networkLatency <= 10`
*   `0 <= messages.length <= 10000`
*   `0 <= messages[i].source < N`
*   `0 <= messages[i].destination < N`
*   `1 <= messages[i].size <= 5000`
*   `0 <= messages[i].creationTime < simulationDuration`
*   `1 <= simulationDuration <= 1000`

**Optimization Requirements:**

*   Your solution should be optimized for performance. Inefficient algorithms will likely time out.
*   Consider using appropriate data structures to efficiently manage message queues, node states, and network traffic.

**Example:**

(This is a simplified example for understanding. Actual test cases will be more complex.)

```
N = 3
nodeCapacities = [100, 150, 200]
failureProbabilities = [0.1, 0.05, 0.0]
downtime = 2
networkBandwidth = 500
networkLatency = 1
messages = [
    {source: 0, destination: 2, size: 50, creationTime: 0},
    {source: 1, destination: 0, size: 75, creationTime: 1},
]
simulationDuration = 5

Output: (An example output, actual values will vary based on your simulation logic)
[2.0, 3.0] // End-to-end latencies of the two messages.
```

**Clarifications:**

*   Assume perfect message delivery if bandwidth is available and nodes are functioning.
*   Dropped messages are lost and do not contribute to latency calculations.
*   If a message reaches its destination after `simulationDuration`, it is considered dropped.
*   Node failures are independent events.
*   Nodes recover immediately at the end of their `downtime`.

This problem requires a combination of data structure knowledge (queues, potentially heaps), probabilistic reasoning, and efficient algorithm design to simulate the network behavior accurately within the given constraints. The optimization aspect will push contestants to think critically about their implementation choices. Good luck!
