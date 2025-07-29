## Question: Distributed Key-Value Store Consistency

### Question Description

You are tasked with implementing a simplified version of a distributed key-value store that guarantees eventual consistency. The store consists of multiple nodes, each capable of storing data. Due to network partitions and node failures, data can become inconsistent across the nodes. Your goal is to implement a conflict resolution mechanism that ensures all nodes eventually converge to the same state.

**Specifically:**

Imagine a scenario where multiple clients are updating the same key in the distributed system. Each write operation to a node creates a new version of the value associated with the key, along with a vector clock.

**Data Structure:**

*   **Key:** A string representing the key in the key-value store.
*   **Value:** A string representing the value associated with the key.
*   **Version Vector (Vector Clock):** A dictionary where each key is a node ID (string) and the value is a counter representing the number of updates made by that node to the key. For example, `{'node1': 3, 'node2': 1}` means node1 has updated the key 3 times and node2 has updated it once.

**Your Task:**

Implement a function `resolve_conflicts(versions)` that takes a list of `versions` as input. Each `version` is a tuple `(value, vector_clock)`. The function should return a single `version` (a tuple `(value, vector_clock)`) that represents the resolved state of the key.

**Conflict Resolution Rules:**

1.  **Dominance:** If one version's vector clock dominates all other version's vector clocks, that version is the correct one. A vector clock A dominates vector clock B if for every node in B, A's counter for that node is greater than or equal to B's counter. Furthermore, there must be at least one node where A's counter is strictly greater than B's.

2.  **Concurrent Versions:** If no version dominates all others, the versions are considered concurrent. In this case, the conflict resolution strategy is to merge the values lexicographically (i.e., choose the value that would come first in a dictionary) and create a new vector clock. The new vector clock should contain the maximum counter for each node from all the conflicting versions.

**Input:**

*   `versions`: A list of tuples, where each tuple represents a version of the data. Each tuple is in the format `(value, vector_clock)`.

**Output:**

*   A single tuple `(value, vector_clock)` representing the resolved version of the data.

**Constraints:**

*   The list `versions` will always contain at least one version.
*   Node IDs are strings.
*   Vector clock counters are non-negative integers.
*   The number of nodes in the system is not known in advance. The vector clocks might not contain every node.
*   Assume all vector clocks in `versions` pertain to the same `key`.
*   Efficiency is important. Strive for a solution with a reasonable time complexity. The number of versions and nodes could potentially be large.

**Example:**

```python
versions = [
    ("value1", {"node1": 1, "node2": 1}),
    ("value2", {"node1": 2, "node2": 1}),
    ("value3", {"node1": 1, "node2": 2})
]

resolved_version = resolve_conflicts(versions)
# Expected output: ("value2", {"node1": 2, "node2": 1}) because ("value2", {"node1": 2, "node2": 1}) dominates ("value1", {"node1": 1, "node2": 1})

versions = [
    ("value1", {"node1": 2, "node2": 1}),
    ("value2", {"node1": 1, "node2": 2})
]

resolved_version = resolve_conflicts(versions)
# Expected output: ("value1", {"node1": 2, "node2": 2}) because "value1" < "value2" and the vector clock is the merged clock
```

**Bonus:**

*   Consider the case where values are not strings but more complex data structures. How would you adapt the conflict resolution strategy?
*   How would you handle deleted keys (tombstones) in this system?

This question is designed to test your understanding of distributed systems concepts, data structures, algorithms, and conflict resolution strategies. It requires careful consideration of edge cases and optimization for efficiency. Good luck!
