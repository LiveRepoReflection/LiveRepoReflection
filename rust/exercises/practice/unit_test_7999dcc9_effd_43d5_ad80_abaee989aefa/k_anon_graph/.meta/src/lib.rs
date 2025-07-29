use std::collections::VecDeque;

pub fn anonymize_graph(n: usize, edges: Vec<(usize, usize)>, k: usize) -> Vec<(usize, usize)> {
    if n == 0 {
        return Vec::new();
    }
    // Build graph using adjacency lists, ignoring self-loops.
    let mut adj: Vec<Vec<usize>> = vec![Vec::new(); n];
    let mut degree: Vec<usize> = vec![0; n];
    for (u, v) in edges.iter() {
        if u == v {
            continue;
        }
        adj[*u].push(*v);
        adj[*v].push(*u);
        degree[*u] += 1;
        degree[*v] += 1;
    }
    // Use a queue to iteratively remove nodes with degree less than k.
    let mut removed: Vec<bool> = vec![false; n];
    let mut queue: VecDeque<usize> = VecDeque::new();
    for i in 0..n {
        if degree[i] < k {
            queue.push_back(i);
        }
    }
    while let Some(u) = queue.pop_front() {
        if removed[u] {
            continue;
        }
        removed[u] = true;
        for &v in &adj[u] {
            if !removed[v] {
                degree[v] = degree[v].saturating_sub(1);
                if degree[v] < k {
                    queue.push_back(v);
                }
            }
        }
    }
    // Produce the resulting edges from the original input, excluding self-loops and edges
    // incident to removed nodes.
    let mut result: Vec<(usize, usize)> = Vec::new();
    for (u, v) in edges.into_iter() {
        if u == v {
            continue;
        }
        if !removed[u] && !removed[v] {
            result.push((u, v));
        }
    }
    result
}