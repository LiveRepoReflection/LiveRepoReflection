# Package Delivery Optimization

This Go package solves the package delivery optimization problem. It finds the minimum cost to deliver packages through a network of hubs, respecting capacity constraints and optimizing for total cost.

## Problem Description

The problem involves optimizing package delivery for a logistics company. The network of hubs is represented as a weighted, directed graph, where nodes represent delivery hubs and edges represent transportation routes between hubs.

Each hub has:
- A unique ID
- A capacity limit (maximum number of packages it can handle)
- A processing cost per package

Each route has:
- A source hub ID
- A destination hub ID
- A transportation cost per package

Packages have:
- A unique ID
- A source hub ID
- A destination hub ID

The goal is to determine the optimal routing plan for a set of packages to minimize the total cost, considering both transportation costs and hub processing costs, while respecting hub capacities.

## Solution Approach

The solution uses Dijkstra's algorithm to find the shortest (least cost) path for each package from its source to destination. Key considerations in the implementation:

1. Packages at the same source going to the same destination are grouped for efficiency
2. Hub capacity constraints are checked
3. Both transportation costs and processing costs at each hub are included in the total
4. Edge cases are handled, including disconnected graphs and packages already at their destination

## Usage
