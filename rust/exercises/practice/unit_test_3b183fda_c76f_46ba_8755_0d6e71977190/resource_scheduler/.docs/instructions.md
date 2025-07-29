## The Multi-Resource Scheduling Problem

**Problem Description:**

You are tasked with designing an efficient resource allocation system for a data center. The data center manages a set of heterogeneous resources (CPU cores, memory, GPU units, and network bandwidth) and needs to schedule incoming jobs to these resources. Each job has specific resource requirements and a deadline.

Your system needs to minimize the number of rejected jobs and maximize the overall resource utilization.

**Input:**

The input consists of two main parts: resource descriptions and job requests.

1.  **Resource Descriptions:** A list of available resources in the data center. Each resource is represented by its type (CPU, Memory, GPU, Network) and its capacity. The resources are described as follows:
    *   `resource_capacities: Vec<(ResourceType, u64)>`

        Where `ResourceType` is an enum:

        ```rust
        enum ResourceType {
            CPU,
            Memory,
            GPU,
            Network,
        }
        ```

        And `u64` representing the resource capacity. For example: `[(CPU, 128), (Memory, 256000), (GPU, 8), (Network, 10000)]`. This represents 128 CPU cores, 256000 MB of memory, 8 GPU units, and 10000 Mbps of network bandwidth.

2.  **Job Requests:** A list of job requests that need to be scheduled. Each job is represented by its resource requirements, deadline, and a unique ID. The jobs are described as follows:

    *   `job_requests: Vec<(u32, Vec<(ResourceType, u64)>, u64)>`

        Where:
        *   `u32` is the unique job ID.
        *   `Vec<(ResourceType, u64)>` is a list of resource requirements for the job, similar to the `resource_capacities` format.
        *   `u64` is the deadline for the job (represented as a timestamp).

**Output:**

Your function should return a `Vec<u32>` containing the IDs of the jobs that were successfully scheduled. Jobs should be scheduled in the order they appear in the input `job_requests` vector.

**Constraints:**

1.  **Resource Limits:** The total resource requirements of all scheduled jobs for a given resource type must not exceed the capacity of that resource type.
2.  **Deadline:** A job can only be scheduled if it can start immediately (at the current time, assumed to be 0) and complete before its deadline.  Assume each job takes a fixed "execution time" of 1 time unit. Thus, a job with deadline `d` can be scheduled only if `1 <= d`.
3.  **Optimization:** The goal is to schedule as many jobs as possible, prioritizing higher resource utilization.
4.  **Real-time Scheduling:** The scheduling decision for each job must be made sequentially, considering the current state of resource allocation. You cannot "look ahead" at future job requests.
5.  **Heterogeneous Resources:** The scheduler must handle different types of resources and ensure that all resource requirements of a job are met before scheduling it.

**Example:**

```rust
use ResourceType::*;

let resource_capacities = vec![(CPU, 4), (Memory, 8)];
let job_requests = vec![
    (1, vec![(CPU, 1), (Memory, 2)], 2),  // Job 1: 1 CPU, 2 Memory, Deadline 2
    (2, vec![(CPU, 2), (Memory, 3)], 3),  // Job 2: 2 CPU, 3 Memory, Deadline 3
    (3, vec![(CPU, 2), (Memory, 4)], 4),  // Job 3: 2 CPU, 4 Memory, Deadline 4
];

// Expected Output (one possible solution)
// vec![1, 2]

```

**Considerations:**

*   The number of resources and jobs can be significant (up to 10000).
*   The resource capacities and job requirements can vary widely.
*   The scheduling algorithm should be efficient in terms of time complexity.  Naive solutions will likely time out. Consider using appropriate data structures to track resource availability.
*   Multiple valid solutions may exist. The grading system will evaluate based on the number of scheduled jobs and overall resource utilization.

**Challenge:**

Implement an efficient and robust resource scheduling algorithm that maximizes job scheduling while respecting resource constraints and deadlines. Consider using appropriate data structures and algorithms to optimize performance.
