use std::cmp::Ordering;
use std::collections::BinaryHeap;

#[derive(Debug, Clone)]
struct Edge {
    to: usize,
    capacity: u32,
    flow: u32,
    max_flow: u32,
}

#[derive(Debug)]
struct Graph {
    adj: Vec<Vec<Edge>>,
}

impl Graph {
    fn new(n: usize) -> Self {
        Graph {
            adj: vec![Vec::new(); n],
        }
    }
    
    fn add_edge(&mut self, u: usize, v: usize, capacity: u32) {
        let max_flow = Self::compute_max_flow(capacity);
        let edge = Edge {
            to: v,
            capacity,
            flow: 0,
            max_flow,
        };
        self.adj[u].push(edge);
    }
    
    // Compute the maximum number of packets (x) that can traverse an edge
    // such that: x * (1 + (x/capacity)^2) <= capacity.
    fn compute_max_flow(capacity: u32) -> u32 {
        let mut best = 0;
        for x in 1..=capacity {
            let lhs = (x as f64) * (1.0 + ((x as f64) / (capacity as f64)).powi(2));
            if lhs <= capacity as f64 + 1e-9 {
                best = x;
            } else {
                break;
            }
        }
        best
    }
}

#[derive(Copy, Clone)]
struct State {
    cost: f64,
    node: usize,
}

// We implement Eq and Ord for the state to use it in a BinaryHeap.
// The cost is the maximum congestion factor along the path so far.
// We want to minimize this "bottleneck" cost.
impl Eq for State {}

impl PartialEq for State {
    fn eq(&self, other: &Self) -> bool {
        self.cost == other.cost && self.node == other.node
    }
}

impl Ord for State {
    fn cmp(&self, other: &Self) -> Ordering {
        // Reverse order so that the lower cost has higher priority.
        other.cost.partial_cmp(&self.cost).unwrap_or(Ordering::Equal)
    }
}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

// Public function that routes k packets from s to t.
// Returns a vector of paths; each path is a vector of node indices.
// If it is impossible to route all packets, returns an empty vector.
pub fn route_packets(n: usize, edges: &[(usize, usize, u32)], s: usize, t: usize, k: usize) -> Vec<Vec<usize>> {
    let mut graph = Graph::new(n);
    for &(u, v, capacity) in edges {
        if u < n && v < n {
            graph.add_edge(u, v, capacity);
        }
    }
    
    let mut result_paths = Vec::new();
    for _ in 0..k {
        match find_minimax_path(&mut graph, s, t) {
            Some(path) => {
                update_flow(&mut graph, &path);
                result_paths.push(path);
            }
            None => {
                return Vec::new();
            }
        }
    }
    result_paths
}

// Finds a path from s to t which minimizes the maximum edge cost (the congestion factor).
// The cost of using an edge is defined as:
//   cost = 1 + ((flow + 1) / capacity)^2
// An edge can be used only if its current flow is less than its computed max_flow.
fn find_minimax_path(graph: &mut Graph, s: usize, t: usize) -> Option<Vec<usize>> {
    let n = graph.adj.len();
    let mut cost = vec![std::f64::INFINITY; n];
    let mut parent = vec![None; n]; // Stores (previous node, index of edge in graph.adj[previous node])
    let mut heap = BinaryHeap::new();
    
    cost[s] = 0.0;
    heap.push(State { cost: 0.0, node: s });
    
    while let Some(State { cost: curr_cost, node: u }) = heap.pop() {
        if curr_cost > cost[u] {
            continue;
        }
        if u == t {
            break;
        }
        
        for (i, edge) in graph.adj[u].iter().enumerate() {
            // Only consider the edge if it has remaining capacity for additional packets.
            if edge.flow >= edge.max_flow {
                continue;
            }
            // Calculate the congestion factor if one more packet uses this edge.
            let new_edge_cost = 1.0 + (((edge.flow + 1) as f64) / (edge.capacity as f64)).powi(2);
            // The cost of the path is the maximum edge cost along the path.
            let next_cost = curr_cost.max(new_edge_cost);
            if next_cost < cost[edge.to] {
                cost[edge.to] = next_cost;
                parent[edge.to] = Some((u, i));
                heap.push(State { cost: next_cost, node: edge.to });
            }
        }
    }
    
    if cost[t] == std::f64::INFINITY {
        return None;
    }
    
    // Reconstruct the path from t back to s.
    let mut path = Vec::new();
    let mut current = t;
    while let Some((prev, edge_index)) = parent[current] {
        path.push(current);
        current = prev;
    }
    path.push(s);
    path.reverse();
    Some(path)
}

// After selecting a path, update the flow on each edge used.
fn update_flow(graph: &mut Graph, path: &Vec<usize>) {
    for i in 0..(path.len() - 1) {
        let u = path[i];
        let v = path[i + 1];
        for edge in graph.adj[u].iter_mut() {
            if edge.to == v && edge.flow < edge.max_flow {
                edge.flow += 1;
                break;
            }
        }
    }
}