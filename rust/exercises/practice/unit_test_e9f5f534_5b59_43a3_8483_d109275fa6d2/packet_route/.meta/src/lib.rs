use std::collections::{BinaryHeap, HashMap};
use std::cmp::Reverse;

pub fn optimal_route(
    n: usize,
    edges: &Vec<(usize, usize, u64)>,
    source: usize,
    destination: usize,
    packet_size_bytes: u64,
    edge_bandwidths: &HashMap<(usize, usize), u64>,
    packet_loss_probabilities: &HashMap<usize, f64>,
) -> Option<(u64, Vec<usize>)> {
    // Create an adjacency list for the undirected graph.
    let mut graph = vec![Vec::new(); n];
    for &(u, v, latency) in edges {
        if u < n && v < n {
            graph[u].push((v, latency));
            graph[v].push((u, latency));
        }
    }

    // Default values for bandwidth and packet loss probability.
    let default_bandwidth: u64 = 1000;
    let default_loss: f64 = 0.0;

    // distances[node] holds minimum cost from source to node.
    let mut dist = vec![u64::MAX; n];
    // parent[node] holds the previous node on the optimal path.
    let mut parent = vec![None; n];

    // Min-heap for Dijkstra: (cost, node)
    let mut heap = BinaryHeap::new();

    dist[source] = 0;
    heap.push(Reverse((0u64, source)));

    while let Some(Reverse((cost, u))) = heap.pop() {
        if cost > dist[u] {
            continue;
        }
        if u == destination {
            break;
        }
        for &(v, latency) in &graph[u] {
            // Determine the effective bandwidth for edge (u, v).
            let bw = edge_bandwidths.get(&(u, v)).copied().unwrap_or(default_bandwidth);
            // Calculate the congestion penalty: (packet_size_bytes / bandwidth) * latency.
            let penalty = (packet_size_bytes / bw) * latency;

            // Retrieve the packet loss probability for the destination node of the edge.
            let loss = *packet_loss_probabilities.get(&v).unwrap_or(&default_loss);
            // Packet loss overhead: floor(latency * loss probability)
            let overhead = ((latency as f64) * loss).floor() as u64;

            // Total cost to traverse edge (u, v)
            let edge_cost = latency + penalty + overhead;
            let next_cost = cost.saturating_add(edge_cost);

            if next_cost < dist[v] {
                dist[v] = next_cost;
                parent[v] = Some(u);
                heap.push(Reverse((next_cost, v)));
            }
        }
    }

    if dist[destination] == u64::MAX {
        return None;
    }

    // Reconstruct the optimal path from destination to source.
    let mut path = Vec::new();
    let mut curr = destination;
    loop {
        path.push(curr);
        if curr == source {
            break;
        }
        match parent[curr] {
            Some(prev) => curr = prev,
            None => break,
        }
    }
    path.reverse();
    Some((dist[destination], path))
}