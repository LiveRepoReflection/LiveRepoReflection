## Project Name

`NetworkSimulation`

## Question Description

You are tasked with simulating a complex network of interconnected servers, each with varying capacities, processing speeds, and security levels. The network is represented as a directed graph, where each node represents a server and each directed edge represents a network connection between two servers.  Each server can be processing multiple tasks at once, and tasks can be routed through the network to be processed by different servers.

**Data Model:**

*   **Server:** Each server has the following properties:
    *   `id`: A unique string identifier for the server.
    *   `processingCapacity`: An integer representing the maximum number of tasks that the server can concurrently process.
    *   `processingSpeed`: An integer representing the number of processing units it can perform per time unit.
    *   `securityLevel`: An integer representing the security level of the server (higher is more secure).
    *   `tasks`: A list of `Task` objects currently being processed.
*   **Task:** Each task has the following properties:
    *   `id`: A unique string identifier for the task.
    *   `size`: An integer representing the amount of processing units required to complete the task.
    *   `securityRequirement`: An integer representing the minimum security level required to process this task.
    *   `priority`: An integer representing the priority of the task (higher is more important).
    *   `sourceServerId`: The id of the server that created the task.
    *   `destinationServerId`: The id of the server that the task needs to be delivered to once complete.

*   **Network Connection:** Each directed edge in the graph has a `latency` (an integer representing the time units it takes for data to travel between the two connected servers).

**Simulation Requirements:**

1.  **Task Routing:** Implement a routing algorithm that efficiently routes tasks through the network. The algorithm should consider the following factors:
    *   Minimize latency: Choose paths with the lowest total latency.
    *   Security compliance: Ensure that tasks are only routed through servers that meet or exceed their `securityRequirement`.
    *   Load balancing: Distribute tasks across available servers to avoid overloading any single server.
    *   Prioritization: Higher priority tasks should be given preferential treatment in routing and processing.

2.  **Task Processing:** Simulate the processing of tasks on each server.
    *   Servers process tasks concurrently up to their `processingCapacity`.
    *   The time it takes to process a task depends on the task's `size` and the server's `processingSpeed`.
    *   Implement a scheduling algorithm that determines the order in which tasks are processed on each server, considering task `priority`.
    *   Upon task completion, the task must be sent to its `destinationServerId` through the network. If the destination server is unreachable, the task should be marked as failed.

3.  **Network Monitoring:** Implement a mechanism to monitor the network's performance.
    *   Track the average latency of task completion.
    *   Identify overloaded servers (servers consistently operating at or near their `processingCapacity`).
    *   Detect security breaches (tasks routed through servers with insufficient `securityLevel`).
    *   Track the number of tasks that failed due to unreachable destination server.

4.  **Dynamic Network Changes:** The network topology can change dynamically. Implement a mechanism to handle the following events:
    *   **Server Failure:** A server may become unavailable (remove the node from the graph). Tasks currently being processed on the failed server must be rerouted to other suitable servers.
    *   **Server Recovery:** A failed server may recover and become available again (add the node back to the graph).
    *   **Connection Failure:** A network connection (edge) may fail, increasing the latency, or be completely severed (remove the edge from the graph).  Tasks en route through the failed connection must be rerouted.
    *   **Connection Recovery:** A failed network connection (edge) may recover, returning the latency to its original value, or reconnecting a severed connection (add the edge back to the graph).

5.  **Optimization:**
    *   The simulation should be able to handle a large number of servers and tasks efficiently. Pay close attention to algorithmic complexity and data structure choices.
    *   Minimize the overall task completion time.

**Input:**

*   A description of the network topology (servers and connections) in a suitable data format (e.g., JSON, XML).
*   A stream of incoming tasks with their properties.
*   A stream of network events (server failures, server recoveries, connection failures, connection recoveries) with their timestamps.

**Output:**

*   The simulation should output the following information at regular intervals:
    *   The average task completion latency.
    *   A list of overloaded servers.
    *   A list of security breaches (if any).
    *   The number of tasks that failed due to unreachable destination server.

**Constraints:**

*   The number of servers in the network can be up to 10,000.
*   The number of tasks in the system at any given time can be up to 1,000,000.
*   The simulation should run in real-time or near real-time.
*   The solution must be thread-safe.

**Bonus:**

*   Implement a self-healing mechanism that automatically adjusts task routing to optimize network performance in response to dynamic network changes.
*   Implement a security auditing system that proactively identifies potential vulnerabilities in the network.

This problem requires a strong understanding of graph algorithms, data structures, concurrency, and system design principles.  It challenges the solver to design an efficient and robust simulation that can handle a complex and dynamic network environment. Different valid approaches are available with different performance tradeoffs.
