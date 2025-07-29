## Project Name

**Intergalactic Communication Network Design**

## Question Description

You are tasked with designing a robust and efficient communication network for a newly formed intergalactic alliance. The alliance consists of `N` planets, each represented by a unique integer ID from `0` to `N-1`. The cost of establishing a direct communication link (cable) between any two planets depends on their distance and the specific communication technology available.

You are given the following information:

1.  **Planet Coordinates:** A list of `N` tuples `(x, y, z)` representing the 3D coordinates of each planet in space.

2.  **Technology Matrix:** An `N x N` matrix `tech_matrix` where `tech_matrix[i][j]` represents the cost multiplier for establishing a direct communication link between planet `i` and planet `j`. This multiplier accounts for the compatibility and efficiency of communication technology between the planets. The `tech_matrix` is symmetric (i.e., `tech_matrix[i][j] == tech_matrix[j][i]`) and `tech_matrix[i][i] = 0`.

3.  **Minimum Spanning Tree Requirement:**  The network must be connected, meaning there must be a path for communication between any two planets in the alliance. To minimize cost and ensure basic connectivity, the core network must form a Minimum Spanning Tree (MST).

4.  **Critical Planet Redundancy:** A subset of planets are designated as "critical planets". These planets are crucial for the alliance's operations. To ensure resilience, each critical planet must have at least `K` direct communication links (cables) to *other* planets. These links may or may not be part of the MST.

5.  **Cost Calculation:** The cost of a direct link between planets `i` and `j` is calculated as:  `distance(i, j) * tech_matrix[i][j]`, where `distance(i, j)` is the Euclidean distance between the planets `i` and `j` in 3D space. The total cost of the network is the sum of the costs of all direct communication links.

Your task is to:

1.  Find the Minimum Spanning Tree (MST) connecting all `N` planets.
2.  Add additional direct communication links (cables) to the network, if necessary, to ensure that each critical planet has at least `K` direct communication links to other planets.
3.  Minimize the total cost of the network (MST cost + cost of additional links).

**Input:**

*   `N`: The number of planets (integer).
*   `planet_coordinates`: A list of `N` tuples `(x, y, z)` representing the coordinates of each planet.
*   `tech_matrix`: An `N x N` matrix representing the technology cost multipliers between planets.
*   `critical_planets`: A list of integers representing the IDs of the critical planets.
*   `K`: The minimum number of direct communication links required for each critical planet (integer).

**Output:**

A single floating-point number representing the minimum total cost of the communication network satisfying the given constraints.  The answer should be accurate to at least 6 decimal places.

**Constraints:**

*   `1 <= N <= 500`
*   `0 <= x, y, z <= 1000` (Coordinates are integers)
*   `0 <= tech_matrix[i][j] <= 10` (Technology multipliers are floating-point numbers)
*   `0 <= K <= N - 1`
*   The number of critical planets is between 0 and N (inclusive).
*   Planet IDs in `critical_planets` are valid (i.e., between 0 and N-1).
*   It is guaranteed that a solution always exists.

**Scoring:**

Your solution will be evaluated based on its correctness and efficiency.  Submissions that time out or produce incorrect results will receive a lower score.  Partial scores may be awarded for solutions that correctly handle some test cases.

**Example:**

Let's say the optimal MST cost is 100.0, and adding the necessary links for critical planets adds an additional cost of 20.0. Then the output should be 120.0.

**Hints:**

*   Consider using efficient algorithms for finding the MST (e.g., Prim's or Kruskal's algorithm).
*   Think about how to efficiently add the necessary links for critical planets while minimizing cost. A greedy approach might be helpful, but consider different strategies for link selection.
*   Pay attention to floating-point precision when calculating distances and costs.
*   The problem requires a combination of graph algorithms and optimization techniques.
