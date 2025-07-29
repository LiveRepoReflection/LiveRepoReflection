## Question: Multi-Commodity Flow Optimization with Dynamic Edge Costs

### Question Description

You are tasked with optimizing the flow of multiple commodities through a network represented by a directed graph. The graph represents a transportation network, where nodes are locations and edges are transportation routes. Each commodity has a source node, a destination node, and a demand, representing the amount of that commodity that needs to be transported from its source to its destination.

The challenge is complicated by the fact that the cost of using each edge is not static. The cost of traversing an edge depends on the total flow (sum of all commodities) currently using that edge. Specifically, the cost of using an edge *e* is a function *c(f_e)*, where *f_e* is the total flow on edge *e*.

**Formal Definition:**

*   **Input:**
    *   A directed graph *G = (V, E)*, where *V* is the set of nodes and *E* is the set of edges.
    *   A set of *K* commodities. For each commodity *k*, you are given:
        *   *s\_k*: Source node for commodity *k*.
        *   *t\_k*: Destination node for commodity *k*.
        *   *d\_k*: Demand for commodity *k*.
    *   A cost function *c\_e(f)* for each edge *e* in *E*. This function takes the total flow *f* on edge *e* as input and returns the cost per unit flow on that edge. Assume *c\_e(f)* is a non-decreasing, non-negative function.
*   **Output:**
    *   For each commodity *k* and each edge *e*, determine the flow *f\_k(e)* of commodity *k* on edge *e*.

**Constraints and Requirements:**

1.  **Flow Conservation:** For each commodity *k* and each node *v* (except the source and destination nodes for that commodity), the inflow of commodity *k* into *v* must equal the outflow of commodity *k* from *v*.
2.  **Demand Satisfaction:** For each commodity *k*, the total flow of commodity *k* leaving the source node *s\_k* must equal the demand *d\_k*, and the total flow of commodity *k* entering the destination node *t\_k* must equal *d\_k*.
3.  **Non-negativity:** The flow of each commodity on each edge must be non-negative (f\_k(e) >= 0 for all k and e).
4.  **Cost Minimization:** The objective is to minimize the total cost of transporting all commodities. The total cost is calculated as the sum, over all edges *e*, of *c\_e(f\_e) \* f\_e*, where *f\_e* is the total flow on edge *e*.
5.  **Edge Cost Function:** The edge cost function *c\_e(f)* is given as a list of (flow, cost) pairs, representing a piecewise linear function. For example, `[(0, 1), (10, 2), (20, 3)]` means:
    *   If 0 <= f <= 10, the cost is 1 + (f - 0) \* (2-1)/(10-0)
    *   If 10 <= f <= 20, the cost is 2 + (f - 10) \* (3-2)/(20-10)
    *   If f > 20, the cost is 3.
6.  **Graph Representation:** The graph *G* will be represented as an adjacency list, where each key is a node and the value is a list of tuples, where each tuple represents an edge to another node and its associated cost function.
7.  **Large Input:** The graph can be large (up to 1000 nodes and 5000 edges), and the number of commodities can be up to 100. Naive solutions will likely time out.
8.  **No Guarantee of Unique Solution:** There might be multiple optimal solutions. Your solution only needs to find one such solution.

**Example:**

Let's consider a simple graph with two nodes (A and B) and one edge (A -> B). There is one commodity that needs to be shipped from A to B.

*   Nodes: `V = {A, B}`
*   Edges: `E = {(A, B)}`
*   Commodities: `K = 1`
    *   `s_1 = A`
    *   `t_1 = B`
    *   `d_1 = 10`
*   Edge Cost Function: `c_(A,B)(f) = [(0, 1), (20, 2)]`

The optimal solution here is to send all 10 units of the commodity from A to B. The total flow on edge (A, B) is 10, and the cost per unit flow is 1 + (10-0) * (2-1)/(20-0) = 1.5. Therefore, the total cost is 10 * 1.5 = 15.

**Grading:**

Your solution will be evaluated based on its correctness (satisfying all constraints) and its ability to minimize the total cost on a set of hidden test cases. The test cases will vary in size, network topology, and the complexity of the edge cost functions. Efficient algorithms and data structures are necessary to pass all test cases within the time limit.

This problem requires a strong understanding of network flow algorithms, optimization techniques, and efficient data structures. Good luck!
