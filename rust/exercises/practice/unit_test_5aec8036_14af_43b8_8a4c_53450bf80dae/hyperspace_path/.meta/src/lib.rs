use std::collections::{BinaryHeap, HashMap};
use std::cmp::Reverse;

struct Edge {
    dest: String,
    base: u32,
    // events: sorted vector of (timestamp, delta)
    events: Vec<(u64, i32)>,
    // prefix sums of deltas corresponding to events vector
    prefix: Vec<i32>,
}

fn compute_effective_weight(edge: &Edge, query_time: u64) -> u32 {
    // Using binary search (partition_point) to find count of events with timestamp <= query_time.
    let idx = edge.events.partition_point(|&(ts, _)| ts <= query_time);
    let cumulative = if idx == 0 { 0 } else { edge.prefix[idx - 1] };
    let new_weight = edge.base as i32 + cumulative;
    if new_weight < 0 { 0 } else { new_weight as u32 }
}

pub fn find_shortest_path(
    initial_routes: Vec<(String, String, u32)>,
    fluctuations: Vec<(u64, String, String, i32)>,
    start: &str,
    end: &str,
    query_time: u64
) -> Option<u32> {
    // Build a graph: map from starting planet to vector of outgoing edges.
    let mut graph: HashMap<String, Vec<Edge>> = HashMap::new();

    // Insert initial routes.
    for (src, dst, base) in initial_routes.into_iter() {
        graph.entry(src)
            .or_insert_with(Vec::new)
            .push(Edge { dest: dst, base, events: Vec::new(), prefix: Vec::new() });
    }

    // Process fluctuations: if a fluctuation event refers to an existing edge, add it.
    for (ts, src, dst, delta) in fluctuations.into_iter() {
        if let Some(edges) = graph.get_mut(&src) {
            // Find the edge with matching destination.
            for edge in edges.iter_mut() {
                if edge.dest == dst {
                    edge.events.push((ts, delta));
                    break;
                }
            }
        }
    }

    // For each edge, sort the events and compute prefix sums.
    for edges in graph.values_mut() {
        for edge in edges.iter_mut() {
            edge.events.sort_by(|a, b| a.0.cmp(&b.0));
            let mut prefix = Vec::with_capacity(edge.events.len());
            let mut sum = 0;
            for &(_ts, delta) in edge.events.iter() {
                sum += delta;
                prefix.push(sum);
            }
            edge.prefix = prefix;
        }
    }

    // Dijkstra's algorithm, using a min-heap (with Reverse) keyed by (distance, planet).
    let mut dist: HashMap<String, u32> = HashMap::new();
    let mut heap = BinaryHeap::new();

    // Start node: even if it is not in graph, we still consider it.
    dist.insert(start.to_string(), 0);
    heap.push(Reverse((0u32, start.to_string())));

    while let Some(Reverse((d, node))) = heap.pop() {
        // If this popped distance is not the latest, skip.
        if let Some(&cur) = dist.get(&node) {
            if d > cur {
                continue;
            }
        }
        if node == end {
            return Some(d);
        }
        // For each outgoing edge from current node:
        if let Some(edges) = graph.get(&node) {
            for edge in edges {
                let effective = compute_effective_weight(edge, query_time);
                let next_distance = d.checked_add(effective);
                if next_distance.is_none() {
                    continue;
                }
                let next_distance = next_distance.unwrap();
                let dest = edge.dest.clone();
                if dist.get(&dest).map_or(true, |&current| next_distance < current) {
                    dist.insert(dest.clone(), next_distance);
                    heap.push(Reverse((next_distance, dest)));
                }
            }
        }
    }
    None
}