## Problem: Optimal Resource Allocation in a Distributed System

**Description:**

You are designing a resource allocation system for a large-scale distributed computing environment. The system consists of `N` computing nodes and `M` distinct types of resources (e.g., CPU cores, memory, GPU, specialized hardware accelerators). Each node possesses a certain quantity of each resource type.  A user submits a job request that requires specific amounts of each resource type to be allocated simultaneously on a *subset* of nodes.  The job can be executed only if all required resources are available on the selected nodes. A node can only be a part of a single subset allocated to a job.

Your task is to design an algorithm to find the *minimum* number of nodes required to satisfy a given job request, or determine that the request cannot be satisfied.

**Input:**

*   `N`: The number of computing nodes (1 <= N <= 1000).
*   `M`: The number of resource types (1 <= M <= 10).
*   `node_resources`: A list of lists, where `node_resources[i][j]` represents the amount of resource type `j` available on node `i`.  (0 <= `node_resources[i][j]` <= 1000).
*   `job_request`: A list representing the resource requirements for the job. `job_request[j]` is the amount of resource type `j` required by the job. (0 <= `job_request[j]` <= 1000).

**Output:**

An integer representing the minimum number of nodes required to satisfy the job request. If the job request cannot be satisfied, return -1.

**Constraints and Edge Cases:**

*   **Resource Exhaustion:**  The sum of a resource type across *all* nodes might still be insufficient to fulfill the `job_request`.
*   **Node Co-location:**  All resource types specified in `job_request` must be available on the *same set* of nodes.  A job cannot use, for example, CPU from node 1 and GPU from node 2.
*   **Optimal Solution:** You need to find the *minimum* number of nodes. A solution that uses more nodes than necessary will be considered incorrect.
*   **Empty Request:** If `job_request` is all zeros, return 0 (no nodes needed).
*   **Large Numbers**: While individual resource values are capped at 1000, the sum of resources across multiple nodes might be large.
*   **Time Complexity:** Aim for a solution with a time complexity significantly better than brute-force (e.g., trying all possible node combinations). A brute force solution will likely time out for larger datasets.
*   **Space Complexity:** Limit your memory usage to avoid exceeding memory limits.

**Example:**

```python
N = 3
M = 2
node_resources = [[5, 3], [2, 4], [3, 1]]
job_request = [7, 5]

# Expected output: 2
# Nodes 0 and 1 can satisfy the request (5+2 >= 7 and 3+4 >= 5)

N = 3
M = 2
node_resources = [[5, 3], [2, 4], [3, 1]]
job_request = [11, 5]

# Expected output: -1
# Not enough total CPU (5+2+3 = 10 < 11)

N = 2
M = 2
node_resources = [[1, 1], [1,1]]
job_request = [2, 2]

#Expected output: 2
```
Good luck!
