use std::collections::BTreeSet;

pub fn min_cut(n: usize, edges: Vec<(usize, usize)>, k: usize) -> i32 {
    // Build the undirected graph as an adjacency list.
    let mut graph = vec![Vec::new(); n];
    for (u, v) in edges {
        if u < n && v < n {
            graph[u].push(v);
            graph[v].push(u);
        }
    }
    // Sort neighbor lists for predictable order.
    for nbrs in graph.iter_mut() {
        nbrs.sort_unstable();
    }

    // Check initial connectivity: if any connected component already has size <= k, no cuts needed.
    let mut visited = vec![false; n];
    for i in 0..n {
        if !visited[i] {
            let mut comp = Vec::new();
            let mut stack = vec![i];
            visited[i] = true;
            while let Some(u) = stack.pop() {
                comp.push(u);
                for &v in &graph[u] {
                    if !visited[v] {
                        visited[v] = true;
                        stack.push(v);
                    }
                }
            }
            if comp.len() <= k {
                return 0;
            }
        }
    }

    // Global minimum cut edge count (set to a large value initially).
    let mut global_min = usize::MAX;
    let mut in_set = vec![false; n];

    // Enumerate all connected subgraphs with size at most k.
    // To avoid duplicates, we force the smallest node in the subgraph to be the start.
    for start in 0..n {
        in_set[start] = true;
        let mut s_vec = vec![start];
        let mut frontier = BTreeSet::new();
        for &nbr in &graph[start] {
            if nbr >= start && !in_set[nbr] {
                frontier.insert(nbr);
            }
        }
        dfs(&graph, &mut in_set, &mut s_vec, frontier, start, k, &mut global_min);
        in_set[start] = false;
    }

    if global_min == usize::MAX {
        -1
    } else {
        global_min as i32
    }
}

// Recursive DFS that enumerates all connected subgraphs with size <= k,
// where every subgraph has the smallest element equal to 'start'.
fn dfs(
    graph: &Vec<Vec<usize>>,
    in_set: &mut Vec<bool>,
    s_vec: &mut Vec<usize>,
    frontier: BTreeSet<usize>,
    start: usize,
    k: usize,
    global_min: &mut usize,
) {
    // Calculate the cut: count edges from nodes in s_vec to nodes not in the subgraph.
    let current_cut = compute_cut(graph, in_set, s_vec);
    if current_cut < *global_min {
        *global_min = current_cut;
    }

    if s_vec.len() == k {
        return;
    }

    // Iterate over a snapshot of the current frontier.
    let candidates: Vec<usize> = frontier.iter().cloned().collect();
    for candidate in candidates {
        let mut new_frontier = frontier.clone();
        new_frontier.remove(&candidate);
        in_set[candidate] = true;
        s_vec.push(candidate);
        // Add neighbors of the candidate to the frontier if they meet the criteria.
        for &nbr in &graph[candidate] {
            if !in_set[nbr] && nbr >= start {
                new_frontier.insert(nbr);
            }
        }
        dfs(graph, in_set, s_vec, new_frontier, start, k, global_min);
        s_vec.pop();
        in_set[candidate] = false;
    }
}

// Computes the number of edges crossing from the subgraph (S) to its complement.
// Each edge from a node in S to a node not in S is counted once.
fn compute_cut(graph: &Vec<Vec<usize>>, in_set: &Vec<bool>, s_vec: &Vec<usize>) -> usize {
    let mut cut = 0;
    for &u in s_vec {
        for &v in &graph[u] {
            if !in_set[v] {
                cut += 1;
            }
        }
    }
    cut
}