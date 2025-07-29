# Network Reconstruction

This is a solution for the Network Reconstruction problem, which involves reconstructing a network topology from incomplete network traffic logs.

## Problem Overview

Given a set of servers (numbered 1 to N) and a log of network traffic between them, the goal is to reconstruct the underlying network topology. The log entries represent valid connections, but missing entries don't necessarily mean servers aren't connected. The reconstruction should minimize the average path length between all pairs of servers.

## Solution Approach

The solution follows these steps:

1. **Validation**: Ensure the input meets the requirements (at least 2 servers, valid server IDs in logs).

2. **Initial Network Construction**: Create an adjacency list representing the network with the known connections from the log.

3. **Connected Components**: Ensure the network is fully connected by adding edges between disconnected components if necessary.

4. **Network Optimization**: Add additional edges to minimize the average path length:
   - Compute all-pairs shortest paths using the Floyd-Warshall algorithm
   - Identify potential edges that would most reduce the average path length
   - Add edges strategically, prioritizing those with the most impact

5. **Return**: Return the optimized network topology as an adjacency list.

## Time and Space Complexity

- **Time Complexity**: O(N³) where N is the number of servers. The Floyd-Warshall algorithm dominates with O(N³).
- **Space Complexity**: O(N²) for storing the distance matrix and adjacency list.

## Trade-offs and Scaling Considerations

- **Trade-offs**: 
  - The solution prioritizes optimality over computational efficiency.
  - For very large networks, the O(N³) time complexity could become problematic.
  
- **Scaling to N = 10000**:
  - The current approach would be too slow for N = 10000.
  - For such large networks, approximation algorithms would be more practical:
    - Greedy algorithms for adding edges
    - Sampling-based approaches for estimating path lengths
    - Hierarchical clustering to identify regions where edges would be most beneficial
    - Distributed computation for parallelization