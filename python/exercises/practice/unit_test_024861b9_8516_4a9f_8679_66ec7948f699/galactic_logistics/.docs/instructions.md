## Question: Optimizing Inter-Galaxy Logistics Network

**Description:**

You are tasked with optimizing the inter-galaxy logistics network for a vast trading conglomerate, "Cosmic Commerce Inc." The network consists of planets connected by wormholes, each wormhole having a certain traversal time and associated cost (in Galactic Credits, GC).

Each planet has a production capacity for a specific set of goods and a demand for another set of goods. Your goal is to determine the most cost-effective way to transport goods between planets to satisfy demands, respecting production capacities and wormhole constraints.

**More specifically:**

1.  **Network Representation:** The inter-galaxy network is represented as a weighted, directed graph.
    *   Nodes are planets, labeled with unique integer IDs (1 to N, where N is the total number of planets).
    *   Edges are wormholes connecting planets. Each wormhole has:
        *   A source planet (start node).
        *   A destination planet (end node).
        *   Traversal time (in Galactic Standard Time Units, GSTU).
        *   Traversal cost (in Galactic Credits, GC).
2.  **Goods:** There are 'M' different types of goods, also represented by unique integer IDs (1 to M).
3.  **Planetary Data:** For each planet, you are given:
    *   Production: A list of `(good_ID, quantity)` pairs representing the amount of each good produced on that planet.
    *   Demand: A list of `(good_ID, quantity)` pairs representing the amount of each good needed on that planet.
4.  **Transport Constraints:**
    *   Goods can only be transported through wormholes.
    *   The total quantity of each good shipped *from* a planet cannot exceed its production capacity for that good.
    *   The total quantity of each good shipped *to* a planet must satisfy its demand for that good.
    *   Wormhole capacity is *unlimited* (i.e., you can ship any quantity of goods through a wormhole).
5.  **Objective:** Minimize the *total cost* (in GC) of transporting goods across the network to satisfy all demands, while respecting all production capacities.
6.  **Time Constraint:** All shipments must arrive at their destination planet within a specified time window, measured in GSTU. This time window is defined as `[T_min, T_max]` where `T_min` is the shortest possible time to move all goods and `T_max` is the upper bound for the time window. Any shipment that takes longer than `T_max` is considered invalid.
7.  **Multiple valid solutions** Many valid solutions exist, but the focus is on finding the *minimum cost* solution.

**Input:**

The input will be provided as follows:

*   `N`: The number of planets.
*   `M`: The number of goods.
*   `wormholes`: A list of tuples, where each tuple represents a wormhole: `(source_planet_ID, destination_planet_ID, traversal_time, traversal_cost)`
*   `planet_data`: A list of dictionaries, one for each planet (in order of planet ID 1 to N). Each dictionary has two keys:
    *   `"production"`: A list of `(good_ID, quantity)` tuples.
    *   `"demand"`: A list of `(good_ID, quantity)` tuples.
*   `T_max`: The upper bound for the time window.

**Output:**

Return the minimum total cost (in GC) required to satisfy all demands, respecting production capacities and wormhole constraints, and within the time constraint. If it's impossible to satisfy all demands, return `-1`.

**Constraints:**

*   1 <= N <= 50
*   1 <= M <= 20
*   0 <= traversal\_time <= 100
*   0 <= traversal\_cost <= 1000
*   0 <= quantity <= 1000
*   T\_max <= 100000
*   The graph may not be fully connected.
*   There may be multiple wormholes between the same two planets.
*   A planet may produce and demand the same good.

**Example:**

Let's consider a simplified scenario with two planets (N=2) and one good (M=1):

*   **Wormholes:** `[(1, 2, 10, 50), (2, 1, 15, 75)]` (Planet 1 to Planet 2 costs 50 GC and takes 10 GSTU, Planet 2 to Planet 1 costs 75 GC and takes 15 GSTU)
*   **Planet Data:**
    *   Planet 1: `production=[(1, 100)], demand=[(1, 20)]` (Produces 100 of good 1, demands 20 of good 1)
    *   Planet 2: `production=[(1, 30)], demand=[(1, 110)]` (Produces 30 of good 1, demands 110 of good 1)
*   `T_max = 1000`

In this case, Planet 2 needs 80 more units of good 1. Planet 1 has enough to satisfy this demand. Shipping 80 units of good 1 from Planet 1 to Planet 2 via the first wormhole would cost 80 * 50 = 4000 GC and take 10 GSTU.

**Challenge:**

This problem requires a combination of graph algorithms (shortest path, flow networks), optimization techniques (linear programming, minimum cost flow), and careful handling of constraints. Finding the optimal solution requires efficient algorithms and data structures, making it a difficult and challenging problem. Consider the scalability of your solution when dealing with a larger number of planets, goods, and wormholes. Remember to optimize for both time and cost. Good luck!
