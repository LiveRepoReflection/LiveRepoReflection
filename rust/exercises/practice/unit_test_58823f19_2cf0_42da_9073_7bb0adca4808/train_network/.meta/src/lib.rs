pub fn min_cost_train_network(n: usize, routes: &[(usize, usize, u64, u64)], k: u64) -> Option<u64> {
    if n == 0 {
        return None;
    }
    if n == 1 {
        // Only one city: by definition, no pairs to connect, so cost is 0.
        return Some(0);
    }
    let m = routes.len();
    let mut best: Option<u64> = None;
    
    // Iterate over all subsets of routes.
    // Since test cases are small, a full power‐set enumeration is acceptable.
    let total_subsets = 1 << m;
    for mask in 0..total_subsets {
        let mut cost = 0u64;
        // Build graph in the form of an edge list (for connectivity check)
        let mut graph_edges: Vec<(usize, usize, u64)> = Vec::new();
        // Build capacity matrix (we will fill after connectivity check)
        // We'll compute connectivity using a simple DFS.
        for i in 0..m {
            if (mask >> i) & 1 == 1 {
                let (u, v, edge_cost, _capacity) = routes[i];
                cost = cost.saturating_add(edge_cost);
                graph_edges.push((u, v, 0)); // capacities not needed for connectivity
            }
        }
        // Prune if cost is already not promising.
        if let Some(best_cost) = best {
            if cost >= best_cost {
                continue;
            }
        }
        if !is_connected(n, &graph_edges) {
            continue;
        }
        // Build capacity matrix for n nodes.
        let mut cap = vec![vec![0u64; n]; n];
        for i in 0..m {
            if (mask >> i) & 1 == 1 {
                let (u, v, _edge_cost, capacity) = routes[i];
                // Since graph is undirected, aggregate capacities.
                cap[u][v] = cap[u][v].saturating_add(capacity);
                cap[v][u] = cap[v][u].saturating_add(capacity);
            }
        }
        // Use Stoer-Wagner to compute global min cut of this subgraph.
        let min_cut = stoer_wagner(&cap);
        if min_cut >= k {
            best = match best {
                Some(current_best) => Some(current_best.min(cost)),
                None => Some(cost),
            };
        }
    }
    best
}

// Helper function: Check connectivity using DFS.
fn is_connected(n: usize, edges: &[(usize, usize, u64)]) -> bool {
    let mut adj = vec![Vec::new(); n];
    for &(u, v, _) in edges {
        adj[u].push(v);
        adj[v].push(u);
    }
    let mut visited = vec![false; n];
    dfs(0, &adj, &mut visited);
    visited.into_iter().all(|v| v)
}

fn dfs(node: usize, adj: &Vec<Vec<usize>>, visited: &mut Vec<bool>) {
    if visited[node] {
        return;
    }
    visited[node] = true;
    for &nbr in &adj[node] {
        if !visited[nbr] {
            dfs(nbr, adj, visited);
        }
    }
}

// Stoer-Wagner min cut algorithm implementation.
// This algorithm works on undirected graphs represented by a capacity matrix.
fn stoer_wagner(cap: &Vec<Vec<u64>>) -> u64 {
    let n = cap.len();
    // Create a vector of active vertices.
    let mut vertices: Vec<usize> = (0..n).collect();
    // Make a mutable copy of the capacity matrix.
    let mut graph = cap.clone();
    let mut best_cut = u64::MAX;
    
    while vertices.len() > 1 {
        let len = vertices.len();
        // 'used' will track if a vertex has been added to the set A.
        let mut used = vec![false; n];
        // 'weights' will track the connectivity weights to A.
        let mut weights = vec![0u64; n];
        let mut prev = vertices[0];
        used[prev] = true;
        
        for _ in 1..len {
            // In each iteration, select the most tightly connected vertex not in A.
            let mut next = None;
            for &v in &vertices {
                if !used[v] {
                    weights[v] = weights[v].saturating_add(graph[prev][v]);
                    if next.is_none() || weights[v] > weights[next.unwrap()] {
                        next = Some(v);
                    }
                }
            }
            // In the last iteration of the inner loop, next is the last vertex added.
            if let Some(next_v) = next {
                used[next_v] = true;
                // If this is the last vertex added, then the cut weight is weights[next_v].
                // It is a candidate for the global min cut.
                if weights[next_v] < best_cut {
                    best_cut = weights[next_v];
                }
                prev = next_v;
            }
        }
        
        // Merge 'prev' and the vertex before it.
        // Find the vertex s that was added just before prev.
        let mut s = None;
        {
            let mut max_weight = 0;
            for &v in &vertices {
                if v != prev && used[v] && weights[v] > max_weight {
                    max_weight = weights[v];
                    s = Some(v);
                }
            }
        }
        let s = s.unwrap_or(prev);
        
        // Merge vertex 'prev' into vertex 's'.
        // Update the graph: for every vertex, add edges from 'prev' to that vertex into s.
        for &v in &vertices {
            if v == s || v == prev {
                continue;
            }
            graph[s][v] = graph[s][v].saturating_add(graph[prev][v]);
            graph[v][s] = graph[s][v];
        }
        
        // Remove vertex 'prev' from vertices.
        vertices.retain(|&vertex| vertex != prev);
    }
    
    best_cut
}

#[cfg(test)]
mod tests {
    use super::min_cost_train_network;

    #[test]
    fn test_single_city() {
        let n = 1;
        let routes: Vec<(usize, usize, u64, u64)> = vec![];
        // When there is a single city, there are no pairs to satisfy,
        // so the cost should be 0.
        let k = 5;
        let res = min_cost_train_network(n, &routes, k);
        assert_eq!(res, Some(0));
    }

    #[test]
    fn test_simple_network() {
        let n = 4;
        let routes = vec![
            (0, 1, 10, 5),
            (1, 2, 20, 7),
            (2, 3, 30, 9),
        ];
        // Spanning tree: (0,1), (1,2), (2,3) with total cost 10+20+30 = 60.
        // Minimum capacity on this network is min(5,7,9)=5, which satisfies K=4.
        let k = 4;
        let res = min_cost_train_network(n, &routes, k);
        assert_eq!(res, Some(60));
    }

    #[test]
    fn test_redundant_routes() {
        let n = 4;
        let routes = vec![
            (0, 1, 10, 5),
            (0, 2, 15, 3),
            (1, 2, 20, 7),
            (1, 3, 25, 2),
            (2, 3, 30, 9),
        ];
        // Although there are extra routes, the optimal network can be obtained by choosing
        // the spanning tree: (0,1) [10,5], (1,2) [20,7], (2,3) [30,9] for a total cost of 60,
        // which satisfies the minimum capacity K=4.
        let k = 4;
        let res = min_cost_train_network(n, &routes, k);
        assert_eq!(res, Some(60));
    }

    #[test]
    fn test_disconnected_network() {
        let n = 3;
        let routes = vec![
            (0, 1, 10, 5),
            (1, 2, 20, 7),
        ];
        // The spanning tree here would yield a path 0-1-2.
        // However, the minimum capacity on this path is min(5,7)=5, which is below the requirement of K=6.
        // Thus, no valid network can be constructed.
        let k = 6;
        let res = min_cost_train_network(n, &routes, k);
        assert_eq!(res, None);
    }

    #[test]
    fn test_multiple_routes_same_cities() {
        let n = 3;
        let routes = vec![
            (0, 1, 10, 5),
            (0, 1, 15, 8),
            (1, 2, 20, 5),
            (1, 2, 10, 6),
        ];
        // The optimal solution would choose the cheaper edge among duplicates:
        // For example: (0, 1) with cost 10 and capacity 5, (1, 2) with cost 10 and capacity 6.
        // Total cost = 10 + 10 = 20, meeting the minimum capacity K=5.
        let k = 5;
        let res = min_cost_train_network(n, &routes, k);
        assert_eq!(res, Some(20));
    }

    #[test]
    fn test_cycle_network() {
        let n = 5;
        let routes = vec![
            (0, 1, 10, 10),
            (1, 2, 10, 3),
            (2, 3, 10, 10),
            (3, 4, 10, 10),
            (4, 0, 50, 10),
            (1, 3, 30, 4),
        ];
        // A possible optimal network to satisfy minimum capacity K=4:
        // One possibility: choose edges (0,1)[10,10], (1,3)[30,4], (2,3)[10,10], (3,4)[10,10].
        // This yields total cost 10+30+10+10 = 60 and the global min cut is at least 4.
        let k = 4;
        let res = min_cost_train_network(n, &routes, k);
        assert_eq!(res, Some(60));
    }
}