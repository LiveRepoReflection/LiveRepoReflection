use std::collections::{BinaryHeap, HashMap};
use std::cmp::Reverse;

#[derive(Debug)]
pub struct Graph {
    // Map from node id to vector of (neighbor, edge cost)
    edges: HashMap<String, Vec<(String, u32)>>,
}

impl Graph {
    pub fn new() -> Self {
        Graph {
            edges: HashMap::new(),
        }
    }

    pub fn add_edge(&mut self, source: &str, dest: &str, cost: u32) {
        self.edges
            .entry(source.to_string())
            .or_insert_with(Vec::new)
            .push((dest.to_string(), cost));
        // If the graph is directed, we do not add the reverse edge.
        // If needed, uncomment the following lines to add an undirected edge.
        // self.edges
        //     .entry(dest.to_string())
        //     .or_insert_with(Vec::new)
        //     .push((source.to_string(), cost));
    }

    pub fn get_edge_cost(&self, source: &str, dest: &str) -> u32 {
        if let Some(neighbors) = self.edges.get(source) {
            for (nbr, cost) in neighbors {
                if nbr == dest {
                    return *cost;
                }
            }
        }
        0
    }

    pub fn neighbors(&self, node: &str) -> Vec<(String, u32)> {
        if let Some(neighbors) = self.edges.get(node) {
            neighbors.clone()
        } else {
            Vec::new()
        }
    }
}

#[derive(Debug, Clone)]
pub struct Event {
    pub time: u32,
    pub node: String,
    pub is_blocked: bool,
}

fn dijkstra(
    graph: &Graph,
    start: &String,
    destination: &String,
    blocked: &HashMap<String, bool>,
    penalty: u32,
) -> Option<(u32, HashMap<String, String>)> {
    // distances map and parent pointer map
    let mut dist: HashMap<String, u32> = HashMap::new();
    let mut parent: HashMap<String, String> = HashMap::new();
    // Priority queue: (Reverse(cost), node)
    let mut heap = BinaryHeap::new();

    // Initialize
    dist.insert(start.clone(), 0);
    heap.push(Reverse((0, start.clone())));

    while let Some(Reverse((cost_u, u))) = heap.pop() {
        // If we reached destination, return early
        if &u == destination {
            return Some((cost_u, parent));
        }

        // If current cost is greater than recorded, skip it.
        if let Some(&d) = dist.get(&u) {
            if cost_u > d {
                continue;
            }
        }

        // For every neighbor of u
        for (v, cost_uv) in graph.neighbors(&u) {
            // Additional penalty if u or v is blocked
            let penalty_u = if *blocked.get(&u).unwrap_or(&false) { penalty } else { 0 };
            let penalty_v = if *blocked.get(&v).unwrap_or(&false) { penalty } else { 0 };
            let effective_cost = cost_uv + penalty_u + penalty_v;
            let next_cost = cost_u + effective_cost;
            if next_cost < *dist.get(&v).unwrap_or(&u32::MAX) {
                dist.insert(v.clone(), next_cost);
                parent.insert(v.clone(), u.clone());
                heap.push(Reverse((next_cost, v)));
            }
        }
    }
    None
}

pub fn find_path(
    graph: &mut Graph,
    start_node: String,
    destination_node: String,
    events: Vec<Event>,
    penalty: u32,
) -> Vec<String> {
    // Process events in order of time. The final state for each node is used.
    let mut blocked: HashMap<String, bool> = HashMap::new();
    for event in events.into_iter() {
        blocked.insert(event.node, event.is_blocked);
    }

    // If start and destination are the same, return early.
    if start_node == destination_node {
        return vec![start_node];
    }

    // Run Dijkstra's algorithm to find the shortest path with dynamic penalty
    if let Some((_cost, parent)) =
        dijkstra(graph, &start_node, &destination_node, &blocked, penalty)
    {
        // Reconstruct path from destination to start using parent map.
        let mut path = Vec::new();
        let mut current = destination_node;
        path.push(current.clone());
        while let Some(prev) = parent.get(&current) {
            path.push(prev.clone());
            current = prev.clone();
        }
        path.reverse();
        // Check if the first element is indeed the start node.
        if path.first().map_or(false, |s| s == &start_node) {
            return path;
        }
    }
    // If there is no path, return an empty vector.
    Vec::new()
}