Okay, here's a challenging problem designed for a competitive programming environment, incorporating several elements to increase complexity and difficulty.

### Project Name

```
NetworkSim
```

### Question Description

You are tasked with building a simplified network simulator to analyze the spread of information within a complex communication network. The network consists of `N` nodes, numbered from `0` to `N-1`. These nodes are interconnected via bidirectional communication channels.

The network is represented by an adjacency list, `network`, where `network[i]` contains a list of node indices that node `i` can directly communicate with.  Note that the graph is undirected; if `j` is in `network[i]`, then `i` is also in `network[j]`.

At time `t=0`, a single node, `source`, becomes infected with a piece of information.  Whenever an infected node communicates with a non-infected node, the non-infected node becomes infected. Communication between two nodes takes exactly one unit of time. A node can only transmit the information once, to each of its direct neighbors. However, a node can receive the information from multiple nodes.

Your simulator must determine the *minimum* time required for the information to reach *all* nodes in the network. If it is impossible for the information to reach all nodes, return `-1`.

**Constraints:**

*   `1 <= N <= 100,000`
*   `0 <= source < N`
*   The `network` adjacency list will contain valid node indices.
*   The total number of connections will not exceed `200,000` (sum of lengths of all lists in `network` is <= 200,000).
*   Your solution must have a time complexity significantly better than O(N^2) to pass the test cases. Aim for O(N log N) or better. Memory usage should also be considered.

**Input:**

*   `N`: The number of nodes in the network (integer).
*   `network`: A list of lists representing the network's adjacency list (list of lists of integers).
*   `source`: The index of the node that initially has the information (integer).

**Output:**

*   The minimum time required for the information to reach all nodes, or `-1` if it's impossible (integer).
