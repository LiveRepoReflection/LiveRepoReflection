## Project Name

`Network Congestion Game`

## Question Description

You are tasked with simulating and analyzing a network congestion game. In this game, multiple users (or agents) want to route traffic between two specific nodes in a network. Each edge in the network has a cost function that depends on the amount of traffic flowing through it. The goal is to find a stable state, a Nash Equilibrium, where no user can unilaterally change their route to improve their individual cost.

**Network Representation:**

The network is represented as a directed graph. Each edge has a cost function associated with it. The cost function is linear and of the form `cost(x) = a*x + b`, where `x` is the traffic flow on the edge, `a` is the congestion factor, and `b` is the fixed cost.

**Users and Routing:**

Each user wants to send 1 unit of traffic from a source node `s` to a target node `t`.  Users can choose any path between `s` and `t`. The cost for a user is the sum of the costs of all edges along their chosen path, considering the traffic flow on those edges.

**Nash Equilibrium:**

A Nash Equilibrium occurs when no user can reduce their cost by unilaterally switching to a different path.

**Your Task:**

You are given:

*   `n`: The number of nodes in the network, numbered from 0 to n-1.
*   `edges`: A list of tuples representing the directed edges in the network. Each tuple is of the form `(u, v, a, b)`, where:
    *   `u` is the source node of the edge.
    *   `v` is the destination node of the edge.
    *   `a` is the congestion factor of the edge.
    *   `b` is the fixed cost of the edge.
*   `s`: The source node.
*   `t`: The target node.
*   `num_users`: The number of users wanting to route traffic from `s` to `t`.

Your task is to write a function that performs the following:

1.  **Initialization:** Initially, assign all users to the shortest path from `s` to `t` based *only* on the fixed cost `b` of the edges (ignore the congestion factor `a` initially). If there are multiple shortest paths, choose one arbitrarily.

2.  **Iterative Improvement:** Iterate through each user one at a time. For each user, calculate the current cost of their path. Then, find the path from `s` to `t` that minimizes their cost, *considering the current traffic flow on all edges.* If switching to this new path reduces their cost, update their path to the new path.

3.  **Termination:** Repeat the iterative improvement process until no user switches paths in a complete iteration (i.e., going through all users once). This indicates that a Nash Equilibrium has been reached (or at least a local minimum).

4.  **Output:** Return a dictionary where the keys are edges (tuples of the form `(u, v)`) and the values are the final traffic flow (number of users using that edge) on that edge after reaching the Nash Equilibrium.

**Constraints:**

*   1 <= `n` <= 100
*   1 <= number of `edges` <= 300
*   0 <= `s` < `n`
*   0 <= `t` < `n`
*   1 <= `num_users` <= 50
*   0 <= `a` <= 10  (congestion factor)
*   0 <= `b` <= 10 (fixed cost)
*   It's guaranteed that there is at least one path from `s` to `t`.
*   Assume the graph is strongly connected.

**Optimization Requirements:**

*   Your solution should be reasonably efficient. Naive approaches with very high time complexity might not pass all test cases. Consider using appropriate data structures and algorithms for graph traversal and shortest path finding.
*   Avoid unnecessary computations within the iterative improvement loop.  Cache computed values if they remain constant across iterations.

**Example:**

Let's say you have a simple network with two paths from node 0 to node 1:

*   Path 1:  Edge (0, 1) with cost function `cost(x) = 1*x + 1`
*   Path 2:  Edge (0, 2) with cost function `cost(x) = 2*x + 0`, Edge (2, 1) with cost function `cost(x) = 0*x + 2`

If there are 2 users, the initial assignment might put both users on Path 1.  The iterative improvement process might then move one user to Path 2 to reduce their cost, eventually reaching a Nash Equilibrium.

**Note:** This problem involves aspects of graph algorithms (shortest paths), simulation, and game theory (Nash Equilibrium). It requires careful consideration of data structures and algorithmic efficiency. There might be multiple valid Nash Equilibria, and your solution should converge to one of them.
