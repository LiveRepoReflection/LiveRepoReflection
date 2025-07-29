## Problem: Decentralized Resource Allocation in a Dynamic Network

**Description:**

Imagine a decentralized network of computing nodes, each with varying processing power, memory, and storage capabilities. These nodes need to collaborate to process a stream of tasks arriving continuously. Each task requires a certain amount of processing power, memory, and storage to be completed. Nodes can dynamically join and leave the network, and their resource capacities can fluctuate due to internal processes.

Your task is to implement a distributed resource allocation system that efficiently assigns tasks to available nodes, maximizing overall network throughput while adhering to node resource constraints.

**Specific Requirements:**

1.  **Node Discovery and Registration:** Implement a mechanism for nodes to discover each other and register their resource capacities with the network. Assume a gossip-based protocol for node discovery and information dissemination. Nodes periodically broadcast their presence and resource information to a subset of their neighbors.

2.  **Task Submission:** Design a mechanism for submitting tasks to the network. Each task specifies its resource requirements (CPU, Memory, Storage) and a priority level.

3.  **Resource Allocation:** Implement a distributed resource allocation algorithm. The algorithm should consider the following:

    *   **Resource Constraints:** Tasks can only be assigned to nodes that have sufficient available resources.
    *   **Task Prioritization:** Higher-priority tasks should be allocated resources before lower-priority tasks. If you have multiple tasks of same priority, you can allocate based on first come first serve.
    *   **Load Balancing:** The algorithm should strive to distribute tasks evenly across the network to prevent overloading individual nodes.
    *   **Dynamic Node Availability:** The algorithm must adapt to nodes joining and leaving the network and fluctuations in node resource capacities. The task will be assigned to a new available node if the previous assigned node left the network during task processing.
    *   **Optimality:** While finding the absolute *optimal* solution may be computationally intractable in a decentralized setting, the algorithm should aim for a reasonably efficient allocation.

4.  **Task Execution and Monitoring:** Once a task is assigned to a node, implement a mechanism for the node to execute the task and report its status (e.g., "running", "completed", "failed").

5.  **Fault Tolerance:** Handle node failures gracefully. If a node fails while executing a task, the task should be automatically reassigned to another available node if possible.

**Constraints:**

*   **Decentralized Implementation:** The solution must be decentralized. No single node should have complete knowledge of the entire network state.
*   **Scalability:** The system should be able to handle a large number of nodes and tasks. Consider the impact of your design on network bandwidth and processing overhead.
*   **Concurrency:** Implement the system using Go's concurrency primitives (goroutines and channels) to maximize performance.
*   **Realism:** Use realistic resource units (e.g., CPU cores, GB of memory, GB of storage).
*   **Assume messages can be lost:** Implement a robust retry mechanism.

**Evaluation Criteria:**

*   **Correctness:** The system must correctly allocate tasks to nodes while respecting resource constraints.
*   **Efficiency:** The system should achieve high throughput and low task completion times.
*   **Scalability:** The system should be able to handle a large number of nodes and tasks without significant performance degradation.
*   **Fault Tolerance:** The system should be resilient to node failures.
*   **Code Quality:** The code should be well-structured, documented, and easy to understand.
*   **Adherence to Constraints:** The solution must adhere to the constraints outlined above (decentralization, scalability, concurrency).

This problem requires a strong understanding of distributed systems concepts, concurrency, data structures, and algorithms. It also encourages creative problem-solving to balance the trade-offs between optimality, scalability, and fault tolerance in a decentralized environment. Good luck!
