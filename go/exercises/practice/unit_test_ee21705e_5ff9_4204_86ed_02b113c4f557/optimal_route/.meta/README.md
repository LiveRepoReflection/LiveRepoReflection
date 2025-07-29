# Optimal Route Planner

This solution implements an optimal route planning service for a delivery company operating in a large city. The city's road network is represented as a directed graph, and each truck has specific delivery locations to visit in a given order.

## Implementation Details

### Main Algorithm

1. **Graph Representation**: The city's road network is represented as an adjacency list where each node (intersection) has a list of outgoing edges (roads) with their respective travel times and toll costs.

2. **Route Planning**: For each truck, the algorithm:
   - Processes delivery locations in the specified order
   - Uses Dijkstra's algorithm to find the optimal path between consecutive locations
   - Maintains a running total of travel time and toll costs
   - Checks if the total travel time exceeds the maximum allowed time

3. **Path Finding**: Dijkstra's algorithm is used to find the shortest path between two points, considering both travel time and toll costs weighted by the `timeTollWeight` factor.

### Time Complexity

- Building the graph: O(E) where E is the number of edges
- For each truck with k delivery locations:
  - Running Dijkstra's algorithm k times: O(k * (E + V log V)) where V is the number of vertices
- Overall: O(T * k * (E + V log V)) where T is the number of trucks

### Space Complexity

- Graph storage: O(V + E)
- Path storage for each truck: O(V)
- Overall: O(V + E + T * V)

## Edge Cases Handled

1. Unreachable destinations
2. Exceeding maximum travel time
3. Empty delivery location lists
4. Start and end points being the same
5. Disconnected graphs