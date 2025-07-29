## Problem Name: Distributed Key-Value Store with Conflict Resolution

### Problem Description:

You are tasked with implementing a highly available and distributed key-value store. This store needs to handle concurrent write operations to the same key across multiple nodes. To resolve conflicting updates, you will implement a conflict resolution mechanism based on Vector Clocks.

**System Design Requirements:**

The key-value store consists of `N` nodes (represented by integers from 0 to N-1). Each node is capable of storing key-value pairs and communicating with other nodes in the system.

**Data Model:**

*   **Key:** String
*   **Value:** String
*   **Vector Clock:** An array of integers of length `N`, where the i-th element represents the number of updates observed by node i for a particular key-value pair.

**Operations:**

1.  **`Put(key string, value string, vectorClock []int)`**: Stores a new key-value pair or updates an existing one. The `vectorClock` represents the current version of the data. If the key exists, your implementation must compare the incoming `vectorClock` with the stored `vectorClock` and resolve any conflicts.

2.  **`Get(key string)`**: Retrieves the value associated with a given key. If there are multiple conflicting versions of the value, you must return *all* conflicting values along with their respective vector clocks.

**Conflict Resolution:**

Implement the following rules to determine the relationship between two vector clocks, `A` and `B`:

*   **A is concurrent with B:** If there exists an `i` such that `A[i] > B[i]` and a `j` such that `B[j] > A[j]`. This means that neither update is a descendant of the other. In this case, both versions must be retained.

*   **A is a descendant of B:** If `A[i] >= B[i]` for all `i` and there exists at least one `j` such that `A[j] > B[j]`. This means that A incorporates all the updates in B, and thus A supersedes B.

*   **A is an ancestor of B:** If `B[i] >= A[i]` for all `i` and there exists at least one `j` such that `B[j] > A[j]`. This means that B incorporates all the updates in A, and thus B supersedes A.

**Implementation Details and Constraints:**

*   You must use Go as the implementation language.
*   The number of nodes, `N`, is fixed at compile time and is available as a constant in your code (e.g., `const N = 5`).
*   You do not need to implement the actual network communication between nodes. Assume a single-node simulation.
*   You must handle concurrent updates correctly using the specified vector clock conflict resolution mechanism.
*   The `Get` operation must return *all* concurrent versions (value and associated vectorClock).
*   Your solution should be optimized for read performance. While writes are important, frequent reads are expected.
*   You can choose the data structures you see fit to store the key-value pairs and their vector clocks. Consider using a concurrent-safe data structure.

**Example:**

Assume N = 3.

1.  Node 0 executes `Put("x", "value1", [1, 0, 0])`
2.  Node 1 executes `Put("x", "value2", [0, 1, 0])`

Now, `Get("x")` should return two versions:

*   Value: "value1", Vector Clock: \[1, 0, 0]
*   Value: "value2", Vector Clock: \[0, 1, 0]

because the updates are concurrent.

Then, Node 0 executes `Put("x", "value3", [2, 1, 0])`

Now, `Get("x")` should return one version:

*   Value: "value3", Vector Clock: \[2, 1, 0]

because [2, 1, 0] supersedes [1, 0, 0] and [0, 1, 0].
