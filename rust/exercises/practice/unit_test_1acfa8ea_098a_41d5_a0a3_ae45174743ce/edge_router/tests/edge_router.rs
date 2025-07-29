use std::collections::HashSet;
use std::collections::VecDeque;
use edge_router::deploy_edge_routers;

fn compute_total_score(
    num_users: usize,
    edges: &Vec<(usize, usize)>,
    influence_scores: &Vec<usize>,
    hosting_costs: &Vec<usize>,
    routers: &Vec<usize>,
) -> f64 {
    // Build graph as an adjacency list.
    let mut graph: Vec<Vec<usize>> = vec![vec![]; num_users];
    for &(u, v) in edges {
        graph[u].push(v);
        graph[v].push(u);
    }

    let mut total = 0.0;
    for node in 0..num_users {
        if routers.contains(&node) {
            total += influence_scores[node] as f64;
        } else {
            // Use BFS to compute the shortest distance to any router.
            let mut dist: Vec<Option<usize>> = vec![None; num_users];
            let mut queue: VecDeque<usize> = VecDeque::new();
            dist[node] = Some(0);
            queue.push_back(node);
            let mut min_distance = None;
            while let Some(cur) = queue.pop_front() {
                if routers.contains(&cur) {
                    min_distance = dist[cur];
                    break;
                }
                for &nbr in &graph[cur] {
                    if dist[nbr].is_none() {
                        dist[nbr] = Some(dist[cur].unwrap() + 1);
                        queue.push_back(nbr);
                    }
                }
            }
            if let Some(d) = min_distance {
                total += (influence_scores[node] as f64) / ((d + 1) as f64);
            }
        }
    }
    let hosting: usize = routers.iter().map(|&r| hosting_costs[r]).sum();
    total - (hosting as f64)
}

#[test]
fn test_linear_graph() {
    // Simple chain graph.
    let num_users = 5;
    let edges = vec![(0, 1), (1, 2), (2, 3), (3, 4)];
    let influence_scores = vec![10, 15, 20, 12, 8];
    let hosting_costs = vec![5, 7, 9, 6, 4];
    let k = 2;
    let routers = deploy_edge_routers(num_users, edges.clone(), influence_scores.clone(), hosting_costs.clone(), k);
    assert_eq!(routers.len(), k);
    let unique: HashSet<_> = routers.iter().collect();
    assert_eq!(unique.len(), k);
    for &r in routers.iter() {
        assert!(r < num_users);
    }
    let score = compute_total_score(num_users, &edges, &influence_scores, &hosting_costs, &routers);
    assert!(score > -1000.0);
}

#[test]
fn test_star_graph() {
    // Star graph: one central hub with multiple leaves.
    let num_users = 6;
    let edges = vec![(0, 1), (0, 2), (0, 3), (0, 4), (0, 5)];
    let influence_scores = vec![50, 10, 10, 10, 10, 10];
    let hosting_costs = vec![20, 5, 5, 5, 5, 5];
    let k = 1;
    let routers = deploy_edge_routers(num_users, edges.clone(), influence_scores.clone(), hosting_costs.clone(), k);
    assert_eq!(routers.len(), k);
    let unique: HashSet<_> = routers.iter().collect();
    assert_eq!(unique.len(), k);
    for &r in routers.iter() {
        assert!(r < num_users);
    }
    let score = compute_total_score(num_users, &edges, &influence_scores, &hosting_costs, &routers);
    assert!(score > 0.0);
}

#[test]
fn test_disconnected_graph() {
    // Two disconnected components.
    // Component 1: nodes 0-2 in a chain.
    // Component 2: nodes 3 and 4 connected by an edge.
    let num_users = 5;
    let edges = vec![(0, 1), (1, 2), (3, 4)];
    let influence_scores = vec![20, 30, 25, 15, 10];
    let hosting_costs = vec![5, 5, 5, 5, 5];
    let k = 2;
    let routers = deploy_edge_routers(num_users, edges.clone(), influence_scores.clone(), hosting_costs.clone(), k);
    assert_eq!(routers.len(), k);
    let unique: HashSet<_> = routers.iter().collect();
    assert_eq!(unique.len(), k);
    for &r in routers.iter() {
        assert!(r < num_users);
    }
    let score = compute_total_score(num_users, &edges, &influence_scores, &hosting_costs, &routers);
    assert!(score > 0.0);
}

#[test]
fn test_identical_scores_and_costs() {
    // All nodes have identical influence scores and hosting costs.
    let num_users = 7;
    let edges = vec![(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 0)];
    let influence_scores = vec![10; 7];
    let hosting_costs = vec![3; 7];
    let k = 3;
    let routers = deploy_edge_routers(num_users, edges.clone(), influence_scores.clone(), hosting_costs.clone(), k);
    assert_eq!(routers.len(), k);
    let unique: HashSet<_> = routers.iter().collect();
    assert_eq!(unique.len(), k);
    for &r in routers.iter() {
        assert!(r < num_users);
    }
    let score = compute_total_score(num_users, &edges, &influence_scores, &hosting_costs, &routers);
    assert!(score > 0.0);
}

#[test]
fn test_complex_graph() {
    // More complex graph with 10 nodes.
    let num_users = 10;
    let edges = vec![
        (0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6),
        (3, 7), (4, 7), (5, 8), (6, 8), (7, 9), (8, 9)
    ];
    let influence_scores = vec![10, 20, 15, 30, 25, 18, 22, 35, 40, 28];
    let hosting_costs = vec![5, 8, 6, 10, 7, 5, 8, 12, 9, 6];
    let k = 3;
    let routers = deploy_edge_routers(num_users, edges.clone(), influence_scores.clone(), hosting_costs.clone(), k);
    assert_eq!(routers.len(), k);
    let unique: HashSet<_> = routers.iter().collect();
    assert_eq!(unique.len(), k);
    for &r in routers.iter() {
        assert!(r < num_users);
    }
    let score = compute_total_score(num_users, &edges, &influence_scores, &hosting_costs, &routers);
    assert!(score > 0.0);
}