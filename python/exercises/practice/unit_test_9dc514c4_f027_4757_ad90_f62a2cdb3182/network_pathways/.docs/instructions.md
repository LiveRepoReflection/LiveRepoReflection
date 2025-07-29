## Project Name

```
NetworkPathways
```

## Question Description

You are tasked with simulating the spread of a signal through a complex communication network. This network is represented as a directed, weighted graph where nodes represent servers and edges represent communication links. Each link has a latency (weight) associated with it, representing the time it takes for a signal to travel from one server to another.

However, this network has a crucial vulnerability: certain servers are susceptible to being compromised by malicious actors. If a server is compromised, it begins to inject noise into the signal it transmits, effectively corrupting any message passing through it. This noise degrades the signal quality, quantified as a "corruption level".

Your task is to design an algorithm to determine the *minimum corruption level* a signal will experience when transmitted from a source server to a destination server, considering potential compromises along the path.

**Specific Requirements:**

1.  **Network Representation:** The network is given as a list of edges, where each edge is a tuple `(source, destination, latency)`. Node IDs are integers.
2.  **Compromised Servers:** A list of compromised server IDs is provided.
3.  **Signal Transmission:** A signal needs to be transmitted from a given `source` server to a given `destination` server.
4.  **Corruption Level:** The corruption level is calculated as follows:
    *   Each compromised server adds a corruption level equal to the *latency of the incoming link* through which the signal *first* reaches that compromised server.
    *   If a path avoids a compromised server entirely, that server contributes no corruption.
    *   If multiple paths exist, the optimal path is the one that minimizes the sum of the corruption levels *plus* the total latency of the path.
5.  **Optimization:** The network can be large (up to 10,000 nodes and 50,000 edges). Your solution must be computationally efficient to handle such networks within a reasonable time limit (e.g., a few seconds).
6.  **Edge Cases:**
    *   The network may not be fully connected. If no path exists between the source and destination, return -1.
    *   The graph can have cycles.
    *   The latency of edges is a non-negative integer.
    *   A server can be compromised or not.
7.  **Multiple Optimal Paths:** If multiple paths achieve the same minimal corruption level and total latency, any of those paths is considered a valid solution.

**Input:**

*   `edges`: A list of tuples, where each tuple represents a directed edge in the form `(source, destination, latency)`. Source, destination are integer node IDs, and latency is an integer.
*   `compromised`: A list of integer node IDs representing the compromised servers.
*   `source`: The integer node ID of the source server.
*   `destination`: The integer node ID of the destination server.

**Output:**

*   An integer representing the minimum corruption level plus the total latency of the optimal path from the source to the destination. Return -1 if no path exists.
