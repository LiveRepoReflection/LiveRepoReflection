# Network Congestion Control & Path Optimization

This project implements a network congestion control and path optimization system capable of handling dynamic latency updates and finding optimal paths in a network while considering congestion.

## Problem Description

The system models a network as a weighted, directed graph where:
- Nodes represent network points (numbered 0 to N-1)
- Edges represent connections with associated latencies
- Latencies can be updated dynamically
- Path selection considers both latency and congestion

The system handles:
1. Dynamic latency updates
2. Finding k shortest paths with congestion awareness
3. Real-time path-finding queries

## Implementation

The solution uses a modified version of Yen's algorithm for k-shortest paths, combined with Dijkstra's algorithm for single shortest path finding. The key components include:

- Graph representation using adjacency lists
- Congestion tracking for each edge
- Congestion penalty calculation: `latency * (1 + congestion * C)`
- Priority queue-based path selection

## Usage
