## Question: Distributed Consensus with Bounded Communication

### Question Description:

You are designing a distributed system where a cluster of `N` nodes (numbered from 0 to N-1) needs to reach a consensus on a single integer value. Each node initially holds a *private* integer value.

The system operates under a unique constraint: nodes can only communicate by sending messages directly to a *limited* number of other nodes. Each node `i` has a predefined set of `k` nodes it can directly send messages to (its "neighbors"). This set of neighbors may be different for each node. Communication is *unidirectional*.

The consensus protocol must satisfy the following properties:

1.  **Agreement:** All non-faulty nodes must eventually agree on the same integer value.
2.  **Validity:** The agreed-upon value must be one of the initial private values held by at least one of the nodes. (No invented values are allowed).
3.  **Termination:** The protocol must eventually terminate, meaning all non-faulty nodes will reach a decision.

However, there is a catch: some nodes might be *Byzantine faulty*. A Byzantine faulty node can behave arbitrarily, sending incorrect or inconsistent messages, or even failing to send messages at all.  The number of Byzantine faulty nodes is at most `f`, where `f < N/3`. This is a critical limitation of distributed system.

**Your Task:**

Implement a function `consensus(initial_values, adjacency_list, f)` that takes:

*   `initial_values`: A list of `N` integers representing the initial private values held by each node. `initial_values[i]` is the initial value of node `i`.
*   `adjacency_list`: A list of lists representing the communication graph. `adjacency_list[i]` is a list of integers representing the indices of the nodes that node `i` can *send* messages to.
*   `f`: An integer representing the maximum number of Byzantine faulty nodes.

The function should return the final consensus value that all non-faulty nodes agree upon.

**Constraints and Requirements:**

*   `3 <= N <= 100` (Number of nodes)
*   `1 <= k <= N - 1` (Number of neighbors per node)
*   `0 <= initial_values[i] <= 1000` (Range of initial values)
*   `0 <= f < N/3` (Maximum number of faulty nodes)
*   The adjacency list guarantees that each node has exactly `k` neighbors.  The neighbors for each node will be unique for that node, and will not include the node itself.
*   The solution must tolerate up to `f` Byzantine faulty nodes.
*   The consensus protocol should be efficient in terms of message complexity. While absolute message complexity is not directly tested, solutions that require an excessive number of messages may time out.
*   Your solution must be deterministic. Given the same inputs, it should always produce the same output.
*   Your code will be executed in an environment with limited memory and a strict time limit. Consider the algorithmic efficiency of your solution.
*   The test cases will include various communication graph structures (e.g., complete graphs, sparse graphs, chains, cycles).

**Judging Criteria:**

Your solution will be judged based on its correctness (achieving agreement, validity, and termination under Byzantine faults), its efficiency (avoiding excessive message passing), and its ability to handle various communication graph structures. The tests will include cases with no faulty nodes, as well as cases with up to `f` faulty nodes. A solution will be considered correct if it consistently produces a valid consensus value within the time and memory constraints for all test cases.
