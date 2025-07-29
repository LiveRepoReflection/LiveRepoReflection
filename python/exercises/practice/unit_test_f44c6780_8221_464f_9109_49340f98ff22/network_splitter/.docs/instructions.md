## Question:

### Problem Title:

**Optimal Network Splitting for Disaster Recovery**

### Problem Description:

You are a network architect designing a resilient communication infrastructure for a large geographical region. The region is represented as an undirected, weighted graph where cities are nodes and communication links between them are edges. The weight of each edge represents the latency of the communication link.

A major disaster is anticipated, and your task is to divide the network into `k` independent sub-networks (clusters) such that communication within each cluster is as efficient as possible, and disruption between clusters is minimized. The goal is to minimize the maximum diameter across all clusters and minimize the total inter-cluster edge weight (cut size).

Formally:

1.  **Input:**
    *   An undirected, weighted graph `G = (V, E)` where `V` is the set of vertices (cities) and `E` is the set of edges (communication links with latency).
    *   A positive integer `k`, representing the number of desired clusters.
    *   A parameter `alpha` (0 <= `alpha` <= 1.0) defining the weight between minimizing the maximum diameter and total inter-cluster edge weight.

2.  **Output:**
    *   An assignment of each vertex in `V` to a cluster ID (an integer between 1 and `k` inclusive). Each vertex must belong to exactly one cluster.

3.  **Objective Function:**

    Minimize `alpha * max_diameter + (1 - alpha) * normalized_cut_size`, where:

    *   `max_diameter`: The maximum diameter among all `k` clusters. The diameter of a cluster is the maximum shortest path distance between any two nodes within that cluster. If a cluster contains only 1 node, its diameter is 0.
    *   `cut_size`:  The sum of the weights of all edges that connect vertices in different clusters.
    *   `normalized_cut_size = cut_size / total_edge_weight` where `total_edge_weight` is the sum of all edge weights in the original graph.

4.  **Constraints:**

    *   `1 <= k <= |V|`
    *   The graph `G` is connected.
    *   Edge weights are positive integers.
    *   Each cluster must have at least one vertex.
    *   Your solution must scale reasonably for graphs with up to 1000 vertices and 10000 edges.  Solutions that perform an exhaustive search will not pass.

5.  **Optimization Requirements:**

    *   The primary goal is to minimize the objective function.
    *   Solutions that provide significantly better results on the test datasets will be preferred.
    *   Solutions that are efficient in terms of time and memory usage will be preferred.

6.  **Evaluation:**

    Your solution will be evaluated based on its ability to minimize the objective function across a range of test cases with varying graph structures, values of `k`, and values of `alpha`. Test cases will include a mix of randomly generated graphs and graphs representing real-world infrastructure networks.

### Example:

Let's say you have a graph with 4 vertices (A, B, C, D) and edges:

*   A-B (weight: 1)
*   B-C (weight: 1)
*   C-D (weight: 1)
*   A-D (weight: 5)

And you want to split it into k=2 clusters with alpha = 0.5.

One possible solution is:

*   Cluster 1: A, B
*   Cluster 2: C, D

*   Diameter of Cluster 1: 1 (distance between A and B)
*   Diameter of Cluster 2: 1 (distance between C and D)
*   max_diameter = 1

*   cut_size: 1 (edge B-C) + 5 (edge A-D) = 6
*   total_edge_weight: 1 + 1 + 1 + 5 = 8
*   normalized_cut_size: 6/8 = 0.75

*   Objective function: 0.5 * 1 + 0.5 * 0.75 = 0.875

Another possible solution is:

*   Cluster 1: A, D
*   Cluster 2: B, C

*   Diameter of Cluster 1: 5 (distance between A and D)
*   Diameter of Cluster 2: 1 (distance between B and C)
*   max_diameter = 5

*   cut_size: 1 (edge A-B) + 1 (edge C-D) = 2
*   total_edge_weight: 1 + 1 + 1 + 5 = 8
*   normalized_cut_size: 2/8 = 0.25

*   Objective function: 0.5 * 5 + 0.5 * 0.25 = 2.625

The first solution would be preferred, as it has a lower objective function value.

### Notes:

*   Consider various graph partitioning algorithms and heuristics.
*   Experiment with different approaches to find a good balance between minimizing the maximum diameter and the normalized cut size.
*   Pay close attention to time complexity and memory usage, especially for larger graphs.
*   Pre-computing shortest paths might be useful.
*   This is a computationally hard problem. Aim for a solution that provides reasonable results within the given constraints.
