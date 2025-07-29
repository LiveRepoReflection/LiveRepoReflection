use std::collections::BinaryHeap;
use std::cmp::Reverse;

pub fn solve(
    n: usize,
    edges: Vec<(usize, usize, u32, u32)>,
    flows: Vec<(usize, usize, u32, usize)>,
    l: u32,
) -> usize {
    // Create matrices for latency and available capacity.
    let mut latency = vec![vec![u32::MAX; n]; n];
    let mut capacity = vec![vec![0u32; n]; n];

    for &(u, v, lat, cap) in edges.iter() {
        // Since the graph is undirected, update both directions.
        if u < n && v < n {
            latency[u][v] = lat;
            latency[v][u] = lat;
            capacity[u][v] = cap;
            capacity[v][u] = cap;
        }
    }

    // Sort flows by descending priority. If equal, sort by packet_id in ascending order.
    let mut flows_sorted = flows.clone();
    flows_sorted.sort_by(|a, b| {
        // a = (source, dest, priority, id)
        // Sort by descending priority first, then ascending packet id.
        b.2.cmp(&a.2).then(a.3.cmp(&b.3))
    });

    let mut routed_count = 0;

    for &(src, dest, _priority, _packet_id) in flows_sorted.iter() {
        // If source and destination are same, route without consuming bandwidth.
        if src == dest {
            routed_count += 1;
            continue;
        }

        // Use Dijkstra algorithm but only consider edges with available capacity >= 1
        let (dist, prev) = dijkstra(n, src, &latency, &capacity);
        if dist[dest] <= l {
            // Reconstruct path from dest to src using prev and update capacities
            let mut cur = dest;
            let mut path = Vec::new();
            while cur != src {
                if let Some(p) = prev[cur] {
                    path.push((p, cur));
                    cur = p;
                } else {
                    // Should not happen since we reached dest.
                    break;
                }
            }
            // Decrement capacity for each edge along the path.
            for (u, v) in path {
                if capacity[u][v] > 0 && capacity[v][u] > 0 {
                    capacity[u][v] -= 1;
                    capacity[v][u] -= 1;
                }
            }
            routed_count += 1;
        }
    }
    routed_count
}

fn dijkstra(
    n: usize,
    src: usize,
    latency: &Vec<Vec<u32>>,
    capacity: &Vec<Vec<u32>>,
) -> (Vec<u32>, Vec<Option<usize>>) {
    let mut dist = vec![u32::MAX; n];
    let mut prev = vec![None; n];
    let mut heap = BinaryHeap::new();

    dist[src] = 0;
    heap.push(Reverse((0, src)));

    while let Some(Reverse((d, u))) = heap.pop() {
        // Skip if we already found a better path.
        if d > dist[u] {
            continue;
        }
        for v in 0..n {
            // Proceed if edge exists and capacity is available.
            if capacity[u][v] >= 1 && latency[u][v] != u32::MAX {
                let alt = d.saturating_add(latency[u][v]);
                if alt < dist[v] {
                    dist[v] = alt;
                    prev[v] = Some(u);
                    heap.push(Reverse((alt, v)));
                }
            }
        }
    }
    (dist, prev)
}