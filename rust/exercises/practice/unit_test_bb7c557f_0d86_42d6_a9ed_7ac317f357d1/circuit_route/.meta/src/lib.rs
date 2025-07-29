use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn minimal_delay(
    n: usize,
    edges: Vec<(usize, usize, u32)>,
    start_components: Vec<usize>,
    end_components: Vec<usize>,
    max_allowed_delay: u32,
) -> i64 {
    // Return -1 immediately if there are no start or end components.
    if start_components.is_empty() || end_components.is_empty() {
        return -1;
    }

    // Build graph as an adjacency list.
    let mut graph = vec![Vec::new(); n];
    for (u, v, w) in edges {
        if u < n && v < n {
            graph[u].push((v, w));
            graph[v].push((u, w)); // undirected graph: add both directions.
        }
    }

    // Create a marker for target nodes.
    let mut is_target = vec![false; n];
    for t in end_components {
        if t < n {
            is_target[t] = true;
        }
    }

    // Initialize distances array with "infinity" (using u64 to avoid overflow).
    let mut dist = vec![u64::MAX; n];

    // Use a binary heap (min-heap via Reverse) for Dijkstra's algorithm.
    let mut heap = BinaryHeap::new();
    for start in start_components {
        if start < n {
            dist[start] = 0;
            heap.push(Reverse((0u64, start)));
        }
    }

    // Perform multi-source Dijkstra's algorithm.
    while let Some(Reverse((d, node))) = heap.pop() {
        if d > dist[node] {
            continue;
        }
        // If current node is a target and delay is within allowed bound, return the delay.
        if is_target[node] {
            if d <= max_allowed_delay as u64 {
                return d as i64;
            } else {
                // Current path exceeds allowed delay.
                continue;
            }
        }
        // Explore adjacent neighbors.
        for &(nei, w) in &graph[node] {
            let nd = d + w as u64;
            if nd < dist[nei] {
                dist[nei] = nd;
                heap.push(Reverse((nd, nei)));
            }
        }
    }

    // No valid connection found within max_allowed_delay.
    -1
}