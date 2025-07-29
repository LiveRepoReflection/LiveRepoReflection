## Project Name

`Highly Connected Graph Partitioning`

## Question Description

You are given a representation of a social network as a graph. Each node in the graph represents a user, and an edge between two nodes indicates that the corresponding users are friends. Your task is to partition this social network into a specified number of communities, aiming to maximize the "connectivity" within each community and minimize the connections between different communities.

More formally:

*   **Input:**
    *   `n`: The number of users (nodes) in the social network, where `1 <= n <= 100,000`.
    *   `edges`: A list of tuples, where each tuple `(u, v)` represents an undirected edge between user `u` and user `v`. User IDs are 0-indexed, so `0 <= u, v < n`. The number of edges `m` satisfies `0 <= m <= min(n*(n-1)/2, 500,000)`.
    *   `k`: The desired number of communities, where `1 <= k <= min(n, 20)`.

*   **Output:**
    *   A list of length `n`, where the `i`-th element represents the community assignment for user `i`. The community assignments should be integers from `0` to `k-1`.

*   **Objective Function (to be maximized):**
    The objective function is defined as modularity. Higher modularity signifies a "better" community structure.

    **Modularity (Q)** = (1 / (2\*m)) \* Σ<sub>i,j</sub> \[A<sub>ij</sub> - (d<sub>i</sub>\*d<sub>j</sub>) / (2\*m)] \* δ(c<sub>i</sub>, c<sub>j</sub>)

    Where:

    *   `m` is the total number of edges in the graph.
    *   `A<sub>ij</sub>` is 1 if there's an edge between nodes `i` and `j`, and 0 otherwise.
    *   `d<sub>i</sub>` is the degree (number of connections) of node `i`.
    *   `c<sub>i</sub>` is the community to which node `i` is assigned.
    *   δ(c<sub>i</sub>, c<sub>j</sub>) is 1 if nodes `i` and `j` belong to the same community, and 0 otherwise.
    *   The summation Σ<sub>i,j</sub>  is over all pairs of nodes in the network.

*   **Constraints and Considerations:**

    1.  **Efficiency:** The solution must be computationally efficient, as the social network can be large (up to 100,000 users and 500,000 edges).  Solutions with time complexity significantly higher than O(m\*log(n)) or O(n^2) may timeout.  Consider using appropriate data structures and algorithms.
    2.  **Quality of Partitioning:** The primary goal is to maximize the modularity of the resulting community structure.  A valid solution must produce a partitioning of all nodes into the specified number of communities, but the solution will be judged on the modularity score it achieves compared to other solutions. Getting very close to optimal solution (e.g. using sophisticated algorithms) is key to outperforming other solvers.
    3.  **Multiple Valid Solutions:** There might be multiple valid community structures that maximize modularity. Your algorithm should aim to find one of the best possible solutions within the given time constraints.
    4.  **Graph Representation:** You are free to choose the graph representation that best suits your algorithm (e.g., adjacency list, adjacency matrix).
    5.  **No External Libraries (Except Standard Python Libraries):** You are allowed to use standard Python libraries (e.g., `collections`, `heapq`, `random`, `math`). However, you are **not** allowed to use external libraries like `networkx`, `igraph`, or any other specialized graph libraries.  The goal is to assess your algorithmic skills, not your ability to use existing tools.
    6. **Edge cases:** Handle cases where the graph is disconnected, or where `k` is close to `n`. Consider also the case where the graph has very few edges.
    7. **Time limit:** the time limit is set to 30 seconds.

*   **Judging:**

    Your solution will be evaluated by running it on a series of test cases with different social network topologies and desired community counts. The modularity of your solution will be compared to other submissions, and the solution with the highest modularity will be considered the best.  The test cases will include a variety of graph structures, including scale-free networks, small-world networks, and random graphs.

This problem requires you to combine graph algorithms, data structure knowledge, and optimization techniques to find a high-quality community structure in a large social network. Good luck!
