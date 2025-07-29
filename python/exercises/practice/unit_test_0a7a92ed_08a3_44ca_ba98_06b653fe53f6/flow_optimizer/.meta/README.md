# Multi-Commodity Flow Optimizer

This package implements a solution to the multi-commodity flow optimization problem with dynamic edge costs. It uses an advanced variation of the Frank-Wolfe algorithm tailored specifically for network flow problems.

## Problem Description

The multi-commodity flow problem involves optimizing the flow of multiple commodities through a network, where each commodity has a source, destination, and demand. The challenge is complicated by the fact that the cost of using each edge depends on the total flow currently using that edge.

## Features

- Supports directed graphs with piecewise linear cost functions on edges
- Optimizes flow for multiple commodities simultaneously
- Handles flow conservation constraints at all nodes
- Ensures demand satisfaction for all commodities
- Minimizes the total cost of transporting all commodities

## Usage
