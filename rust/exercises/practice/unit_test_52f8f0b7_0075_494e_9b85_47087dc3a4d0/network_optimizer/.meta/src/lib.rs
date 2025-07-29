use std::collections::BinaryHeap;
use std::cmp::Reverse;

pub fn optimize_network(
    n: usize,
    edge_list: Vec<(usize, usize, u32)>,
    requests: Vec<(usize, usize, u32)>,
    bandwidth: u32,
) -> f64 {
    // Build graph as an adjacency list.
    let mut graph: Vec<Vec<(usize, u32)>> = vec![Vec::new(); n];
    for (u, v, latency) in edge_list {
        graph[u].push((v, latency));
    }

    let mut total_path_latency: u64 = 0;
    let mut total_size: u64 = 0;

    // For each request, compute the shortest path latency.
    // If any request fails to find a path, return INFINITY.
    for (src, dest, size) in &requests {
        let latency = dijkstra(*src, *dest, n, &graph);
        if latency == u32::MAX {
            return f64::INFINITY;
        }
        total_path_latency += latency as u64;
        total_size += *size as u64;
    }

    // Transmission delay is determined by the total message size of all requests.
    // Each request must wait the total transmission time (in ms) which is
    // (total_size / bandwidth). Add this delay to the computed path latency.
    let transmission_delay = total_size as f64 / bandwidth as f64;
    let m = requests.len() as f64;
    let average_path_latency = total_path_latency as f64 / m;

    average_path_latency + transmission_delay
}

fn dijkstra(src: usize, dest: usize, n: usize, graph: &Vec<Vec<(usize, u32)>>) -> u32 {
    let mut dist = vec![u32::MAX; n];
    let mut heap = BinaryHeap::new();

    dist[src] = 0;
    heap.push(Reverse((0u32, src)));

    while let Some(Reverse((d, u))) = heap.pop() {
        if u == dest {
            return d;
        }
        if d > dist[u] {
            continue;
        }
        for &(v, weight) in &graph[u] {
            let nd = d.saturating_add(weight);
            if nd < dist[v] {
                dist[v] = nd;
                heap.push(Reverse((nd, v)));
            }
        }
    }
    dist[dest]
}