# Celestial Paths

## Overview

The Celestial Cartographers problem involves calculating the probability of being able to travel between space stations within a given time limit, where the traversal times of wormholes connecting the stations follow uniform distributions.

## Implementation Details

This solution uses Monte Carlo simulation to estimate the probability:

1. For each simulation, we randomly generate traversal times for each wormhole according to their uniform distribution.
2. We then use Dijkstra's algorithm to find the shortest path with these generated times.
3. If the shortest path is within the allowed time, we count it as a success.
4. After running many simulations, we compute the probability as (number of successful simulations) / (total number of simulations).

The Monte Carlo approach is used because the problem involves continuous probability distributions, making it difficult to compute the exact probability analytically. By running a large number of simulations (100,000 in this implementation), we can get a reasonable approximation of the true probability.

## Time Complexity

- Monte Carlo Simulation: O(S * (M + N log N))
  - Where S is the number of samples, M is the number of wormholes, and N is the number of space stations
  - Each Dijkstra's run is O(M + N log N)

## Space Complexity

- O(N + M) for storing the graph and distance information

## Trade-offs

The accuracy of our probability estimate depends on the number of Monte Carlo simulations. More simulations yield more accurate results but take longer to compute. 

An alternate approach could be to use analytical methods for certain special cases or to use more advanced numerical integration techniques, but the Monte Carlo approach provides a good balance between accuracy and implementation simplicity.