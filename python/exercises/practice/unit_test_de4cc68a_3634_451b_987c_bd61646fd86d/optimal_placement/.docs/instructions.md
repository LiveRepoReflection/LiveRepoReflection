## Question: Optimal File Placement on a Distributed File System

### Question Description

You are designing a distributed file system (DFS) for a large-scale data analytics platform. The DFS consists of `N` storage nodes, each with a limited storage capacity. You are given a set of `M` files that need to be stored across these nodes.

Each file has a size and a popularity score. The popularity score represents the frequency with which the file is accessed. Your goal is to determine an *optimal* placement of files onto the storage nodes to minimize the overall data retrieval latency.

**Data Retrieval Latency:**  The retrieval latency for a file is proportional to the distance between the node where the client requests the file and the node where the file is stored. Assume each node is placed on a 2D grid. The distance between two nodes is calculated using the Manhattan distance (sum of absolute differences of their x and y coordinates).

**Constraints:**

1.  **Capacity Constraint:** The total size of files stored on any given node cannot exceed the node's storage capacity.
2.  **Replication Constraint:** Each file must be stored on exactly `R` nodes, where `R` is a replication factor provided as input.  This ensures redundancy and fault tolerance.
3.  **Node Location:** Each storage node is located at a unique (x, y) coordinate on a 2D grid.
4.  **Client Location:** For simplicity, assume that all clients are located at a single, known coordinate (x_c, y_c). The latency of retrieving a file is the average Manhattan distance between the client and each replica of the file.
5. **File Size:** File size is represented in a single unit.
6. **Node Capacity**: Node capacity is represented in the same unit as file size.

**Input:**

*   `N`: The number of storage nodes.
*   `M`: The number of files.
*   `R`: The replication factor (1 <= R <= N).
*   `node_capacities`: A list of `N` integers representing the storage capacity of each node.
*   `node_locations`: A list of `N` tuples, where each tuple `(x, y)` represents the coordinates of a storage node.
*   `file_sizes`: A list of `M` integers representing the size of each file.
*   `file_popularities`: A list of `M` integers representing the popularity score of each file. Higher value means more popular.
*   `client_location`: A tuple `(x_c, y_c)` representing the coordinates of the client.

**Output:**

A list of `M` lists. Each inner list contains `R` integers, representing the indices of the nodes where the corresponding file is stored.  The indices should be 0-based (i.e., the first node has index 0, the second node has index 1, and so on).

**Objective Function:**

Minimize the total weighted latency, where the weight for each file is its popularity score. The total weighted latency is calculated as:

`Total Weighted Latency = sum (file_popularity[i] * average_distance(client_location, nodes_where_file_i_is_stored))`

where `average_distance` is the average Manhattan distance from the client location to each of the `R` nodes where the file is stored.

**Optimization Requirements:**

*   The solution should aim for a near-optimal placement.  A brute-force approach is not feasible for larger values of `N` and `M`.
*   Consider using heuristics, approximation algorithms, or metaheuristic optimization techniques (e.g., simulated annealing, genetic algorithms, etc.) to find a good solution within a reasonable time.
*   Prioritize placing popular files closer to the client.
*   Balance storage load across the nodes to avoid exceeding capacity constraints.

**Example:**

```python
N = 3  # Number of storage nodes
M = 2  # Number of files
R = 1  # Replication factor

node_capacities = [10, 10, 10]  # Capacities of the nodes
node_locations = [(0, 0), (1, 1), (2, 2)]  # Locations of the nodes
file_sizes = [5, 5]  # Sizes of the files
file_popularities = [100, 50]  # Popularities of the files
client_location = (0, 0)  # Location of the client

# Possible Output (one optimal solution):
# [[0], [1]]  # File 0 is on node 0, File 1 is on node 1.
```

**Grading Criteria:**

*   Correctness: The output must satisfy the capacity and replication constraints.
*   Optimality: The lower the total weighted latency, the better the solution.  Test cases will be designed to differentiate between good and poor file placements.
*   Efficiency: The solution should run within a reasonable time limit (e.g., a few minutes) for moderate values of `N` and `M`.
*   Code Quality: The code should be well-structured, readable, and maintainable.

This problem requires a combination of data structure knowledge (representing the file system), algorithmic thinking (designing an efficient placement strategy), and optimization techniques. Good luck!
