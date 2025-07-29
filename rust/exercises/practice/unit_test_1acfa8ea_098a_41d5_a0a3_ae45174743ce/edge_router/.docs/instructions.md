## Question: Optimal Edge Router Placement

### Question Description

You are tasked with designing a robust and efficient network infrastructure for a rapidly growing decentralized social media platform. The platform relies on a peer-to-peer network where users connect to each other to share content. To improve network performance and resilience, you need to strategically place edge routers within the network.

The network is represented as an undirected graph where nodes represent users and edges represent connections between users. Each user has a certain "influence score," which represents the amount of traffic they generate on the network. Edge routers act as content caches and traffic managers, reducing latency and improving network stability.

Your goal is to select a set of *k* users to host edge routers such that the overall "network coverage" is maximized while minimizing the cost of router deployment.

**Network Coverage:** The coverage of a user *u* is defined as its influence score if *u* has an edge router. If *u* does not have an edge router, its coverage is a fraction of its influence score, specifically *influence_score(u) / (d(u, R) + 1)* where *d(u, R)* is the shortest path distance between user *u* and the nearest edge router in the chosen set *R*.

**Router Deployment Cost:** Each user has a unique "hosting cost" associated with deploying an edge router on their node.

**Your task is to write a function that:**

1.  Takes as input the network graph, the influence score of each user, the hosting cost for each user, and the number of edge routers to deploy (*k*).
2.  Returns a set of *k* user IDs (nodes) representing the optimal locations for the edge routers.
3.  The objective is to maximize the total network coverage minus the total deployment cost.

**Constraints:**

*   The graph can be large (up to 10,000 nodes and 100,000 edges).
*   The influence scores and hosting costs are positive integers.
*   The number of edge routers *k* is significantly smaller than the number of users.
*   Finding the absolute optimal solution might be computationally infeasible within the time limit. Therefore, you need to find a near-optimal solution using efficient algorithms and data structures.
*   Execution time is critical. Solutions that are not reasonably efficient will time out.
*   The input graph may not be fully connected.

**Input Format:**

*   `num_users`: An integer representing the number of users in the network.
*   `edges`: A vector of tuples, where each tuple `(u, v)` represents an undirected edge between user *u* and user *v*. User IDs are 0-indexed.
*   `influence_scores`: A vector of integers, where `influence_scores[i]` represents the influence score of user *i*.
*   `hosting_costs`: A vector of integers, where `hosting_costs[i]` represents the hosting cost of placing an edge router on user *i*.
*   `k`: An integer representing the number of edge routers to deploy.

**Output Format:**

*   A vector of integers representing the user IDs (nodes) where the edge routers should be placed. The vector should contain exactly *k* elements.

**Example:**

Let's say you have a small network:

*   `num_users = 5`
*   `edges = [(0, 1), (1, 2), (2, 3), (3, 4)]`
*   `influence_scores = [10, 15, 20, 12, 8]`
*   `hosting_costs = [5, 7, 9, 6, 4]`
*   `k = 2`

A possible (but not necessarily optimal) solution could be `[1, 3]`.

**Judging:**

Your solution will be judged based on the total network coverage minus the total deployment cost achieved on a set of hidden test cases. The higher the score, the better. Efficiency and correctness are crucial. Solutions that produce incorrect results or time out will receive a low score.
