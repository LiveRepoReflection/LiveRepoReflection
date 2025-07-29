use std::collections::BinaryHeap;

#[derive(Clone)]
struct Edge {
    u: usize,
    v: usize,
    cost: u32,
}

pub fn min_average_cost(n: usize, input_edges: Vec<(usize, usize, u32)>, k: usize) -> Option<f64> {
    if n < 2 {
        return Some(0.0);
    }
    
    // Build graph for DFS disjoint paths.
    // For each undirected edge, we store it once.
    let mut edges = Vec::with_capacity(input_edges.len());
    let mut adj: Vec<Vec<usize>> = vec![Vec::new(); n];
    for (idx, &(u, v, cost)) in input_edges.iter().enumerate() {
        edges.push(Edge { u, v, cost });
        // Add edge index to both endpoints.
        adj[u].push(idx);
        adj[v].push(idx);
    }
    
    // Build graph for Dijkstra (shortest path computation).
    let mut dijk_adj: Vec<Vec<(usize, u32)>> = vec![Vec::new(); n];
    for &(u, v, cost) in input_edges.iter() {
        dijk_adj[u].push((v, cost));
        dijk_adj[v].push((u, cost));
    }
    
    let mut total_cost: u64 = 0;
    let mut pair_count: u64 = 0;
    
    // For every distinct pair (i, j) with i < j.
    for i in 0..n {
        for j in (i+1)..n {
            // Check for at least k edge-disjoint paths using repeated DFS.
            let mut used = vec![false; edges.len()];
            let mut count = 0;
            for _ in 0..k {
                let mut visited = vec![false; n];
                if dfs_find_path(i, j, &adj, &edges, &mut used, &mut visited) {
                    count += 1;
                } else {
                    break;
                }
            }
            if count < k {
                return None;
            }
            
            // Compute the minimum cost path between i and j using Dijkstra.
            if let Some(cost) = dijkstra(i, j, n, &dijk_adj) {
                total_cost += cost as u64;
            } else {
                return None;
            }
            pair_count += 1;
        }
    }
    
    let avg = total_cost as f64 / pair_count as f64;
    // Round to 6 decimal places.
    let rounded = (avg * 1e6).round() / 1e6;
    Some(rounded)
}

// DFS routine to find one simple path from s to t using only unused edges.
// Marks edges used permanently for the purpose of disjoint path counting.
fn dfs_find_path(s: usize, t: usize, adj: &Vec<Vec<usize>>, edges: &Vec<Edge>, used: &mut Vec<bool>, visited: &mut Vec<bool>) -> bool {
    if s == t {
        return true;
    }
    visited[s] = true;
    for &edge_idx in &adj[s] {
        if used[edge_idx] {
            continue;
        }
        let edge = &edges[edge_idx];
        let neighbor = if edge.u == s { edge.v } else { edge.u };
        if visited[neighbor] {
            continue;
        }
        used[edge_idx] = true; // Mark the edge as used in this disjoint path.
        if dfs_find_path(neighbor, t, adj, edges, used, visited) {
            return true;
        }
    }
    false
}

// Standard Dijkstra algorithm to compute the shortest path cost from src to dest.
fn dijkstra(src: usize, dest: usize, n: usize, adj: &Vec<Vec<(usize, u32)>>) -> Option<u32> {
    let mut dist = vec![u32::MAX; n];
    let mut heap = BinaryHeap::new();
    dist[src] = 0;
    heap.push(State { cost: 0, position: src });
    
    while let Some(State { cost, position }) = heap.pop() {
        if position == dest {
            return Some(cost);
        }
        if cost > dist[position] {
            continue;
        }
        for &(neighbor, edge_cost) in &adj[position] {
            let next = cost.saturating_add(edge_cost);
            if next < dist[neighbor] {
                dist[neighbor] = next;
                heap.push(State { cost: next, position: neighbor });
            }
        }
    }
    None
}

#[derive(Copy, Clone, Eq, PartialEq)]
struct State {
    cost: u32,
    position: usize,
}

impl Ord for State {
    fn cmp(&self, other: &State) -> std::cmp::Ordering {
        // Reverse order for min-heap.
        other.cost.cmp(&self.cost)
            .then_with(|| self.position.cmp(&other.position))
    }
}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &State) -> Option<std::cmp::Ordering> {
        Some(self.cmp(other))
    }
}