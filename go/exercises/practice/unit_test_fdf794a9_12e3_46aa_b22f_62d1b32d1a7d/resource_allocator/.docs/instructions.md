## Project Name

`ResourceAllocator`

## Question Description

You are tasked with designing a resource allocation system for a distributed computing cluster. The cluster consists of `N` nodes, each with varying amounts of CPU cores, memory, and disk space. Jobs are submitted to the cluster, each requiring a specific amount of CPU cores, memory, and disk space.

The goal is to allocate jobs to nodes in the cluster such that the following objectives are met:

1.  **Resource Constraints:** A node cannot be allocated more resources (CPU cores, memory, disk space) than it possesses.
2.  **Minimize Fragmentation:** Reduce the overall fragmentation of resources across the cluster.  Fragmentation occurs when available resources on individual nodes are not sufficient to satisfy the resource requirements of waiting jobs.
3.  **Priority Scheduling:** Jobs have priorities (integer values, higher is better). Higher-priority jobs should be allocated resources before lower-priority jobs.  If multiple nodes can satisfy a job's requirements, prioritize the node with the least remaining resources *after* allocation, to promote resource balancing.
4.  **Node Affinity (Optional):** Some jobs may have an affinity for specific nodes (identified by node ID). If possible, allocate the job to one of its preferred nodes, as long as it doesn't significantly violate other objectives. If no preferred nodes can fulfill the needs, allocate to the node that best satisfies the other objectives.

Your system must handle the following operations:

*   **SubmitJob(jobID string, priority int, cpu int, memory int, disk int, preferredNodes []string):** Submits a new job to the system with the specified resource requirements, priority, and optional preferred nodes.
*   **AllocateResources():** Attempts to allocate resources to waiting jobs based on their priority and the available resources on the nodes. This function should return a map of jobID to nodeID indicating which jobs were assigned to which nodes. Jobs that could not be allocated should not appear in the returned map.
*   **ReleaseResources(jobID string):** Releases the resources allocated to a specific job, making them available for other jobs.
*   **GetNodeStatus(nodeID string):** Returns the current resource utilization of a specific node (CPU cores, memory, disk space used and total).

**Constraints and Requirements:**

*   The number of nodes (`N`) can be up to 1000.
*   The number of jobs can be up to 10,000.
*   CPU cores, memory, and disk space are all integers.
*   Priorities are integers.
*   The `AllocateResources()` function must be reasonably efficient. Naive brute-force approaches will likely time out. Consider the tradeoffs between allocation speed and optimal resource utilization.
*   Handle edge cases gracefully, such as invalid job IDs, node IDs, or resource requests.
*   The system must be thread-safe, as multiple operations may be performed concurrently.

**Clarifications:**

*   A job can only be allocated to one node.
*   Once a job is allocated to a node, it remains on that node until its resources are explicitly released.
*   If a job cannot be allocated due to insufficient resources or other constraints, it remains in a waiting queue until resources become available.
*   If a job requests more resources than any single node possesses, it should be rejected and an error returned on submission.

**Bonus:**

*   Implement a preemption mechanism, where lower-priority jobs can be preempted (resources released) to accommodate higher-priority jobs.  This significantly complicates the problem.
*   Implement a more sophisticated fragmentation metric than simple "number of nodes with insufficient resources for any waiting job." Consider weighted fragmentation based on the size of the remaining resources and the size of waiting jobs.

This problem requires a good understanding of data structures (maps, queues, potentially heaps or trees), algorithms (resource allocation strategies), and system design principles (concurrency, error handling, optimization).  There are multiple valid approaches, each with different trade-offs in terms of performance, resource utilization, and complexity.
