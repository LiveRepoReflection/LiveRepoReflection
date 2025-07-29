use std::collections::{BinaryHeap, HashMap};
use std::cmp::Ordering;

#[derive(Copy, Clone, Eq, PartialEq)]
struct State {
    cost: u64,
    time: u32,
    node: usize,
}

// Custom implementation for BinaryHeap to create a min-heap based on cost
impl Ord for State {
    fn cmp(&self, other: &Self) -> Ordering {
        other.cost.cmp(&self.cost)
            .then_with(|| other.time.cmp(&self.time))
            .then_with(|| self.node.cmp(&other.node))
    }
}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

pub fn find_optimal_path(
    n: usize,
    edges: Vec<(usize, usize, u32, u64, u32)>,
    s: usize,
    d: usize,
    t: u32,
    goods_weight: u32,
) -> Option<u64> {
    // Handle the case where source and destination are the same
    if s == d {
        return Some(0);
    }

    // Create adjacency list representation of the graph
    let mut graph: Vec<Vec<(usize, u32, u64, u32)>> = vec![Vec::new(); n];
    for (from, to, time, cost, capacity) in edges {
        if capacity >= goods_weight {
            graph[from].push((to, time, cost, capacity));
        }
    }

    // Initialize data structures for Dijkstra's algorithm
    let mut heap = BinaryHeap::new();
    let mut best_costs: HashMap<(usize, u32), u64> = HashMap::new();

    // Add starting point to heap
    heap.push(State { cost: 0, time: 0, node: s });
    best_costs.insert((s, 0), 0);

    // Dijkstra's algorithm with time constraint
    while let Some(State { cost, time, node }) = heap.pop() {
        // If we've reached the destination
        if node == d {
            return Some(cost);
        }

        // If this state has been superseded
        if best_costs.get(&(node, time)).map_or(false, |&c| cost > c) {
            continue;
        }

        // Explore neighbors
        for &(next_node, edge_time, edge_cost, _) in &graph[node] {
            let new_time = time + edge_time;
            let new_cost = cost + edge_cost;

            // Check time constraint
            if new_time > t {
                continue;
            }

            // If we've found a better path to this node at this time
            let is_better = best_costs
                .get(&(next_node, new_time))
                .map_or(true, |&c| new_cost < c);

            if is_better {
                heap.push(State {
                    cost: new_cost,
                    time: new_time,
                    node: next_node,
                });
                best_costs.insert((next_node, new_time), new_cost);
            }
        }
    }

    // No valid path found
    None
}