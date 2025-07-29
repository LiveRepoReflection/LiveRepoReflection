Okay, here is a challenging Rust coding problem designed to be difficult and require careful consideration of efficiency and edge cases.

**Project Name:** NetworkFlowScheduler

**Question Description:**

You are tasked with designing a network flow scheduler for a data center. The data center consists of `N` servers, each with a limited processing capacity.  There are `M` data flows that need to be scheduled across these servers. Each data flow `i` is characterized by:

*   `source_server_id`: The ID of the server where the data flow originates (0-indexed).
*   `destination_server_id`: The ID of the server where the data flow needs to be processed (0-indexed).  The source and destination servers are *always different*.
*   `data_volume`:  The amount of data (in arbitrary units) that needs to be processed for this flow.
*   `priority`: An integer representing the priority of this flow. Higher values indicate higher priority.

Each server `j` has a `processing_capacity`, representing the maximum amount of data it can process.

The goal is to implement a scheduler that maximizes the *total weighted throughput* of the scheduled data flows. The weighted throughput of a data flow is its `data_volume` multiplied by its `priority` if the data flow is fully scheduled (i.e., all its data volume is processed), or 0 if the data flow is only partially scheduled or not scheduled at all.

**Constraints:**

1.  **Server Capacity:** The total data volume processed by each server cannot exceed its `processing_capacity`.
2.  **All-or-Nothing Scheduling:** A data flow must be either fully scheduled (all its `data_volume` is processed) or not scheduled at all. Partial scheduling is not allowed.
3.  **Priority Matters:** The scheduler should prioritize flows with higher priority to maximize the total weighted throughput.
4.  **Scalability:** The solution should be efficient enough to handle a large number of servers and data flows. The number of servers `N` and the number of data flows `M` can be up to 1,000. The `data_volume` can be up to 1,000, and the processing capacity can be up to 100,000. The priority can be up to 100.
5.  **Integer Arithmetic:** All calculations must be performed using integer arithmetic to avoid floating-point precision issues.

**Input:**

The input will consist of the following:

*   `N`: The number of servers.
*   `M`: The number of data flows.
*   `processing_capacities`: A vector of integers of length `N`, where `processing_capacities[i]` is the processing capacity of server `i`.
*   `data_flows`: A vector of tuples, where each tuple represents a data flow in the format `(source_server_id, destination_server_id, data_volume, priority)`.

**Output:**

The output should be a single integer representing the maximum achievable total weighted throughput.

**Example:**

```
N = 2
M = 3
processing_capacities = [100, 100]
data_flows = [(0, 1, 50, 2), (1, 0, 60, 3), (0, 1, 70, 1)]
```

One possible optimal solution is to schedule the first two flows. The total weighted throughput would be (50 * 2) + (60 * 3) = 100 + 180 = 280.  The first server processes 50 data volume and second process 60 data volume which are within their respective capacity limits.

**Requirements:**

Your solution must be implemented in Rust and must be efficient enough to pass all test cases within a reasonable time limit. Consider the algorithmic complexity of your solution and optimize accordingly. Think about how the data flows are scheduled to maximize the weighted throughput within the constraints.
