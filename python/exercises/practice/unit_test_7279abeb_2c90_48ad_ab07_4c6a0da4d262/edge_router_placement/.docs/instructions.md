## Problem: Optimal Edge Router Placement for a Distributed CDN

### Question Description:

You are designing the edge router network for a content delivery network (CDN) that serves video streams to users across a large geographical area. The CDN consists of a set of origin servers where the video content is stored, and a set of edge routers strategically placed to cache and deliver the content to end-users with low latency. Your task is to determine the optimal locations for these edge routers.

**Input:**

1.  **User Locations:** A list of `N` user locations, represented as (latitude, longitude) coordinates. These are the locations where video streams are being requested from.

2.  **Potential Router Locations:** A list of `M` potential locations for placing edge routers, also represented as (latitude, longitude) coordinates. You can only place routers at these locations.

3.  **Number of Routers to Place:** An integer `K`, representing the maximum number of edge routers you can deploy. `K` will always be less than or equal to `M`.

4.  **Maximum Latency:** A maximum allowable latency `L` (in milliseconds) between a user and the nearest edge router serving their requests. If the latency from any user to their nearest edge router exceeds `L`, the solution is invalid. You can calculate latency as the great-circle distance between two geo-coordinates, multiplied by a constant propagation delay factor (defined below).

5.  **Router Capacity:** Each edge router has a limited capacity `C`, representing the maximum number of concurrent users it can effectively serve while maintaining acceptable performance.

6.  **Propagation Delay Factor:** A constant `P` (in milliseconds per kilometer), representing the latency introduced per unit of distance. Latency = Distance * P, where Distance is the great-circle distance between user and edge router.

**Output:**

A list of `K'` (where `K' <= K`) indices indicating the selected potential router locations.

**Constraints and Requirements:**

1.  **Coverage:** Every user must be within the maximum latency `L` of their nearest edge router.

2.  **Capacity:** No edge router can exceed its capacity `C`. The number of users assigned to each edge router must be less than or equal to `C`.

3.  **Optimization Goal:** Minimize the *total deployment cost* of the edge routers, while meeting coverage and capacity constraints. Assume each edge router has a fixed cost of `R` (router cost), and prioritize using fewer routers when possible. If multiple solutions exist with the same number of routers, choose the solution that minimizes the total latency.

4.  **Tie-Breaking:** If multiple solutions have the same number of routers and nearly identical total latencies (within a tiny tolerance), any one of those solutions is considered valid.

5.  **Scalability:** The solution must be efficient enough to handle a large number of users (`N <= 10,000`), a reasonable number of potential router locations (`M <= 500`), and a limited number of routers (`K <= 50`).

6.  **Great-Circle Distance Calculation:** You are required to use the Haversine formula for calculating the great-circle distance between two geographic coordinates, to ensure accuracy.

7.  **Edge Cases:** Handle cases where no solution is possible within the given constraints (return an empty list). Also handle edge cases like when `K` is 0, 1, or equal to `M`.

8.  **Efficiency:** Aim for the most efficient solution possible, considering the time complexity of your algorithm. Suboptimal, brute-force approaches will likely time out on larger test cases.

**Example:**

Let's say you have 5 users, 3 potential router locations, can place up to 2 routers, have a max latency of 100ms, a router capacity of 3 users, a propagation delay factor of 0.2 ms/km, and each router costs 1000. Your solution should return the optimal 2 (or fewer) router locations that cover all 5 users within the latency constraint, without exceeding router capacity, and minimizing cost (number of routers * router cost).
