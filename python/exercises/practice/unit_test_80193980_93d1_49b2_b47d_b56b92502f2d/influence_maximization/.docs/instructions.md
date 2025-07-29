Okay, here's a problem designed to be quite challenging, incorporating several of the elements you requested:

**Project Title:**  Social Network Influence Maximization

**Problem Description:**

You are tasked with optimizing a viral marketing campaign for a new product on a social network. The social network is represented as a directed graph where nodes are users and edges represent influence relationships.  Each user `u` has an influence score `influence(u)` (a positive integer). If a user `u` is "activated" (i.e., they purchase the product and promote it), they can influence their direct followers (out-neighbors in the graph) to also become activated.

The probability that user `u` activates user `v` (where `v` is a direct follower of `u`) is given by `influence(u) / (influence(u) + influence(v))`.

Given the social network graph, a budget `k` representing the maximum number of users you can initially activate, and a target number of total activated users `T`, your goal is to select an initial set of `k` users (the "seed set") that maximizes the *probability* of reaching at least `T` activated users in the entire network.

**Constraints and Requirements:**

1.  **Graph Representation:** The graph will be provided as an adjacency list.  The keys of the dictionary are user IDs (integers), and the values are lists of integers representing the user IDs of their direct followers.

2.  **Influence Scores:** A dictionary mapping user IDs (integers) to their influence scores (positive integers) will be provided.

3.  **Optimization:**  Finding the absolute optimal seed set is likely NP-hard.  Therefore, you are expected to implement an *efficient* heuristic algorithm that provides a good approximation.  Solutions that are demonstrably too slow will be penalized.

4.  **Probability Calculation:** Since exactly calculating the probability of reaching `T` users is computationally expensive, you will use a Monte Carlo simulation approach. You need to perform multiple independent simulations to estimate the probability.

5.  **Edge Cases:**

    *   Handle disconnected graphs gracefully.
    *   Consider cases where `k` is larger than the total number of users.
    *   Consider cases where `T` is larger than the total number of users.
    *   Handle cases where the graph is empty.
    *   Handle cases where `influence(u) + influence(v)` is zero for some edges.

6.  **Efficiency:** The solution must be able to handle graphs with up to 10,000 nodes and 100,000 edges within a reasonable time limit (e.g., a few minutes).  The simulation count should be adjustable to balance accuracy and runtime.  Consider using appropriate data structures and algorithms to optimize performance.

7.  **Tie Breaking:** If multiple seed sets result in the same estimated probability, choose the one with the lowest sum of user IDs in the seed set.

8.  **Input:** The function should accept the following inputs:

    *   `graph`: A dictionary representing the social network graph (adjacency list).
    *   `influence_scores`: A dictionary mapping user IDs to their influence scores.
    *   `k`: The budget (number of users to initially activate).
    *   `T`: The target number of activated users.
    *   `num_simulations`: The number of Monte Carlo simulations to run (integer, e.g., 1000).

9. **Output:** The function should return a sorted list of user IDs representing the optimal seed set.

This problem requires a strong understanding of graph algorithms, probability, simulation techniques, and optimization strategies. It also demands careful consideration of edge cases and performance. Good luck!
