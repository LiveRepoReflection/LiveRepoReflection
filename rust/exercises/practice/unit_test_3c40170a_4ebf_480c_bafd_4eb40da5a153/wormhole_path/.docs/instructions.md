Okay, here's a challenging Rust problem description designed to test a variety of skills.

**Problem Title:** Intergalactic Shortest Path Network

**Problem Description:**

The Intergalactic Consortium of Planets (ICP) is building a new communication network to connect its member planets. Each planet has a number of communication hubs. The ICP wants to minimize the latency of communication between any two planets in the network. Due to the vast distances involved, signals must travel through wormholes to reach other planets, but wormholes have a limited bandwidth.

You are tasked with designing an efficient algorithm to determine the shortest path (minimum latency) between any two planets in the ICP network, considering the locations of communication hubs on each planet, the connections between them, the bandwidth limitations of the wormholes, and gravitational effects.

**Network Details:**

*   **Planets:** The network consists of `N` planets, numbered from 0 to `N-1`. Each planet `i` has `H_i` communication hubs.
*   **Hubs:** Each communication hub is represented by a unique integer ID. Hub IDs are assigned sequentially, starting from 0. So if there are a total of `T` hubs across all planets, they will be numbered from 0 to `T-1`. Each hub belongs to exactly one planet.
*   **Connections:** There are two types of connections:
    *   **Intra-Planet Connections:** These connections exist *within* a planet, linking its communication hubs. The latency of these connections is negligible (considered to be 0). You are given a list of pairs of hub IDs representing these connections.
    *   **Inter-Planet Connections (Wormholes):** These connections link hubs on *different* planets via wormholes. Each wormhole has a latency value and a maximum bandwidth. You are given a list of tuples `(hub_id1, hub_id2, latency, bandwidth)`, where `hub_id1` and `hub_id2` are the IDs of the connected hubs, `latency` is the signal travel time across the wormhole, and `bandwidth` represents the maximum data throughput the wormhole can handle.
*   **Gravitational Effects:** Each wormhole also has a gravitational impact value. For each planet `i`, there is a gravitational sensitivity `G_i`. When traversing a wormhole connected to a hub on planet `i`, the latency of that wormhole is *increased* by `G_i * bandwidth`. The gravitational sensitivity is only applied to the *destination* planet hub of the wormhole.
*   **Bandwidth Consumption:** When a path uses a wormhole, the bandwidth of that wormhole is considered "consumed" for the duration of that communication. This means that no other path can use this wormhole at the same time. For simplicity, assume that you only need to find the shortest path between one pair of planets, and not all pairs.

**Input:**

Your function will receive the following inputs:

*   `N: usize`: The number of planets.
*   `hub_counts: Vec<usize>`: A vector of length `N`, where `hub_counts[i]` is the number of communication hubs on planet `i`.
*   `intra_planet_connections: Vec<(usize, usize)>`: A vector of tuples, where each tuple `(hub_id1, hub_id2)` represents a connection between hubs `hub_id1` and `hub_id2` on the same planet.
*   `inter_planet_connections: Vec<(usize, usize, u64, u64,)>`: A vector of tuples, where each tuple `(hub_id1, hub_id2, latency, bandwidth)` represents a wormhole connection between `hub_id1` and `hub_id2` with the given `latency` and `bandwidth`.
*   `gravitational_sensitivities: Vec<u64>`: A vector of length `N`, where `gravitational_sensitivities[i]` is the gravitational sensitivity of planet `i`.
*   `start_planet: usize`: The ID of the starting planet.
*   `end_planet: usize`: The ID of the destination planet.

**Output:**

Your function must return an `Option<u64>`:

*   `Some(min_latency)`: If a path exists between *any* hub on the `start_planet` and *any* hub on the `end_planet`, return the minimum latency of the shortest path.
*   `None`: If no path exists between any hub on the `start_planet` and any hub on the `end_planet`.

**Constraints:**

*   `1 <= N <= 100`
*   `1 <= H_i <= 100` for each planet `i`
*   The total number of hubs `T` across all planets is at most 10,000.
*   `0 <= latency <= 10^9`
*   `1 <= bandwidth <= 10^6`
*   `0 <= gravitational_sensitivity <= 10^3`
*   `0 <= start_planet, end_planet < N`
*   All hub IDs in `intra_planet_connections` and `inter_planet_connections` will be valid.

**Optimization Requirements:**

*   Your solution must be efficient enough to handle large networks (close to the maximum constraint limits) within a reasonable time limit (e.g., under 10 seconds). Consider algorithmic complexity and choose appropriate data structures.
*   Avoid unnecessary memory allocations and copies.

**Example:**

Imagine two planets, Earth (0) with hub IDs 0 and 1 and Mars (1) with hub IDs 2 and 3.
There is an intra-planet connection between hubs 0 and 1, and hubs 2 and 3.
There is a wormhole between hub 1 (Earth) and hub 2 (Mars) with latency 10 and bandwidth 100.
Earth's gravitational sensitivity is 0, and Mars' gravitational sensitivity is 1.

The shortest path from Earth to Mars would be from any hub on Earth to the wormhole, then across the wormhole to any hub on Mars.
The latency would be 10 + (1 * 100) = 110.

**This problem requires you to:**

*   Represent the network as a graph.
*   Implement a shortest path algorithm (e.g., Dijkstra or A*) suitable for large graphs with potentially many edges.
*   Account for the gravitational effects on wormhole latency.
*   Efficiently handle the bandwidth constraint.
*   Handle edge cases and disconnected components.
*   Optimize for performance.

Good luck!
