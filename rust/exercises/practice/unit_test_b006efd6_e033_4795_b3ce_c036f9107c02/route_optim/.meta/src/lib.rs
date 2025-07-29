use std::collections::{BinaryHeap, HashMap};
use std::cmp::Ordering;

#[derive(Clone, Debug)]
struct State {
    time: u32,
    cost: u32,
    pos: usize,
    mask: u32,
    route: Vec<usize>,
}

impl Eq for State {}

impl PartialEq for State {
    fn eq(&self, other: &Self) -> bool {
        self.time == other.time && self.cost == other.cost && self.pos == other.pos && self.mask == other.mask
    }
}

impl Ord for State {
    fn cmp(&self, other: &Self) -> Ordering {
        // We want the state with lower time to be considered "greater" when using Reverse,
        // so we reverse the ordering here.
        other.time.cmp(&self.time)
            .then_with(|| other.cost.cmp(&self.cost))
            .then_with(|| self.pos.cmp(&other.pos))
            .then_with(|| self.mask.cmp(&other.mask))
    }
}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

/// Find the optimal route starting and ending at the depot (node 0). The route must visit all the
/// destination nodes at least once while staying within the given time_limit and budget.
/// 
/// # Arguments
/// * `num_intersections` - Total number of intersections (nodes) in the graph.
/// * `edges` - A vector of tuples representing directed edges: (from, to, travel_time, toll_cost).
/// * `destination_nodes` - A vector of nodes that must be visited at least once.
/// * `time_limit` - Maximum allowed total travel time.
/// * `budget` - Maximum allowed total toll cost.
/// 
/// # Returns
/// An Option containing a vector of node indices representing the route (starting and ending at 0)
/// if a valid route exists, otherwise None.
pub fn optimal_route(
    num_intersections: usize, 
    edges: Vec<(usize, usize, u32, u32)>, 
    destination_nodes: Vec<usize>, 
    time_limit: u32, 
    budget: u32
) -> Option<Vec<usize>> {
    // Build the graph as an adjacency list.
    let mut graph: Vec<Vec<(usize, u32, u32)>> = vec![Vec::new(); num_intersections];
    for (from, to, travel_time, toll_cost) in edges.iter() {
        graph[*from].push((*to, *travel_time, *toll_cost));
    }
    
    // Map destination nodes to bits in the mask.
    let mut dest_bit: HashMap<usize, u32> = HashMap::new();
    for (i, &dest) in destination_nodes.iter().enumerate() {
        dest_bit.insert(dest, 1 << i);
    }
    let full_mask: u32 = if destination_nodes.is_empty() { 0 } else { (1 << destination_nodes.len()) - 1 };
    
    // Initial mask if depot (0) is among the destination nodes.
    let init_mask = if let Some(&bit) = dest_bit.get(&0) { bit } else { 0 };
    
    // Priority queue for Dijkstra-like search. We want states with lower time (and then lower cost) prioritized.
    let mut heap = BinaryHeap::new();
    let initial_state = State {
        time: 0,
        cost: 0,
        pos: 0,
        mask: init_mask,
        route: vec![0],
    };
    heap.push(initial_state);
    
    // Use a hashmap to store the best (lowest time) encountered for a state defined by (pos, mask, cost).
    let mut best: HashMap<(usize, u32, u32), u32> = HashMap::new();
    best.insert((0, init_mask, 0), 0);
    
    while let Some(state) = heap.pop() {
        // If we've returned to depot, have visited all destination nodes, and are within constraints, return route.
        if state.pos == 0 && state.mask == full_mask && state.time <= time_limit && state.cost <= budget && state.route.len() > 1 {
            return Some(state.route);
        }
        
        // Expand the current state.
        for &(next, t, c) in &graph[state.pos] {
            let new_time = state.time + t;
            let new_cost = state.cost + c;
            if new_time > time_limit || new_cost > budget {
                continue; // skip if exceeding constraints.
            }
            // Update mask if next is a destination.
            let next_mask = if let Some(&bit) = dest_bit.get(&next) {
                state.mask | bit
            } else {
                state.mask
            };
            let mut new_route = state.route.clone();
            new_route.push(next);
            let key = (next, next_mask, new_cost);
            
            // Check if we've found a better (lower time) route for the same state.
            if let Some(&prev_time) = best.get(&key) {
                if new_time >= prev_time {
                    continue; // not an improvement.
                }
            }
            best.insert(key, new_time);
            let new_state = State {
                time: new_time,
                cost: new_cost,
                pos: next,
                mask: next_mask,
                route: new_route,
            };
            heap.push(new_state);
        }
    }
    
    None
}