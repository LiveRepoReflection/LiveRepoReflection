## Question: Optimal High-Density Storage Allocation

### Question Description

You are tasked with designing a high-density storage allocation system for a data center. The data center has a large number of storage devices, each with its own capacity.  Incoming data chunks need to be efficiently allocated across these devices to maximize storage utilization and minimize fragmentation.

Each data chunk has a specific size and a set of *affinity requirements*. Affinity requirements dictate which storage devices are suitable for storing that chunk. These requirements can be due to data locality, security constraints, or other application-specific reasons.  A data chunk *must* be stored on a device that satisfies *all* of its affinity requirements.

Your goal is to write a function that, given a list of storage devices, a list of data chunks, and their respective affinity requirements, determines an optimal allocation of data chunks to storage devices.

**Specifically, you must implement the following:**

*   **Allocation Strategy:** The storage allocation should be performed in a way that attempts to minimize the total number of storage devices used. In other words, you should try to pack as many chunks as possible onto a single device before moving on to the next available device.

*   **Data Chunk Splitting:** A single data chunk *cannot* be split across multiple storage devices. It must reside entirely on a single storage device that meets its affinity requirements and has sufficient capacity.

*   **Dynamic Affinity:** Affinity requirements are not just a simple allow/deny list. Instead, each storage device is assigned a list of *capabilities*. Each data chunk requests a list of *required capabilities*. A storage device is only suitable for a data chunk if the device's capabilities *contain* all of the chunk's required capabilities (i.e., the chunk's required capabilities are a subset of the device's capabilities).

*   **Optimization Goal:** Your primary goal is to minimize the number of storage devices used. Secondarily, you should aim to balance the utilization across the used devices (i.e., avoid having one device nearly full while another is almost empty).

**Input:**

*   `devices`: A list of tuples. Each tuple represents a storage device and contains:
    *   `device_id` (string): A unique identifier for the storage device.
    *   `capacity` (int): The total storage capacity of the device (in MB).
    *   `capabilities` (set of strings): The set of capabilities supported by the device.

*   `chunks`: A list of tuples. Each tuple represents a data chunk and contains:
    *   `chunk_id` (string): A unique identifier for the data chunk.
    *   `size` (int): The size of the data chunk (in MB).
    *   `required_capabilities` (set of strings): The set of capabilities required by the data chunk.

**Output:**

A dictionary representing the optimal storage allocation.  The keys of the dictionary are `device_id`s.  The values are lists of `chunk_id`s allocated to that device. If a chunk cannot be allocated to any device, it should be placed in a list associated with the key `"unallocated"`. The dictionary should only contain `device_id`s that have at least one chunk allocated to them, in addition to the `"unallocated"` key if there are any unallocated chunks.

**Constraints:**

*   The number of storage devices can be large (up to 1000).
*   The number of data chunks can be large (up to 10000).
*   Device capacities and chunk sizes can vary significantly (from 1 MB to 10000 MB).
*   Affinity requirements can be complex, with chunks requiring multiple capabilities and devices providing varying sets of capabilities.
*   The solution must be computationally efficient. A naive brute-force approach will likely time out. Consider using appropriate data structures and algorithms.
*   If multiple optimal allocations exist (i.e., allocations that use the same minimal number of devices), any of them is acceptable.

**Example:**

```python
devices = [
    ("device1", 100, {"A", "B", "C"}),
    ("device2", 50, {"B", "D"}),
    ("device3", 75, {"A", "C"}),
]

chunks = [
    ("chunk1", 30, {"A", "C"}),
    ("chunk2", 20, {"B"}),
    ("chunk3", 60, {"A"}),
    ("chunk4", 40, {"B", "D"}),
]

# One possible optimal allocation:
# {
#     "device1": ["chunk3"],
#     "device2": ["chunk2", "chunk4"],
#     "device3": ["chunk1"],
#     "unallocated": []
# }
```

**Judging Criteria:**

*   **Correctness:** The allocation must satisfy all constraints (affinity requirements, no chunk splitting, capacity constraints).
*   **Optimality:** The allocation must use the minimal possible number of storage devices.
*   **Efficiency:** The solution must complete within a reasonable time limit.
*   **Code Clarity:** The code should be well-structured, readable, and maintainable.

This problem requires careful consideration of algorithm design, data structure selection, and optimization techniques. Good luck!
