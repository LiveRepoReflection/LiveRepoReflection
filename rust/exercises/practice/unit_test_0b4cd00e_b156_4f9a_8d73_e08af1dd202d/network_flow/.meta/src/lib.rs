use std::cmp::Ordering;
use std::collections::BinaryHeap;

pub struct Edge {
    pub from: usize,
    pub to: usize,
    pub capacity: f64,
    pub cost: Box<dyn Fn(f64) -> f64>,
}

struct DijkstraState {
    cost: f64,
    node: usize,
}

impl Eq for DijkstraState {}

impl PartialEq for DijkstraState {
    fn eq(&self, other: &Self) -> bool {
        self.cost == other.cost && self.node == other.node
    }
}

impl Ord for DijkstraState {
    fn cmp(&self, other: &Self) -> Ordering {
        // Note: we reverse the order so that the smallest cost has highest priority.
        other.cost.partial_cmp(&self.cost).unwrap_or(Ordering::Equal)
    }
}

impl PartialOrd for DijkstraState {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

/// Calculates the minimum total energy cost to send `demand` units
/// of resources from source `s` to sink `t` in a network defined by
/// `n` nodes and a vector of `edges`. Returns Err if the demand cannot be met.
///
/// The edges vector contains Edge structures that hold from, to, capacity,
/// and a cost function. The cost function takes the current flow on the edge
/// and returns the total cost for sending that amount of flow.
pub fn min_cost_flow(
    n: usize,
    edges: Vec<Edge>,
    s: usize,
    t: usize,
    demand: f64,
) -> Result<f64, String> {
    // Build adjacency list for outgoing edge indices from each node.
    let mut adj: Vec<Vec<usize>> = vec![Vec::new(); n];
    for (i, edge) in edges.iter().enumerate() {
        if edge.from >= n || edge.to >= n {
            return Err("Edge contains invalid node".into());
        }
        adj[edge.from].push(i);
    }

    // Initialize current flow for each edge.
    let mut flow: Vec<f64> = vec![0.0; edges.len()];
    let mut total_cost = 0.0;
    let mut remaining = demand;
    let epsilon = 1e-6;

    // Main loop: while we still have flow to send.
    while remaining > 1e-9 {
        // Dijkstra initialization.
        let mut dist = vec![f64::INFINITY; n];
        let mut prev: Vec<Option<usize>> = vec![None; n]; // stores edge index used to reach node
        dist[s] = 0.0;

        let mut heap = BinaryHeap::new();
        heap.push(DijkstraState { cost: 0.0, node: s });

        while let Some(DijkstraState { cost, node }) = heap.pop() {
            if cost > dist[node] + 1e-9 {
                continue;
            }
            if node == t {
                // Early exit if we reached sink.
                break;
            }
            // Explore outgoing edges.
            for &edge_idx in &adj[node] {
                // Only consider if edge has residual capacity.
                if flow[edge_idx] < edges[edge_idx].capacity - 1e-9 {
                    // Compute marginal cost using a small epsilon increment.
                    let current_flow = flow[edge_idx];
                    let tentative_flow = current_flow + epsilon;
                    let cost_increase = (edges[edge_idx].cost)(tentative_flow) - (edges[edge_idx].cost)(current_flow);
                    let new_cost = dist[node] + cost_increase;
                    let v = edges[edge_idx].to;
                    if new_cost < dist[v] - 1e-9 {
                        dist[v] = new_cost;
                        prev[v] = Some(edge_idx);
                        heap.push(DijkstraState { cost: new_cost, node: v });
                    }
                }
            }
        }

        // If sink is unreachable, cannot send more flow.
        if dist[t] == f64::INFINITY {
            return Err("Demand cannot be met with given capacities".into());
        }

        // Reconstruct path and determine maximum flow that can be sent along it.
        let mut path = Vec::new();
        let mut cur = t;
        while cur != s {
            let edge_idx = match prev[cur] {
                Some(e) => e,
                None => break,
            };
            path.push(edge_idx);
            cur = edges[edge_idx].from;
        }
        path.reverse();

        // Determine the maximum additional flow that can be sent along this path.
        let mut send = remaining;
        for &edge_idx in &path {
            let available = edges[edge_idx].capacity - flow[edge_idx];
            if available < send {
                send = available;
            }
        }
        if send < 1e-9 {
            return Err("No residual capacity on chosen path".into());
        }

        // Apply flow along the path and update total cost.
        for &edge_idx in &path {
            let current_flow = flow[edge_idx];
            let new_flow = current_flow + send;
            let cost_increase = (edges[edge_idx].cost)(new_flow) - (edges[edge_idx].cost)(current_flow);
            total_cost += cost_increase;
            flow[edge_idx] = new_flow;
        }

        remaining -= send;
    }
    Ok(total_cost)
}