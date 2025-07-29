## Question: Optimal Multi-Hop Wireless Routing

**Description:**

You are tasked with designing an efficient routing algorithm for a wireless sensor network (WSN). The WSN consists of `N` sensor nodes distributed in a 2D plane. Each sensor node has a limited transmission range `R`. A message needs to be delivered from a source node `S` to a destination node `D`.

Due to the limited transmission range, direct communication between `S` and `D` might not be possible. Therefore, the message may need to be relayed through intermediate nodes in a multi-hop fashion.

Each sensor node `i` has a battery level `B_i`. Relaying a message consumes energy, and the energy consumption is proportional to the distance of the transmission. Specifically, if node `i` transmits a message to node `j`, the energy consumed by node `i` is `C * dist(i, j)`, where `dist(i, j)` is the Euclidean distance between node `i` and node `j`, and `C` is a constant representing energy consumption per unit distance. A node cannot relay a message if its battery level is less than the energy consumption required for that transmission.

The goal is to find the **minimum-hop** path from the source node `S` to the destination node `D` such that the total energy consumption of the path is minimized *and* each node along the path has sufficient battery to relay the message to the next node. If multiple such paths exist, choose the path with the lowest total energy consumption. If no such path exists, return an empty list.

**Input:**

*   `N`: The number of sensor nodes (integer).
*   `nodes`: A list of tuples, where each tuple `(x, y, B)` represents a sensor node:
    *   `(x, y)`: The coordinates of the sensor node in the 2D plane (floats).
    *   `B`: The battery level of the sensor node (float).
*   `R`: The transmission range of each sensor node (float).
*   `S`: The index of the source node (integer, 0-indexed).
*   `D`: The index of the destination node (integer, 0-indexed).
*   `C`: The energy consumption constant per unit distance (float).

**Output:**

*   A list of integers representing the indices of the nodes in the optimal path from `S` to `D` (including `S` and `D`). Return an empty list if no path exists.

**Constraints:**

*   `1 <= N <= 1000`
*   `0 <= x, y <= 1000` for all nodes
*   `0 <= B <= 1000` for all nodes
*   `0 < R <= 500`
*   `0 <= S, D < N`
*   `0 < C <= 1`
*   `S != D`
*   The Euclidean distance between two points (x1, y1) and (x2, y2) is calculated as `sqrt((x1 - x2)^2 + (y1 - y2)^2)`.
*   Your solution must be reasonably efficient. Solutions with excessively high time complexity might not pass all test cases.
*   The code should handle edge cases where no path exists or where the source/destination node has insufficient battery to transmit to any neighbors.
*   Assume that the coordinates are distinct.

**Example:**

```python
N = 5
nodes = [(0, 0, 10), (10, 0, 5), (5, 5, 7), (10, 10, 8), (0, 10, 6)]
R = 12
S = 0
D = 3
C = 0.5

# Possible optimal path: [0, 2, 3]
# Other paths are possible but may be longer or require more energy.
# Note: The path [0, 4, 3] is also possible.
```
