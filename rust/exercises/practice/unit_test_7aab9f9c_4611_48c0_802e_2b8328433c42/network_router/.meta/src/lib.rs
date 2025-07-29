use std::collections::{BinaryHeap, HashMap};
use std::cmp::Ordering;

#[derive(Copy, Clone, Eq, PartialEq)]
struct State {
    cost: u32,
    node: usize,
}

// Custom implementation for State to be used in BinaryHeap
impl Ord for State {
    fn cmp(&self, other: &Self) -> Ordering {
        other.cost.cmp(&self.cost)
            .then_with(|| self.node.cmp(&other.node))
    }
}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

pub fn can_reach_destination(
    num_nodes: usize,
    edges: &[(usize, usize, u32)],
    source: usize,
    destination: usize,
    max_cost: u32,
) -> bool {
    // Validate input nodes
    if source >= num_nodes || destination >= num_nodes {
        return false;
    }

    // Handle special case where source equals destination
    if source == destination {
        return true;
    }

    // Create adjacency list representation of the graph
    let mut graph: HashMap<usize, Vec<(usize, u32)>> = HashMap::new();
    
    // Build the graph (undirected)
    for &(from, to, cost) in edges {
        if from >= num_nodes || to >= num_nodes {
            continue;
        }
        graph.entry(from).or_default().push((to, cost));
        graph.entry(to).or_default().push((from, cost));
    }

    // Initialize distances
    let mut distances: Vec<u32> = vec![u32::MAX; num_nodes];
    distances[source] = 0;

    // Priority queue for Dijkstra's algorithm
    let mut heap = BinaryHeap::new();
    heap.push(State {
        cost: 0,
        node: source,
    });

    // Dijkstra's algorithm
    while let Some(State { cost, node }) = heap.pop() {
        // If we've reached the destination, check if the cost is acceptable
        if node == destination {
            return cost <= max_cost;
        }

        // If current cost is greater than the known distance, skip
        if cost > distances[node] {
            continue;
        }

        // Check all neighbors
        if let Some(neighbors) = graph.get(&node) {
            for &(next_node, edge_cost) in neighbors {
                let next_cost = match cost.checked_add(edge_cost) {
                    Some(c) => c,
                    None => continue, // Skip if overflow
                };

                // If the new path is shorter and within max_cost
                if next_cost < distances[next_node] && next_cost <= max_cost {
                    distances[next_node] = next_cost;
                    heap.push(State {
                        cost: next_cost,
                        node: next_node,
                    });
                }
            }
        }
    }

    // If we get here, no path was found within max_cost
    false
}