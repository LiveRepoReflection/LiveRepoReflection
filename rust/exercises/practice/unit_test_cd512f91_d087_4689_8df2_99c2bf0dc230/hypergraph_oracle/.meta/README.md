# Hypergraph Connectivity Oracle

This crate implements a data structure for efficiently answering connectivity queries on a dynamic hypergraph.

## Features

- Initialize a hypergraph with a specified number of vertices
- Add hyperedges to connect vertices
- Query whether two vertices are connected by a path through the hypergraph
- Highly efficient implementation using Union-Find (Disjoint-Set) data structure with path compression and union by rank

## Implementation Details

The implementation uses a Union-Find (also known as Disjoint-Set) data structure with two key optimizations:

1. **Path Compression**: During find operations, all traversed nodes are made to point directly to the root, flattening the tree structure.
2. **Union by Rank**: When merging two sets, the tree with smaller rank is attached to the root of the tree with larger rank.

These optimizations result in nearly constant-time operations in practice, with a theoretical time complexity of O(α(n)) where α is the inverse Ackermann function, which grows extremely slowly (α(n) ≤ 5 for any practical value of n).

## Performance

- Constructor: O(n) time, where n is the number of vertices
- add_hyperedge: O(k * α(n)) amortized time, where k is the number of vertices in the hyperedge
- are_connected: O(α(n)) amortized time, effectively constant time in practice

## Example Usage
