use std::collections::{BinaryHeap, HashMap};
use std::cmp::Reverse;

#[derive(Debug)]
pub enum Command {
    FindRoute {
        start_node: usize,
        end_node: usize,
        data_size: u64,
    },
    UpdateLink {
        node1: usize,
        node2: usize,
        new_latency: u64,
        new_capacity: u64,
    },
    RemoveLink {
        node1: usize,
        node2: usize,
    },
    AddLink {
        node1: usize,
        node2: usize,
        latency: u64,
        capacity: u64,
    },
}

pub fn process_network(
    n: usize,
    initial_links: Vec<(usize, usize, u64, u64)>,
    commands: Vec<Command>,
) -> Vec<Option<u64>> {
    // Build initial graph: graph represented as a vector of HashMaps.
    // Each node maps to its neighbor along with the tuple (latency, capacity).
    let mut graph: Vec<HashMap<usize, (u64, u64)>> = vec![HashMap::new(); n];
    for (u, v, latency, capacity) in initial_links {
        graph[u].insert(v, (latency, capacity));
        graph[v].insert(u, (latency, capacity));
    }

    let mut results = Vec::new();

    for cmd in commands {
        match cmd {
            Command::FindRoute {
                start_node,
                end_node,
                data_size,
            } => {
                let res = dijkstra(&graph, start_node, end_node, data_size);
                results.push(res);
            }
            Command::UpdateLink {
                node1,
                node2,
                new_latency,
                new_capacity,
            } => {
                graph[node1].insert(node2, (new_latency, new_capacity));
                graph[node2].insert(node1, (new_latency, new_capacity));
            }
            Command::RemoveLink { node1, node2 } => {
                graph[node1].remove(&node2);
                graph[node2].remove(&node1);
            }
            Command::AddLink {
                node1,
                node2,
                latency,
                capacity,
            } => {
                graph[node1].insert(node2, (latency, capacity));
                graph[node2].insert(node1, (latency, capacity));
            }
        }
    }
    results
}

// Modified Dijkstra algorithm to account for congestion effects.
// For a link with given latency and capacity,
// if data_size exceeds capacity, multiplier = ceil(data_size / capacity) is applied,
// and the effective latency becomes latency * multiplier.
fn dijkstra(
    graph: &Vec<HashMap<usize, (u64, u64)>>,
    start: usize,
    target: usize,
    data_size: u64,
) -> Option<u64> {
    let n = graph.len();
    let mut dist: Vec<u64> = vec![u64::MAX; n];
    let mut heap: BinaryHeap<Reverse<(u64, usize)>> = BinaryHeap::new();

    dist[start] = 0;
    heap.push(Reverse((0, start)));

    while let Some(Reverse((d, node))) = heap.pop() {
        if node == target {
            return Some(d);
        }
        if d > dist[node] {
            continue;
        }
        for (&neighbor, &(latency, capacity)) in &graph[node] {
            let multiplier = if data_size > capacity {
                (data_size + capacity - 1) / capacity
            } else {
                1
            };
            let effective_latency = latency.saturating_mul(multiplier);
            let attempt = d.saturating_add(effective_latency);
            if attempt < dist[neighbor] {
                dist[neighbor] = attempt;
                heap.push(Reverse((attempt, neighbor)));
            }
        }
    }
    None
}