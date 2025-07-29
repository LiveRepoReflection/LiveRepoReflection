## The Intergalactic Logistics Problem

**Problem Description:**

The Intergalactic Federation (IGF) manages a vast network of space stations and trade routes across the galaxy. Each station is uniquely identified by an integer ID. Trade routes connect these stations, each having a specific travel time (in galactic standard time units - GSTU) and a cargo capacity limit (in metric tonnes).

The IGF needs to optimize the transportation of goods between various origin and destination stations. However, the network is dynamic: trade routes can be temporarily blocked due to space pirate activity or maintenance. Moreover, cargo demands can fluctuate rapidly.

You are tasked with designing a system to efficiently determine the optimal routes for transporting goods, taking into account these constraints.

**Specific Requirements:**

1.  **Network Representation:** Represent the intergalactic network as a graph, where nodes are space stations and edges are trade routes. Each trade route has a *travel time* and a *cargo capacity*.

2.  **Route Finding:** Given an origin station, a destination station, a cargo amount (in metric tonnes), and a list of blocked trade routes (specified by pairs of station IDs), find the route with the *shortest travel time* that can accommodate the given cargo amount, avoiding the blocked routes.

3.  **Dynamic Updates:** Implement functionality to efficiently update the network. This includes:
    *   Adding new trade routes.
    *   Removing existing trade routes.
    *   Temporarily blocking/unblocking trade routes.

4.  **Cargo Splitting:** If no single route exists that can accommodate the entire cargo amount, the system should attempt to split the cargo across multiple routes to the destination.  Minimize the *maximum travel time* of any route used. If cargo splitting is necessary, return a list of routes with their respective cargo amounts.

5.  **Optimization:**
    *   Route finding should be optimized for speed, as cargo requests need to be processed quickly. Consider using appropriate graph algorithms and data structures.
    *   Dynamic updates should also be efficient, avoiding complete recalculations of the entire network.

**Constraints:**

*   The number of stations can be up to 10,000.
*   The number of trade routes can be up to 100,000.
*   Travel times are non-negative integers.
*   Cargo capacities are positive integers.
*   Cargo amounts are positive integers.
*   Blocked routes are temporary and can be unblocked later.
*   Multiple routes may exist between two stations.  You must consider all of them.
*   The system must handle cases where no route exists (or no combination of routes can handle the cargo).
*   The blocked routes must be considered during the routing process.
*   Cargo splitting must be minimized, only use it when neccessary.
*   Cargo splitting needs to minimize the maximum travel time of any route used for cargo splitting.
*   The number of cargo splits should be kept as low as possible.

**Input:**

The system receives cargo requests with the following information:

*   Origin station ID.
*   Destination station ID.
*   Cargo amount (in metric tonnes).
*   A list of currently blocked trade routes (pairs of station IDs).

The system also receives update requests:

*   Add trade route (station ID 1, station ID 2, travel time, cargo capacity).
*   Remove trade route (station ID 1, station ID 2, travel time, cargo capacity).
*   Block trade route (station ID 1, station ID 2).
*   Unblock trade route (station ID 1, station ID 2).

**Output:**

For cargo requests:

*   If a single route can accommodate the cargo: return the list of station IDs representing the route.
*   If cargo splitting is necessary: return a list of tuples, where each tuple contains a route (list of station IDs) and the cargo amount for that route.
*   If no route exists or the cargo cannot be transported: return an appropriate error message (e.g., "No route available", "Cargo exceeds network capacity").

For update requests:

*   Return a success message (e.g., "Trade route added", "Trade route blocked").

**Evaluation Criteria:**

Solutions will be evaluated based on:

*   Correctness: The ability to find valid routes and handle all edge cases.
*   Efficiency: The speed of route finding and dynamic updates.
*   Code quality: Readability, maintainability, and adherence to good programming practices.
*   Cargo splitting optimization: Ability to minimize maximum travel time during cargo splitting.
*   Cargo splitting count: Keeping the number of cargo splits as low as possible.

This problem requires a strong understanding of graph algorithms, data structures, and optimization techniques, and will challenge participants to design a robust and efficient solution. Good luck.
