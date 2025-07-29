# Social Rank

This module implements a ranking algorithm for users in a decentralized social network.

## Overview

The algorithm ranks users based on their influence in a network, where influence is determined by:

1. The user's PageRank score - a measure of global importance based on the network structure
2. The number of direct followers - rewarding users with many immediate connections
3. The user's proximity to the starting node - indicating relevance to the initial user

## Algorithm Design

### Network Exploration
- Uses a breadth-first search (BFS) approach to explore the network from a starting node
- Respects the `max_hops` and `max_users` constraints to limit resource usage
- Handles missing data and cycles gracefully

### Influence Score Calculation
- Utilizes a modified PageRank algorithm (70% of the final score)
- Incorporates direct follower count as a measure of immediate reach (30% of the final score)
- Normalizes scores to provide meaningful comparisons between users

### Efficiency Considerations
- Avoids redundant network queries by tracking visited users
- Optimizes memory usage by only storing necessary information
- Uses efficient data structures (deque for BFS, defaultdict for graph representation)

## Justification of Influence Metric

The influence score combines:

1. **PageRank** - A well-established algorithm for determining the importance of nodes in a network, accounting for the recursive nature of influence (i.e., being followed by influential users makes you more influential)

2. **Direct Follower Count** - Ensures users with many direct followers are appropriately recognized, as they have immediate reach regardless of the influence of those followers

This hybrid approach balances global network structure with direct reach, providing a more nuanced measure of influence than either metric alone would offer.

## Limitations

- Accuracy is limited by the scope of exploration (max_hops and max_users)
- The snapshot nature means it can't account for rapidly changing network dynamics
- The algorithm prioritizes exploration breadth over depth, which may not capture deep influence chains

## Usage
