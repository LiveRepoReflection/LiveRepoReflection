# Traffic Light Control Optimization

This Go module implements an optimization algorithm for controlling traffic lights in a road network.

## Problem

The problem involves optimizing traffic light schedules across N intersections connected by M bidirectional roads.
Each road has an associated travel time, and there are K vehicle trips that need to traverse the road network.
The goal is to minimize the average travel time for all trips.

## Approach

The solution uses a combination of:

1. **Simulated Annealing**: A probabilistic technique for approximating the global optimum
2. **Local Search**: For fine-tuning the solution
3. **Dijkstra's Algorithm**: For finding shortest paths with traffic light timing constraints
4. **Traffic Density Analysis**: To focus optimization on the most heavily used intersections

## Implementation

The main function `OptimalTrafficLightControl` takes the following inputs:
- Number of intersections
- Number of roads with their travel times
- Vehicle trips (start and end points)
- Traffic light cycle length

It returns an optimal schedule of green light durations for each intersection.

## Optimization Techniques

- Intelligent exploration of the solution space using simulated annealing with a cooling schedule
- Prioritization of high-traffic intersections using traffic density analysis
- Path-finding algorithms that account for traffic light waiting times
- Local search to further refine promising solutions

## Performance Considerations

The implementation balances computation time with solution quality:
- Uses efficient data structures (priority queues)
- Focuses optimization effort on critical intersections
- Implements early termination conditions for search algorithms
- Uses heuristics to guide the search process

## Usage
