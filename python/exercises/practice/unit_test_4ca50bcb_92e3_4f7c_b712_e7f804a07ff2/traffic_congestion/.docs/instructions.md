## Project Name

```
TrafficCongestion
```

## Question Description

You are tasked with simulating and optimizing traffic flow in a simplified city. The city is represented as a directed graph where nodes represent intersections and edges represent one-way streets. Each street has a capacity, representing the maximum number of vehicles that can travel on it per unit time.

Initially, each intersection has a certain number of vehicles waiting to enter the road network. Your goal is to devise a traffic routing strategy that minimizes the maximum congestion experienced on any street in the city during a given simulation period. Congestion on a street is defined as the number of vehicles using the street at any given time, exceeding the capacity of the street.

Specifically, you are given:

*   `n`: The number of intersections in the city, numbered from 0 to `n-1`.
*   `edges`: A list of tuples `(u, v, capacity)`, where `u` and `v` are the starting and ending intersections of a street, and `capacity` is the street's capacity.
*   `initial_vehicles`: A list of integers where `initial_vehicles[i]` represents the number of vehicles initially present at intersection `i`.
*   `time_steps`: The number of time steps to simulate the traffic flow.
*   `routing_function`: A function that you need to implement. It takes the current state of the city (vehicles at each intersection, edge capacities) and returns a dictionary indicating the number of vehicles to route along each edge for the *next* time step. The keys of the dictionary are tuples `(u, v)` representing the edge, and the values are non-negative integers indicating the number of vehicles to route along that edge.

Your task is to implement the `routing_function` to minimize the maximum congestion observed on any street throughout the entire simulation period.

## Requirements

*   The routing function must be deterministic. Given the same input state, it must produce the same routing decisions.
*   The routing function must be efficient. It should not take an excessive amount of time to compute the routing decisions for each time step. (Approximate runtime: ~20s for 100 time steps on testcase.)
*   Vehicles can only move along the specified edges. It is not allowed to create new paths or teleport vehicles.
*   The total number of vehicles entering an intersection (excluding initial vehicles) in each time step must be less than or equal to the total number of vehicles available at the origin intersections. No vehicles should be "created" or "destroyed."
*   The `routing_function` should aim to distribute vehicles in a way that minimizes the maximum congestion across all streets throughout the simulation.
*   The congestion is the number of vehicles using the street at any given time **exceeding** the capacity of the street. A street with 10 vehicles using it and capacity of 7 has congestion of 3.
*   All vehicles routed in one time step successfully reach their destination before the next time step.

## Constraints

*   `1 <= n <= 100` (Number of intersections)
*   `1 <= len(edges) <= 200` (Number of streets)
*   `1 <= capacity <= 50` for each street
*   `0 <= initial_vehicles[i] <= 100` for each intersection
*   `1 <= time_steps <= 100`

## Input

The input to your `routing_function` consists of:

*   `n`: An integer representing the number of intersections.
*   `edges`: A list of tuples `(u, v, capacity)` representing the streets and their capacities.
*   `current_vehicles`: A list of integers where `current_vehicles[i]` represents the number of vehicles currently at intersection `i`.
*   `time_step`: The current time step (starting from 0).

## Output

The `routing_function` must return a dictionary where the keys are tuples `(u, v)` representing the edge, and the values are non-negative integers indicating the number of vehicles to route along that edge during the next time step.

## Evaluation

Your solution will be evaluated based on the maximum congestion observed on any street across all time steps in several test cases. The lower the maximum congestion, the better your solution. The solution that minimizes the maximum congestion will be considered the best.

## Example

Let's say you have 3 intersections and the following graph:

*   `n = 3`
*   `edges = [(0, 1, 10), (0, 2, 5), (1, 2, 7)]`
*   `initial_vehicles = [20, 5, 0]`
*   `time_steps = 5`

Your `routing_function` would be called repeatedly with updated `current_vehicles` and `time_step`.

For the first call (time_step = 0, current_vehicles = initial_vehicles):

A possible (but not necessarily optimal) output from your `routing_function` could be:

`{(0, 1): 10, (0, 2): 5}`

This means that 10 vehicles will be routed from intersection 0 to intersection 1, and 5 vehicles will be routed from intersection 0 to intersection 2. The remaining vehicles at node 0 will wait.
