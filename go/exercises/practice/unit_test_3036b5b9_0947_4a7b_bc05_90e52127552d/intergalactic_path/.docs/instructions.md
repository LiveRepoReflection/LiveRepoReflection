Okay, here's a challenging Go coding problem designed to test advanced data structures, algorithms, and optimization techniques.

## Problem:  Intergalactic Shortest Path Network

**Description:**

The Intergalactic Federation has established a network of stargates to facilitate rapid travel between planets.  Each planet is identified by a unique integer ID.  The stargates are not perfectly reliable, and their connection costs can fluctuate based on various intergalactic factors.

You are given a dynamic network of planets and stargates. The network evolves over time through a series of events. Your task is to efficiently answer shortest path queries between any two planets in the network *at the current state* after each event.

**Data Structures:**

*   **Planet:** A planet is represented by a unique integer ID.
*   **Stargate:** A stargate connects two planets. Each stargate has a cost associated with its usage, which can change over time.  Multiple stargates can exist between the same pair of planets, each with potentially different costs.
*   **Network:** The network consists of a set of planets and stargates.

**Events:**

The following events can occur, modifying the network:

1.  **`AddPlanet(planetID int)`:**  Adds a new planet with the given `planetID` to the network.  If a planet with the same ID already exists, the operation should be ignored.

2.  **`RemovePlanet(planetID int)`:** Removes the planet with the given `planetID` from the network. All stargates connected to this planet are also removed. If a planet with the given ID does not exist, the operation should be ignored.

3.  **`AddStargate(planet1 int, planet2 int, cost int)`:** Adds a new stargate between `planet1` and `planet2` with the given `cost`. Planets `planet1` and `planet2` must already exist in the network. The stargate is undirected (travel is possible in both directions with the same cost). If a stargate already exists between these two planets with the same cost, the operation should be ignored. If a stargate already exists between these two planets but with a different cost, a new stargate will need to be added alongside it.

4.  **`RemoveStargate(planet1 int, planet2 int, cost int)`:** Removes a stargate between `planet1` and `planet2` with the given `cost`. If no such stargate exists, the operation should be ignored. If multiple stargates exist between the same planets with the same cost, only one of them should be removed.

5.  **`UpdateStargateCost(planet1 int, planet2 int, oldCost int, newCost int)`:** Updates the cost of a stargate between `planet1` and `planet2` from `oldCost` to `newCost`. If no such stargate exists with the `oldCost`, the operation should be ignored. If multiple such stargates exist, only the first encountered should be updated.

6.  **`QueryShortestPath(planet1 int, planet2 int)`:**  Returns the minimum cost to travel between `planet1` and `planet2` using the existing stargates. If no path exists, return `-1`. Planets `planet1` and `planet2` must already exist in the network.

**Constraints:**

*   The number of planets and stargates can be very large (up to 10<sup>5</sup>).
*   The number of events (including queries) can also be very large (up to 10<sup>5</sup>).
*   Planet IDs are positive integers within the range [1, 10<sup>9</sup>].
*   Stargate costs are positive integers within the range [1, 10<sup>6</sup>].
*   The solution must efficiently handle a sequence of events and queries.  Naive solutions that recalculate the shortest path for every query will likely time out.
*   Memory usage should also be considered.

**Requirements:**

*   Implement the data structures and event handling logic in Go.
*   The `QueryShortestPath` function must have a time complexity significantly better than O(V\*E) where V is the number of vertices and E is the number of edges, ideally close to Dijkstra's algorithm with a good heap implementation. Using a precomputed matrix would not be feasible, and therefore must be dynamically calculated.
*   The solution should handle edge cases gracefully (e.g., invalid planet IDs, non-existent stargates).

**Judging Criteria:**

*   Correctness (all test cases must pass).
*   Efficiency (time and memory usage).  Solutions that are too slow or consume too much memory will be rejected.
*   Code clarity and organization.

This problem requires careful consideration of data structure choices, algorithm selection, and optimization techniques to achieve acceptable performance. Good luck!
