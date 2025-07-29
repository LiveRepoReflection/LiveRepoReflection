# Network Routing

This project implements an optimal routing algorithm for a complex network. The network consists of nodes connected by bidirectional edges, each with an associated latency and bandwidth.

## Problem Description

Given a network with N nodes and M bidirectional edges, find the path between a source node S and a destination node D that maximizes the available bandwidth while satisfying the given latency constraint.

The main constraints are:
- The path must satisfy both a minimum bandwidth requirement B and a maximum latency constraint L
- If multiple paths satisfy the constraints, choose the path with the highest minimum bandwidth along the path
- Prioritize paths with fewer hops if multiple paths have the same maximum achievable bandwidth

## Solution Approach

The solution uses a modified version of Dijkstra's algorithm with the following considerations:

1. We prioritize paths with higher bandwidth
2. For paths with equal bandwidth, we prioritize paths with fewer hops
3. For paths with equal bandwidth and hops, we prioritize paths with lower latency

The algorithm uses a priority queue to explore the network, maintaining the best paths found so far.

An alternative binary search approach is also provided, which searches for the optimal bandwidth value and then checks if a path exists with that bandwidth.

## Implementation Details

- `NetworkRouting.java`: Contains the main algorithm implementation
- `findOptimalPath`: Primary method that returns the maximum achievable bandwidth, or -1 if no valid path exists
- Custom classes for representing edges and paths

## Time Complexity

The time complexity is O(E log N), where E is the number of edges and N is the number of nodes in the network.

## Space Complexity

The space complexity is O(N + E) for storing the graph and the priority queue.