Okay, here's a challenging Rust coding problem designed to test a candidate's understanding of graph algorithms, data structures, and optimization techniques, similar to a LeetCode Hard level question:

### Project Name

`NetworkResilience`

### Question Description

A critical infrastructure network is represented as a weighted, undirected graph.  The nodes represent facilities, and the edges represent communication links with associated costs (positive integers).  The network is considered *resilient* if, even after the *worst-case* single facility failure, all remaining facilities can still communicate with each other.  Communication requires a path between two facilities.

Your task is to design and implement a system for assessing and improving the resilience of this network.  You need to implement two main functions:

1.  `is_resilient(graph: &Graph) -> bool`: Determines whether the given network graph is resilient.  A graph is resilient if, for *every* node in the graph, removing that node and its adjacent edges leaves a connected graph.

2.  `minimize_disruption(graph: &mut Graph, facility_failure_probability: &HashMap<NodeId, f64>, budget: u64) -> Vec<Edge>`: Given a potentially non-resilient graph, a map of facility failure probabilities, and a budget, return a list of new edges to add to the graph that *maximizes* the expected number of facility pairs that can communicate after a potential single facility failure, while staying within the budget.

    *   **Expected Communication**: For each node in the graph, calculate the probability that the node will fail (given in `facility_failure_probability`), and the number of facility pairs that cannot communicate in the sub-graph. Your goal is to add new edges to reduce the overall number of facility pairs that cannot communicate, weighted by the failure probability of each node. The expected number of facility pairs is the sum of the number of facility pairs multiplied by the facility failure probability for each facility.
    *   **Budget**: Each edge has an associated cost equal to the sum of the node IDs it connects. You cannot exceed the given `budget`.
    *   **Optimization**:  Finding the optimal set of edges to add is likely NP-hard.  Your solution should aim to find a "good" (near-optimal) set of edges within a reasonable time limit (e.g., a few seconds).
    *   **Prioritization**: In the case of equal total cost of added edges, the optimal solution is the one that minimizes the expected communication more.
    *   **Tie-breaking**: In the case of equal total cost and the same expected communication, the optimal solution is the one that adds the edges with the smallest NodeId from a-z.

    *   **Constraints**:
        *   You can only add edges between existing nodes in the original graph.
        *   You cannot add duplicate edges (i.e., an edge already exists).
        *   The cost of adding an edge between nodes `u` and `v` is `u + v`.
        *   The NodeId should be unique and start at 'a'

### Data Structures

You are free to choose your own data structures, but consider the following:

*   `NodeId`: A unique identifier for each facility (e.g., a `char`).
*   `Edge`: A tuple representing a connection between two `NodeId`s with an associated cost: `(NodeId, NodeId, u64)`.
*   `Graph`: A representation of the network (e.g., an adjacency list or adjacency matrix). It should efficiently support adding edges, removing nodes, and checking connectivity.
*   `HashMap<NodeId, f64>`: A map that stores the probability of failure for each facility (node). The probability is a float between 0.0 and 1.0, inclusive.

### Additional Considerations

*   **Error Handling:**  Handle invalid input gracefully (e.g., invalid `NodeId`s, negative edge costs, probabilities outside the range \[0, 1]).
*   **Algorithmic Efficiency:**  The `is_resilient` function should be reasonably efficient. The `minimize_disruption` function will likely require a heuristic approach to find a good solution within the time limit.
*   **Testability:**  Design your code with testability in mind.  Consider how you would write unit tests to verify the correctness of your solution.
*   **Real-World Relevance:** Think about how this problem relates to the design and maintenance of critical infrastructure networks.

This problem requires a combination of graph theory knowledge, algorithmic thinking, and practical programming skills. Good luck!
