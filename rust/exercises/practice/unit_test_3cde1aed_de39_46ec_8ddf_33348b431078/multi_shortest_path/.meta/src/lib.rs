use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn multi_source_shortest_path(
    num_nodes: usize,
    edges: Vec<(usize, usize, i32)>,
    sources: Vec<usize>,
) -> Vec<i32> {
    // Build graph as an adjacency list: graph[u] = vector of (v, weight)
    let mut graph = vec![Vec::new(); num_nodes];
    for (u, v, weight) in edges {
        if u < num_nodes && v < num_nodes {
            graph[u].push((v, weight));
        }
    }

    // Define a constant INF to represent an unreachable distance.
    const INF: i32 = i32::MAX;
    let mut dist = vec![INF; num_nodes];

    // Priority queue holding (distance, node) wrapped in Reverse for min-heap behavior
    let mut heap = BinaryHeap::new();

    // Initialize distances for every source node and push them into the heap.
    for &src in &sources {
        if src < num_nodes && dist[src] > 0 {
            dist[src] = 0;
            heap.push(Reverse((0, src)));
        }
    }

    // Dijkstra's algorithm with multiple sources.
    while let Some(Reverse((d, u))) = heap.pop() {
        if d > dist[u] {
            continue;
        }
        for &(v, weight) in &graph[u] {
            // Calculate the new distance with normal addition
            let new_dist = d + weight;
            if new_dist < dist[v] {
                dist[v] = new_dist;
                heap.push(Reverse((new_dist, v)));
            }
        }
    }

    // Replace any INF values with -1 to indicate unreachable nodes.
    for d in &mut dist {
        if *d == INF {
            *d = -1;
        }
    }

    dist
}