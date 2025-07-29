Okay, I'm ready to set a new hard-level programming competition problem. Here it is:

## Project Name

`Network Congestion Control`

## Question Description

You are tasked with simulating a network congestion control algorithm within a simplified network. The network consists of `n` nodes (numbered 0 to n-1) and `m` unidirectional links connecting these nodes. Each link has a capacity representing the maximum data rate it can handle.

The goal is to implement a rate-limiting mechanism at each node to prevent congestion, aiming for efficient network utilization without exceeding link capacities.

Specifically, you need to implement a distributed algorithm where each node dynamically adjusts its sending rate based on feedback signals from the links it directly uses.

**Network Model:**

*   The network topology is represented by an adjacency list where `network[i]` contains a list of tuples `(j, capacity)`, indicating a unidirectional link from node `i` to node `j` with the given `capacity`.
*   Each node `i` initially sends data at a rate of `initial_rate`.
*   Time is divided into discrete rounds.

**Congestion Feedback:**

*   After each round, each link calculates its utilization, defined as the total data rate passing through it divided by its capacity.
*   If a link's utilization exceeds a threshold `congestion_threshold` (e.g., 0.9), it sends a congestion signal back to the sending node.
*   Nodes receiving a congestion signal reduce their sending rate by a factor of `decrease_factor` (e.g., 0.5).
*   If a node has no outgoing links reporting congestion and its sending rate is below `max_rate`, it increases its sending rate by a fixed increment `increase_increment` (e.g., 1.0).

**Task:**

Implement a function `simulate_congestion_control(n, network, initial_rate, max_rate, congestion_threshold, decrease_factor, increase_increment, num_rounds)` that simulates the network congestion control algorithm for the specified number of rounds.

The function should return a list of length `n`, where the `i`-th element represents the final sending rate of node `i` after `num_rounds`.

**Constraints and Requirements:**

*   `1 <= n <= 1000`
*   `0 <= m <= 5000`
*   `0 < initial_rate <= max_rate <= 1000.0`
*   `0 < congestion_threshold < 1.0`
*   `0 < decrease_factor < 1.0`
*   `0 < increase_increment <= 10.0`
*   `1 <= num_rounds <= 100`
*   The network is guaranteed to be connected.
*   Your solution should be efficient and avoid unnecessary computations. Inefficient solutions may time out. Pay particular attention to data structures and algorithm choices.

**Edge Cases:**

*   Handle the case where a node has no outgoing links.
*   Ensure that the sending rate never exceeds `max_rate` or becomes negative.
*   Be careful with floating-point precision. Consider using a small tolerance when comparing floating-point numbers.

**Optimization:**

*   Focus on writing a solution that is both correct and efficient. The test cases will be designed to reward optimized solutions.

**Example:**

Let's say you have a network with 2 nodes, a link from node 0 to node 1 with a capacity of 10, initial rate of 5, max rate of 10, congestion threshold of 0.9, decrease factor of 0.5, increase increment of 1, and simulation duration of 5 rounds. The function call would be:

```python
simulate_congestion_control(2, {0: [(1, 10)], 1: []}, 5.0, 10.0, 0.9, 0.5, 1.0, 5)
```

This will test ability to simulate the rate-limiting mechanisms, and will be rated as Hard.

Good luck!
