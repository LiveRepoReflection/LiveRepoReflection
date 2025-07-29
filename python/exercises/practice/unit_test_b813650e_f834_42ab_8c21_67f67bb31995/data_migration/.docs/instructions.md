## Problem: Optimizing Inter-Datacenter Data Migration

**Problem Description:**

You are tasked with designing an optimal strategy for migrating a massive dataset between geographically distributed datacenters. You have `N` datacenters, each containing a subset of the total dataset. The total dataset is conceptually divided into `M` data blocks. Each datacenter `i` holds a certain number of these blocks.

Migrating a data block from one datacenter to another incurs a cost that depends on the network bandwidth between the two datacenters and the size of the data block.  The cost of migrating a block `j` from datacenter `i` to datacenter `k` is given by `cost(i, k, j) = size(j) / bandwidth(i, k)`.

Your goal is to determine the optimal migration plan to consolidate *all* data blocks into a single designated target datacenter, datacenter `T`.  The "optimal" plan minimizes the *total cost* of migrating all data blocks to the target datacenter.

**Input:**

*   `N`: The number of datacenters (1 <= N <= 100). Datacenters are indexed from 0 to N-1.
*   `M`: The number of data blocks (1 <= M <= 1000). Data blocks are indexed from 0 to M-1.
*   `T`: The index of the target datacenter (0 <= T <= N-1).
*   `ownership[N][M]`: A boolean matrix representing the ownership of data blocks. `ownership[i][j] = True` if datacenter `i` owns data block `j`, and `False` otherwise.
*   `size[M]`: An array representing the size (in GB) of each data block (1 <= size[j] <= 100).
*   `bandwidth[N][N]`: A matrix representing the bandwidth (in Gbps) between each pair of datacenters.  `bandwidth[i][k]` represents the bandwidth from datacenter `i` to datacenter `k`.  `bandwidth[i][i] = 0` for all `i`. Assume the graph is complete and `bandwidth[i][k] > 0` for `i != k` (1 <= bandwidth[i][k] <= 100).  Bandwidth is not necessarily symmetric (`bandwidth[i][k]` may not equal `bandwidth[k][i]`).

**Output:**

A single floating-point number representing the *minimum total cost* (in seconds) to migrate all data blocks to the target datacenter. The answer should be accurate to within a relative or absolute error of 1e-6.

**Constraints and Requirements:**

1.  **Optimization:** Your solution must be highly efficient to handle the maximum input sizes (N=100, M=1000) within a reasonable time limit (e.g., a few seconds).
2.  **No Redundant Migrations:** Data blocks should only be migrated as necessary. Avoid unnecessary transfers.
3.  **Intermediate Storage:** Datacenters can act as temporary storage. A data block can be moved from datacenter A to datacenter B and then later moved from datacenter B to the target datacenter T. This means you don't necessarily need to move a block directly from its originating datacenter to the target.
4.  **Real-World Considerations:** Think about the problem in terms of a realistic scenario. Data transfers are costly, and intermediate transfers can sometimes be more efficient due to varying network bandwidths.
5.  **Edge Cases:** Consider cases such as:
    *   The target datacenter already owns some or all of the data blocks.
    *   The dataset is very small.
    *   The bandwidth between some datacenters is very low compared to others.
6.  **Algorithmic Complexity:** Aim for an algorithm with a time complexity better than O(N^2 * M^2). This might involve clever use of graph algorithms and data structures.
7.  **Python Specifics:** Ensure your solution leverages Python's built-in data structures and libraries effectively. Consider using libraries like `heapq` or `networkx` if they are appropriate.

**Example:**

Let's say you have 3 datacenters (N=3), 3 data blocks (M=3), and the target datacenter is datacenter 2 (T=2).

```
N = 3
M = 3
T = 2
ownership = [
    [True, False, False],  # Datacenter 0 owns block 0
    [False, True, False],  # Datacenter 1 owns block 1
    [False, False, True]   # Datacenter 2 owns block 2
]
size = [10, 20, 30]  # Size of blocks 0, 1, and 2 in GB
bandwidth = [
    [0, 5, 10],    # Bandwidth from 0 to 0, 0 to 1, 0 to 2 (in Gbps)
    [5, 0, 15],    # Bandwidth from 1 to 0, 1 to 1, 1 to 2
    [10, 15, 0]     # Bandwidth from 2 to 0, 2 to 1, 2 to 2
]
```

In this example, block 0 needs to be moved from datacenter 0 to datacenter 2, and block 1 needs to be moved from datacenter 1 to datacenter 2.  The optimal solution would calculate the cost of these direct transfers. However, a smarter solution might consider if moving block 0 from datacenter 0 to datacenter 1 first and then to datacenter 2 is cheaper.
