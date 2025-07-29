# Decentralized Social Network Analysis - k-hop Reachability

This project provides an implementation of a k-hop reachability algorithm for a decentralized social network. The algorithm determines all users reachable within k hops from a given starting user.

## Implementation Details

Two implementations are provided:

1. `social_reach.cpp`: The primary implementation using a queue-based BFS approach with caching.
2. `social_reach_optimized.cpp`: An optimized implementation that uses a layer-by-layer BFS approach to minimize API calls.

Both implementations efficiently handle:
- Decentralized network data access
- Cycle detection
- Minimizing API calls
- Proper k-hop constraint enforcement

## Algorithm Complexity

- Time Complexity: O(V + E) where V is the number of users and E is the number of connections, bounded by the k-hop constraint.
- Space Complexity: O(V) for storing visited users and the result set.
- API Calls: Optimized to make exactly one API call per reachable user within k hops.

## Usage
