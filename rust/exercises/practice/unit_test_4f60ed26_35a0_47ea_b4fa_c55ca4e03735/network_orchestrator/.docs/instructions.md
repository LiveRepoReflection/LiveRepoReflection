## Project Name

```
NetworkOrchestrator
```

## Question Description

You are tasked with designing and implementing a network orchestrator for a large-scale distributed system. This system consists of a network of interconnected nodes, each capable of performing various tasks. The orchestrator's role is to efficiently assign tasks to nodes, considering their capabilities, network latency, and resource constraints.

**System Overview:**

*   **Nodes:** Represented by unique IDs (integers). Each node has a set of capabilities (strings) indicating the types of tasks it can perform, CPU cores, and memory size(MB).
*   **Tasks:** Represented by unique IDs (integers). Each task requires a specific capability (string), CPU cores, and memory size(MB).
*   **Network:** The network is represented as a weighted graph where nodes are vertices and the weights represent the latency between them. Latency is represented as an integer. A latency of -1 indicates that there is no direct connection between the two nodes. Assume the graph is undirected.
*   **Orchestrator:** Your orchestrator must efficiently assign tasks to available nodes minimizing total cost. The total cost is the sum of CPU cost, Memory cost and Latency cost. CPU cost is `CPU_WEIGHT * (task_cpu/node_cpu)`. Memory cost is `MEM_WEIGHT * (task_mem/node_mem)`. Latency cost is the latency between the node requesting the task and the node that will be assigned the task.

**Requirements:**

1.  **Task Assignment:** Implement a function `assign_tasks` that takes the following inputs:
    *   `nodes`: A `HashMap<NodeId, Node>` representing the available nodes in the system.
    *   `tasks`: A `HashMap<TaskId, Task>` representing the tasks to be assigned.
    *   `network`: A `HashMap<(NodeId, NodeId), i32>` representing the network latency between nodes.
    *   `requesting_node`: `NodeId` representing the ID of the node requesting the task.
2.  **Capability Matching:** Tasks can only be assigned to nodes possessing the required capability.
3.  **Resource Constraints:** Nodes have limited CPU cores and memory. A task can only be assigned to a node if it has sufficient available resources.
4.  **Latency Minimization:** The orchestrator should attempt to minimize the total latency cost when assigning tasks.
5.  **Optimization:** The solution should be optimized for performance. Consider the time complexity of your algorithm, especially when dealing with a large number of nodes and tasks. There might be multiple valid solutions; the solution with the lowest total cost is preferred.
6.  **CPU and Memory Utilization:** The orchestrator should attempt to balance the CPU and memory utilization across the nodes to prevent overloading any single node.
7.  **Error Handling:** Return appropriate error messages for cases where tasks cannot be assigned (e.g., no node with the required capability, insufficient resources).
8.  **Asynchronous Handling:** While not strictly required to be implemented asynchronously, consider how your design could be adapted to handle task assignments asynchronously in a real-world distributed system.

**Data Structures:**

```rust
use std::collections::HashMap;

type NodeId = u32;
type TaskId = u32;

#[derive(Debug, Clone)]
struct Node {
    id: NodeId,
    capabilities: Vec<String>,
    cpu_cores: u32,
    memory_mb: u32,
    available_cpu: u32,
    available_memory: u32,
}

#[derive(Debug, Clone)]
struct Task {
    id: TaskId,
    required_capability: String,
    cpu_cores: u32,
    memory_mb: u32,
}
```

**Constraints:**

*   The number of nodes can be up to 1000.
*   The number of tasks can be up to 1000.
*   Node IDs and Task IDs are unique.
*   CPU cores and memory sizes are positive integers.
*   `CPU_WEIGHT` and `MEM_WEIGHT` are constants defined as 0.4 and 0.6 respectively.
*   Your solution must be able to handle edge cases, such as:
    *   Empty node or task lists.
    *   Tasks with no matching node capabilities.
    *   Nodes with insufficient resources for any task.
    *   Network graphs with disconnected nodes.
*   The solution needs to be efficient enough to handle large numbers of nodes and tasks within reasonable time limits (e.g., under 10 seconds).
*   The function signature must be exactly as specified below.

**Output:**

The `assign_tasks` function should return a `Result<HashMap<TaskId, NodeId>, String>`. The `HashMap` maps each `TaskId` to the `NodeId` it has been assigned to. If a task cannot be assigned, it should not be present in the output map. If no tasks can be assigned, return an empty `HashMap`. If an error occurs, return a descriptive error string.

**Function Signature:**

```rust
fn assign_tasks(
    nodes: HashMap<NodeId, Node>,
    tasks: HashMap<TaskId, Task>,
    network: HashMap<(NodeId, NodeId), i32>,
    requesting_node: NodeId,
) -> Result<HashMap<TaskId, NodeId>, String>;
```

This problem requires a good understanding of graph algorithms, resource allocation strategies, and optimization techniques. Consider using algorithms like Dijkstra's or Floyd-Warshall for shortest path calculations, and explore heuristics or approximation algorithms to find near-optimal task assignments within the given constraints. Good luck!
