## The Algorithmic Art Gallery

**Problem Description:**

You are hired as a software engineer for "Algorithmic Art Gallery", a revolutionary art gallery showcasing computer-generated art pieces. The gallery aims to maximize its profit by strategically placing security cameras to protect the artworks.

The gallery's layout can be represented as a directed graph. Each node in the graph represents an intersection or a room, and each directed edge represents a corridor connecting two locations. Each location (node) in the gallery contains a certain number of artworks, each with a specific value. The gallery wants to protect these artworks from theft.

To protect the gallery, you need to strategically place security cameras. Each camera can be placed at a location (node). A camera placed at location *i* protects all artworks in that location and all artworks in any location reachable from *i* following the directed edges.

Given the graph representing the gallery layout, the number of artworks and their values at each location, and the cost of placing a camera at each location, your task is to determine the minimum cost required to protect all artworks in the gallery.

**Constraints and Requirements:**

1.  **Graph Representation:** The gallery layout is provided as a dictionary where keys are locations (nodes represented by integers) and values are lists of integers representing the locations reachable from that location through a directed edge. For example, `{0: [1, 2], 1: [3], 2: [3]}` means there are corridors from location 0 to 1 and 2, from 1 to 3, and from 2 to 3.
2.  **Artwork Values:** The number of artworks and their values at each location are provided as a dictionary where keys are locations and values are lists of artwork values. For example, `{0: [10, 20], 1: [30], 2: [40]}` means location 0 has two artworks with values 10 and 20, location 1 has one artwork with value 30, and location 2 has one artwork with value 40.
3.  **Camera Costs:** The cost of placing a camera at each location is provided as a dictionary where keys are locations and values are the cost (integer) of placing a camera at that location.
4.  **Complete Protection:** All artworks in the gallery *must* be protected.
5.  **Minimization:** You must find the *minimum* total cost to protect all artworks.
6.  **Graph Size:** The gallery can have up to 1000 locations (nodes).
7.  **Artwork Value:** Artwork values are positive integers.
8.  **Camera Costs:** Camera costs are positive integers.
9.  **Optimization:** A naive brute-force solution will not pass the time limit. Your solution needs to be efficient, potentially using dynamic programming or graph algorithms.
10. **Edge Cases:** Handle cases where the graph is disconnected, contains cycles, or has locations with no artworks.
11. **Memory Limits:** The memory usage of your solution should be reasonable, consider not storing the entire graph's transitive closure in memory.

**Input:**

*   `graph`: A dictionary representing the directed graph of the gallery.
*   `artwork_values`: A dictionary representing the artwork values at each location.
*   `camera_costs`: A dictionary representing the cost of placing a camera at each location.

**Output:**

*   An integer representing the minimum cost to protect all artworks in the gallery.

Good luck!
