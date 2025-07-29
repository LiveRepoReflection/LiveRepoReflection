use std::collections::{HashMap, VecDeque};

#[derive(Clone)]
struct Edge {
    u: usize,
    v: usize,
    cost: u32,
    capacity: u32,
}

pub fn optimize_network(
    n: usize,
    edge_costs: &HashMap<(usize, usize), u32>,
    edge_capacities: &HashMap<(usize, usize), u32>,
    max_total_cost: u32,
    fault_tolerance: usize,
) -> Option<f64> {
    // For a single node or no pairs, return 0.0 latency.
    if n <= 1 {
        return Some(0.0);
    }

    // Collect unique candidate edges (only one per undirected pair) where u < v.
    let mut candidates: Vec<Edge> = Vec::new();
    for (&(u, v), &cost) in edge_costs.iter() {
        if u < v {
            if let Some(&cap) = edge_capacities.get(&(u, v)) {
                candidates.push(Edge {
                    u,
                    v,
                    cost,
                    capacity: cap,
                });
            }
        }
    }

    let k = candidates.len();
    if k == 0 {
        return None;
    }

    let mut best_avg: Option<f64> = None;

    // Iterate over all subsets of candidate edges.
    // For each subset, if it satisfies the constraints, compute its average latency.
    for mask in 1..(1 << k) {
        let mut subset: Vec<Edge> = Vec::new();
        let mut total_cost: u32 = 0;
        for i in 0..k {
            if (mask >> i) & 1 == 1 {
                total_cost += candidates[i].cost;
                subset.push(candidates[i].clone());
            }
        }
        if total_cost > max_total_cost {
            continue;
        }

        // Check connectivity for the chosen subset.
        if !is_connected(n, &subset) {
            continue;
        }

        // Check fault tolerance requirement.
        if !check_fault_tolerance(n, &subset, fault_tolerance) {
            continue;
        }

        // Compute average latency using Dijkstra's algorithm on the weighted graph.
        let avg_latency = compute_average_latency(n, &subset);
        if let Some(current_best) = best_avg {
            if avg_latency < current_best {
                best_avg = Some(avg_latency);
            }
        } else {
            best_avg = Some(avg_latency);
        }
    }

    best_avg
}

// Helper: check if graph represented by chosen edges is connected.
fn is_connected(n: usize, edges: &Vec<Edge>) -> bool {
    let mut adj: Vec<Vec<usize>> = vec![Vec::new(); n];
    for edge in edges.iter() {
        adj[edge.u].push(edge.v);
        adj[edge.v].push(edge.u);
    }
    let mut visited = vec![false; n];
    let mut queue = VecDeque::new();
    queue.push_back(0);
    visited[0] = true;
    while let Some(u) = queue.pop_front() {
        for &v in &adj[u] {
            if !visited[v] {
                visited[v] = true;
                queue.push_back(v);
            }
        }
    }
    visited.iter().all(|&x| x)
}

// Helper: check fault-tolerance requirement.
// The requirement "at least fault_tolerance edge-disjoint paths" is equivalent to
// saying that removal of any set of (fault_tolerance - 1) edges should not disconnect the graph.
fn check_fault_tolerance(n: usize, edges: &Vec<Edge>, fault_tolerance: usize) -> bool {
    if fault_tolerance <= 1 {
        return true; // Only connectivity is required.
    }

    // For small graphs and small fault_tolerance, we check all combinations of (fault_tolerance - 1) edges removal.
    let removal_count = fault_tolerance - 1;
    let m = edges.len();
    let indices: Vec<usize> = (0..m).collect();
    let combinations = combinations(&indices, removal_count);
    for combo in combinations {
        // Build a new edge set excluding the edges in combo.
        let filtered: Vec<Edge> = edges
            .iter()
            .enumerate()
            .filter(|(i, _)| !combo.contains(i))
            .map(|(_, e)| e.clone())
            .collect();
        if !is_connected(n, &filtered) {
            return false;
        }
    }
    true
}

// Generate all combinations of indices of size r from the vector `data`.
fn combinations(data: &Vec<usize>, r: usize) -> Vec<Vec<usize>> {
    let mut result: Vec<Vec<usize>> = Vec::new();
    let mut comb: Vec<usize> = Vec::new();
    gen_combinations(data, r, 0, &mut comb, &mut result);
    result
}

fn gen_combinations(
    data: &Vec<usize>,
    r: usize,
    start: usize,
    comb: &mut Vec<usize>,
    result: &mut Vec<Vec<usize>>,
) {
    if comb.len() == r {
        result.push(comb.clone());
        return;
    }
    for i in start..data.len() {
        comb.push(data[i]);
        gen_combinations(data, r, i + 1, comb, result);
        comb.pop();
    }
}

// Compute average latency over all unordered pairs using Dijkstra for each source.
fn compute_average_latency(n: usize, edges: &Vec<Edge>) -> f64 {
    // Build weighted graph: for each edge, weight = 1.0 / (capacity as f64)
    let mut graph: Vec<Vec<(usize, f64)>> = vec![Vec::new(); n];
    for edge in edges.iter() {
        let weight = 1.0 / (edge.capacity as f64);
        graph[edge.u].push((edge.v, weight));
        graph[edge.v].push((edge.u, weight));
    }

    let mut total_latency = 0.0;
    let mut pair_count = 0;

    for src in 0..n {
        let dist = dijkstra(n, src, &graph);
        for dst in src + 1..n {
            total_latency += dist[dst];
            pair_count += 1;
        }
    }
    total_latency / (pair_count as f64)
}

// Simple Dijkstra's algorithm.
fn dijkstra(n: usize, src: usize, graph: &Vec<Vec<(usize, f64)>>) -> Vec<f64> {
    let mut dist = vec![std::f64::INFINITY; n];
    let mut visited = vec![false; n];
    dist[src] = 0.0;

    for _ in 0..n {
        let mut u = None;
        let mut best = std::f64::INFINITY;
        for i in 0..n {
            if !visited[i] && dist[i] < best {
                best = dist[i];
                u = Some(i);
            }
        }
        if let Some(u_idx) = u {
            visited[u_idx] = true;
            for &(v, w) in &graph[u_idx] {
                if !visited[v] && dist[u_idx] + w < dist[v] {
                    dist[v] = dist[u_idx] + w;
                }
            }
        }
    }

    dist
}