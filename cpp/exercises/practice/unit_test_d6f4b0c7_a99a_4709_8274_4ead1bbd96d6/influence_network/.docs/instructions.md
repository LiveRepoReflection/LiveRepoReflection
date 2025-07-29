## Project Name

**Scalable Social Graph with Influence Propagation**

## Question Description

You are tasked with designing and implementing a scalable system for representing and analyzing a social network. The system should efficiently handle a large number of users and their connections, and also be able to model and simulate the propagation of influence within the network.

**Core Requirements:**

1.  **Graph Representation:** Implement a graph data structure to represent the social network.  Each user in the network is a node, and connections (friendships, follows, etc.) between users are represented by directed edges. The system must be able to efficiently add new users, add new connections between users, and retrieve the neighbors (outgoing and incoming) of a given user.  The graph should be designed to handle a very large number of nodes (millions or billions) and edges, with potentially high degree nodes.

2.  **Influence Modeling:** Each user has an *influence score* (a non-negative floating-point number). When a user adopts a new idea or product (becomes "activated"), their influence can spread to their neighbors.  Implement a discrete-time influence propagation model.  At each time step, an inactive user becomes activated if the sum of the influence scores of their activated neighbors exceeds a certain *activation threshold* for that user.  Each user has a unique activation threshold.

3.  **Scalable Simulation:** Simulate the influence propagation process over a given number of time steps, starting with a given set of initially activated users.  The simulation must be scalable to large networks.

4.  **Query Processing:** Implement the following query: given a set of initially activated users and a number of time steps, determine the total number of users activated at the end of the simulation.

**Constraints and Considerations:**

*   **Memory Efficiency:**  The graph data structure should be as memory-efficient as possible, given the potentially massive size of the network.  Consider using techniques like adjacency lists or compressed sparse row (CSR) format. Bit fields can also be considered for node status tracking.
*   **Time Complexity:**  The `add_user`, `add_connection`, `get_neighbors`, and simulation steps should be optimized for performance. Aim for sublinear or amortized constant time where possible. The simulation runtime should be linear with respect to the total number of edges and the number of simulation steps.
*   **Concurrency:**  The simulation process should be parallelized to leverage multi-core processors. Implement appropriate synchronization mechanisms to ensure data consistency and avoid race conditions.  Consider using lock-free data structures where applicable to minimize contention.
*   **Large Datasets:** The system should be designed to handle graphs that are too large to fit entirely in memory. Consider strategies for partitioning the graph and processing it in chunks. Disk-based data structures (e.g., using memory-mapped files) might be necessary for the largest networks.
*   **Edge Cases:** Handle edge cases such as self-loops, duplicate edges, and non-existent users gracefully.
*   **Activation Threshold Distribution:** Assume that activation thresholds are uniformly distributed between 0.0 and 1.0.
*   **Influence Score Distribution:**  Assume that influence scores follow a power-law distribution.  Users with very high influence scores are relatively rare.
*   **Directed Graph:** The connections represent influences. If A influences B, there is a directed edge from A to B, not necessarily the other way around.

**Input Format:**

The input will consist of the following:

1.  **Number of Users (N):** An integer representing the number of users in the network. Users are identified by unique integer IDs from 0 to N-1.
2.  **List of Connections (Edges):** A list of pairs of integers (u, v), where u and v are user IDs, representing a directed connection from user u to user v (u influences v).
3.  **Initial Activated Users:** A list of user IDs that are initially activated.
4.  **Number of Time Steps (T):** An integer representing the number of time steps to simulate.

**Output Format:**

A single integer representing the total number of users activated after T time steps.

**Example:**

```
Input:
N = 5
Edges = [(0, 1), (0, 2), (1, 3), (2, 4)]
Initial Activated Users = [0]
T = 3

Output:
5
```

**Explanation:**

*   Initially, user 0 is activated.
*   Time step 1: Users 1 and 2 become activated (assuming their activation thresholds are low enough given user 0's influence).
*   Time step 2: Users 3 and 4 become activated.
*   Time step 3: No new users are activated.
*   Total activated users: 0, 1, 2, 3, 4. Count is 5.

**Grading Criteria:**

*   **Correctness:** The solution must produce the correct output for all valid inputs.
*   **Efficiency:** The solution must be able to handle large networks (millions of users and connections) within a reasonable time limit.
*   **Memory Usage:** The solution must use memory efficiently.
*   **Code Quality:** The code must be well-structured, readable, and maintainable.
*   **Parallelization:** The solution should effectively utilize multi-core processors to speed up the simulation.

This problem requires a strong understanding of graph data structures, algorithms, concurrency, and memory management. The challenge lies in designing a system that is both correct and scalable to extremely large datasets.
