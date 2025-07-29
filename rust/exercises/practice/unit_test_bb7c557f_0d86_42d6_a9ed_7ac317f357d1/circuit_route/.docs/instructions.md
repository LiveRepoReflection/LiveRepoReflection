### Project Name

`OptimalCircuitRouting`

### Question Description

You are tasked with designing an efficient routing algorithm for electrical signals within a complex integrated circuit. The circuit can be represented as a weighted undirected graph. Nodes represent components, and edges represent potential connections between components. The weight of an edge represents the delay associated with sending a signal across that connection.

You are given:

*   `n`: The number of components in the circuit, numbered from `0` to `n-1`.
*   `edges`: A vector of tuples, where each tuple `(u, v, w)` represents an undirected edge between component `u` and component `v` with a delay (weight) of `w`.
*   `start_components`: A vector of integers representing the starting components where signals originate.
*   `end_components`: A vector of integers representing the target components where signals need to arrive.
*   `max_allowed_delay`: An integer representing the maximum allowed delay for a signal to travel from any starting component to any target component.

Your objective is to design an algorithm that finds a minimum cost Steiner Tree that connects at least *one* start component to *one* end component without violating delay constraints. The Steiner tree is a tree that connects all the nodes of a given set (start and end components in this case) through a minimal number of intermediate nodes.

**Cost Function:**

The cost of a connection from a starting component to a target component is defined by the following:

*   If any valid path exists between a starting component and a target component with a total delay less than or equal to `max_allowed_delay`, the cost is the minimum total delay of *any* such path.
*   If no path exists between any starting component and any target component that satisfies the delay constraint, the cost is `-1`.

**Constraints:**

1.  The graph can be very large (up to 10<sup>5</sup> nodes and edges).
2.  The edge weights (delays) are non-negative integers.
3.  You must minimize the total delay of the path used to connect start and end components.
4.  You do not need to connect *all* start components to *all* end components. Connecting *at least one* start component to *at least one* end component while minimizing the cost is sufficient.
5.  Your solution should be efficient enough to handle large graphs within a reasonable time limit.
6.  The number of start/end components could be very large or very small.
7.  The graph may not be fully connected.
8.  The input graph is an undirected graph, make sure you consider both directions for edges.

**Input:**

*   `n: usize` (number of components)
*   `edges: Vec<(usize, usize, u32)>` (edges represented as (u, v, weight))
*   `start_components: Vec<usize>` (starting components)
*   `end_components: Vec<usize>` (target components)
*   `max_allowed_delay: u32` (maximum allowed delay)

**Output:**

*   `i64` (The minimum cost (minimum delay) to connect any start component to any end component, or `-1` if no such connection exists within the delay constraint).  Return -1 if no start or end components are present.
