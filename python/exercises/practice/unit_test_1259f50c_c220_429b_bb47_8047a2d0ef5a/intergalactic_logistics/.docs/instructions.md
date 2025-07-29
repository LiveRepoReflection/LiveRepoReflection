## The Intergalactic Logistics Problem

**Problem Description:**

The Intergalactic Federation (IGF) is responsible for distributing resources across its vast network of colonized planets. Due to the immense distances involved, resource transportation relies on a complex network of wormholes. Each wormhole connects two distinct planets and has a specific capacity, representing the maximum amount of resources that can be transported through it per standard time unit.

The IGF is facing a critical resource shortage on planet designated as the "Destination Planet."  Your task is to design and implement an efficient algorithm to determine the maximum amount of resource that can be transported from a designated "Source Planet" to the "Destination Planet" within a given timeframe, considering the wormhole network's capacity constraints.

**Input:**

*   `num_planets`: An integer representing the total number of planets in the IGF network, numbered from 0 to `num_planets - 1`.
*   `wormholes`: A list of tuples, where each tuple `(u, v, capacity)` represents a wormhole connecting planet `u` to planet `v` with capacity `capacity`.  The wormholes are directed. There can be multiple wormholes between two planets.
*   `source`: An integer representing the index of the Source Planet.
*   `destination`: An integer representing the index of the Destination Planet.
*   `timeframe`:  An integer representing the available timeframe in standard time units. The capacity is per standard time unit.

**Output:**

An integer representing the maximum amount of resource that can be transported from the Source Planet to the Destination Planet within the given timeframe.

**Constraints:**

*   1 <= `num_planets` <= 1000
*   0 <= `source`, `destination` < `num_planets`
*   `source` != `destination`
*   0 <= `len(wormholes)` <= 10000
*   0 <= `u`, `v` < `num_planets`
*   0 <= `capacity` <= 1000
*   1 <= `timeframe` <= 1000

**Efficiency Requirements:**

The solution must be efficient enough to handle large input graphs.  Consider algorithmic complexity and potential optimizations.  Solutions exceeding a time complexity of O(V^2 * E) where V is the number of planets and E is the number of wormholes might time out.

**Edge Cases:**

*   No path exists between the Source and Destination Planet.
*   The Source and Destination Planet are directly connected by a wormhole.
*   The wormhole network contains cycles.
*   The wormhole network is disconnected.

**Considerations:**

*   Multiple wormholes may exist between the same two planets.
*   The resource flow along a wormhole cannot exceed its capacity.
*   You may need to utilize advanced data structures and algorithms to achieve optimal performance.
*   The total amount of transported resource is limited by the 'timeframe' so it is required to take into account.

Good luck!
