use std::collections::BinaryHeap;
use std::cmp::Reverse;

pub fn shortest_path(
    n: usize,
    hub_counts: Vec<usize>,
    intra_planet_connections: Vec<(usize, usize)>,
    inter_planet_connections: Vec<(usize, usize, u64, u64)>,
    gravitational_sensitivities: Vec<u64>,
    start_planet: usize,
    end_planet: usize,
) -> Option<u64> {
    // Compute total number of hubs and map each hub to its planet.
    let total_hubs: usize = hub_counts.iter().sum();
    let mut hub_to_planet = vec![0; total_hubs];
    let mut offset = 0;
    for (planet, &count) in hub_counts.iter().enumerate() {
        for hub in offset..offset + count {
            hub_to_planet[hub] = planet;
        }
        offset += count;
    }

    // Build graph: each node is a hub; graph[node] is a vector of (neighbor, weight).
    let mut graph = vec![Vec::new(); total_hubs];

    // Intra-planet connections: bidirectional edges with cost 0.
    for (u, v) in intra_planet_connections.iter() {
        if *u < total_hubs && *v < total_hubs {
            graph[*u].push((*v, 0));
            graph[*v].push((*u, 0));
        }
    }

    // Inter-planet connections (wormholes): bidirectional edges with different costs.
    for (u, v, latency, bandwidth) in inter_planet_connections.iter() {
        if *u < total_hubs && *v < total_hubs {
            let planet_v = hub_to_planet[*v];
            let planet_u = hub_to_planet[*u];
            // u -> v: cost increases by gravitational sensitivity of planet_v.
            let cost_uv = latency.saturating_add(gravitational_sensitivities[planet_v].saturating_mul(*bandwidth));
            // v -> u: cost increases by gravitational sensitivity of planet_u.
            let cost_vu = latency.saturating_add(gravitational_sensitivities[planet_u].saturating_mul(*bandwidth));
            graph[*u].push((*v, cost_uv));
            graph[*v].push((*u, cost_vu));
        }
    }

    // Prepare Dijkstra's algorithm.
    // Distance vector: index is hub id.
    let mut dist = vec![u64::MAX; total_hubs];
    let mut heap = BinaryHeap::new();

    // Initialize starting hubs (all hubs on start_planet) with distance 0.
    let mut start_offset = 0;
    for i in 0..n {
        if i == start_planet {
            break;
        }
        start_offset += hub_counts[i];
    }
    let start_hubs = hub_counts[start_planet];
    for hub in start_offset..start_offset + start_hubs {
        dist[hub] = 0;
        heap.push(Reverse((0u64, hub)));
    }

    // Dijkstra's algorithm.
    while let Some(Reverse((current_dist, u))) = heap.pop() {
        // If this hub belongs to the destination planet, we have reached our goal.
        if hub_to_planet[u] == end_planet {
            return Some(current_dist);
        }
        // If we have found a better path before, skip.
        if current_dist > dist[u] {
            continue;
        }
        // Relax neighbors.
        for &(v, weight) in graph[u].iter() {
            let next = current_dist.saturating_add(weight);
            if next < dist[v] {
                dist[v] = next;
                heap.push(Reverse((next, v)));
            }
        }
    }

    None
}