use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn find_route(
    n: usize,
    resource_limits: Vec<u64>,
    edges: Vec<(usize, usize, u64)>,
    start_node: usize,
    end_node: usize,
    required_resource: u64,
    max_total_cost: u64,
) -> Option<(u64, Vec<usize>)> {
    // Check if destination node meets required resource.
    if resource_limits[end_node] < required_resource {
        return None;
    }
    // Build adjacency list.
    let mut adj: Vec<Vec<(usize, u64)>> = vec![Vec::new(); n];
    for (u, v, cost) in edges {
        adj[u].push((v, cost));
    }
    
    // Prepare candidate resource limits.
    // Only consider resource limits that are >= both start and end node.
    let lower_bound = resource_limits[start_node].max(resource_limits[end_node]);
    let mut candidates: Vec<u64> = resource_limits
        .iter()
        .copied()
        .filter(|&r| r >= lower_bound)
        .collect();
    candidates.sort_unstable();
    candidates.dedup();
    
    // Binary search for the minimal candidate T for which a valid route exists.
    let mut lo = 0;
    let mut hi = candidates.len();
    let mut best_path: Option<(u64, Vec<usize>)> = None;
    while lo < hi {
        let mid = (lo + hi) / 2;
        let candidate = candidates[mid];
        if let Some((path_edges, total_cost, path)) =
            dijkstra(n, &resource_limits, &adj, start_node, end_node, candidate, max_total_cost)
        {
            // Found a valid path with candidate as upper bound.
            // Because we restrict nodes to those with resource limit <= candidate,
            // the maximum resource on the path is at most candidate.
            // We try to lower candidate.
            best_path = Some((compute_max_resource(&resource_limits, &path), path));
            hi = mid;
        } else {
            lo = mid + 1;
        }
    }
    best_path
}

fn compute_max_resource(resource_limits: &Vec<u64>, path: &Vec<usize>) -> u64 {
    path.iter().map(|&node| resource_limits[node]).max().unwrap_or(0)
}

fn dijkstra(
    n: usize,
    resource_limits: &Vec<u64>,
    adj: &Vec<Vec<(usize, u64)>>,
    start_node: usize,
    end_node: usize,
    candidate_limit: u64,
    max_total_cost: u64,
) -> Option<(usize, u64, Vec<usize>)> {
    // We will only consider nodes whose resource limit <= candidate_limit.
    // Use Dijkstra variant with lexicographic ordering:
    // Prioritize fewer edges, then lower total cost.
    // State: (edge_count, total_cost, node)
    let mut dist: Vec<Option<(usize, u64)>> = vec![None; n];
    let mut prev: Vec<Option<usize>> = vec![None; n];
    let mut heap = BinaryHeap::new();
    
    // Check that start_node satisfies candidate condition.
    if resource_limits[start_node] > candidate_limit {
        return None;
    }
    
    dist[start_node] = Some((0, 0));
    heap.push(Reverse((0, 0, start_node))); // (edge_count, cost, node)
    
    while let Some(Reverse((edge_count, cost, node))) = heap.pop() {
        // If we have already a better way, skip.
        if let Some((best_edge, best_cost)) = dist[node] {
            if edge_count > best_edge || cost > best_cost {
                continue;
            }
        }
        if node == end_node {
            // Return early; found optimal in lex order.
            let path = reconstruct_path(start_node, end_node, &prev);
            return Some((edge_count, cost, path));
        }
        for &(nbr, edge_cost) in &adj[node] {
            // Only consider neighbor if its resource limit is <= candidate_limit.
            if resource_limits[nbr] > candidate_limit {
                continue;
            }
            let new_cost = cost.saturating_add(edge_cost);
            if new_cost > max_total_cost {
                continue;
            }
            let new_edge_count = edge_count + 1;
            let update = match dist[nbr] {
                None => true,
                Some((prev_edge_count, prev_cost)) => {
                    // Lexicographic comparison: first compare edge_count, then cost.
                    (new_edge_count < prev_edge_count)
                        || (new_edge_count == prev_edge_count && new_cost < prev_cost)
                }
            };
            if update {
                dist[nbr] = Some((new_edge_count, new_cost));
                prev[nbr] = Some(node);
                heap.push(Reverse((new_edge_count, new_cost, nbr)));
            }
        }
    }
    None
}

fn reconstruct_path(start: usize, end: usize, prev: &Vec<Option<usize>>) -> Vec<usize> {
    let mut path = Vec::new();
    let mut current = end;
    path.push(current);
    while current != start {
        if let Some(p) = prev[current] {
            current = p;
            path.push(current);
        } else {
            break;
        }
    }
    path.reverse();
    path
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_valid_route_shorter_path() {
        // Test with two possible paths:
        // Path A: 0 -> 1 -> 4 with cost: 5+10 = 15, maximum resource = max(5,15,30)=30.
        // Path B: 0 -> 2 -> 3 -> 4 with cost: 3+4+5 = 12, maximum resource = max(5,10,20,30)=30.
        // Expect the path with fewer edges (Path A).
        let n = 5;
        let resource_limits = vec![5, 15, 10, 20, 30];
        let edges = vec![
            (0, 1, 5),
            (1, 4, 10),
            (0, 2, 3),
            (2, 3, 4),
            (3, 4, 5),
        ];
        let start_node = 0;
        let end_node = 4;
        let required_resource = 25;
        let max_total_cost = 20;
        
        let result = find_route(n, resource_limits.clone(), edges.clone(), start_node, end_node, required_resource, max_total_cost);
        
        let expected_resource_usage = 30;
        let expected_path = vec![0, 1, 4];
        
        assert!(result.is_some(), "Expected a valid route, got None");
        let (res_usage, path) = result.unwrap();
        assert_eq!(res_usage, expected_resource_usage, "Resource usage does not match");
        assert_eq!(path, expected_path, "Path does not match expected shorter path");
    }
    
    #[test]
    fn test_no_route_due_to_cost() {
        // Test where the path cost exceeds max_total_cost.
        let n = 3;
        let resource_limits = vec![20, 30, 40];
        let edges = vec![
            (0, 1, 100),
            (1, 2, 100),
        ];
        let start_node = 0;
        let end_node = 2;
        let required_resource = 35;
        let max_total_cost = 50;
        
        let result = find_route(n, resource_limits, edges, start_node, end_node, required_resource, max_total_cost);
        assert!(result.is_none(), "Expected None due to cost constraint");
    }
    
    #[test]
    fn test_insufficient_destination_resource() {
        // Test where the destination node's resource is insufficient.
        let n = 3;
        let resource_limits = vec![50, 60, 20]; // destination node 2 has 20, required is 25.
        let edges = vec![
            (0, 1, 10),
            (1, 2, 10),
        ];
        let start_node = 0;
        let end_node = 2;
        let required_resource = 25;
        let max_total_cost = 50;
        
        let result = find_route(n, resource_limits, edges, start_node, end_node, required_resource, max_total_cost);
        assert!(result.is_none(), "Expected None due to destination resource constraint");
    }
    
    #[test]
    fn test_multiple_paths_different_resource_usage() {
        // Test with two paths where resource usage differs:
        // Path A: 0 -> 1 -> 3 with cost: 5+15=20, max resource = max(10,20,30)=30.
        // Path B: 0 -> 2 -> 3 with cost: 10+5=15, max resource = max(10,40,30)=40.
        // Optimal is Path A.
        let n = 4;
        let resource_limits = vec![10, 20, 40, 30];
        let edges = vec![
            (0, 1, 5),
            (1, 3, 15),
            (0, 2, 10),
            (2, 3, 5),
        ];
        let start_node = 0;
        let end_node = 3;
        let required_resource = 25;
        let max_total_cost = 30;
        
        let result = find_route(n, resource_limits, edges, start_node, end_node, required_resource, max_total_cost);
        
        let expected_resource_usage = 30;
        let expected_path = vec![0, 1, 3];
        
        assert!(result.is_some(), "Expected a valid route");
        let (res_usage, path) = result.unwrap();
        assert_eq!(res_usage, expected_resource_usage, "Resource usage does not match expected optimal value");
        assert_eq!(path, expected_path, "Path does not match expected optimal path");
    }
    
    #[test]
    fn test_start_equals_end() {
        // Test when start and end are the same.
        let n = 1;
        let resource_limits = vec![100];
        let edges: Vec<(usize, usize, u64)> = vec![];
        let start_node = 0;
        let end_node = 0;
        let required_resource = 50;
        let max_total_cost = 0;
        
        let result = find_route(n, resource_limits, edges, start_node, end_node, required_resource, max_total_cost);
        
        let expected_resource_usage = 100;
        let expected_path = vec![0];
        
        assert!(result.is_some(), "Expected a valid route for start equals end");
        let (res_usage, path) = result.unwrap();
        assert_eq!(res_usage, expected_resource_usage, "Resource usage mismatch for single node route");
        assert_eq!(path, expected_path, "Path mismatch for single node route");
    }
    
    #[test]
    fn test_tie_break_fewer_edges() {
        // Test tie-breaker: when multiple paths yield the same maximum resource usage,
        // choose the one with fewer edges.
        // Paths:
        // Path A: 0 -> 1 -> 4 with cost: 5+10 = 15, max resource = max(10,50,60) = 60.
        // Path B: 0 -> 4 direct with cost: 25, max resource = max(10,60) = 60.
        // Path C: 0 -> 2 -> 3 -> 4 with cost: 5+5+10 = 20, max resource = max(10,20,40,60) = 60.
        // Optimal is Path B.
        let n = 5;
        let resource_limits = vec![10, 50, 20, 40, 60];
        let edges = vec![
            (0, 1, 5),
            (1, 4, 10),
            (0, 2, 5),
            (2, 3, 5),
            (3, 4, 10),
            (0, 4, 25),
        ];
        let start_node = 0;
        let end_node = 4;
        let required_resource = 50;
        let max_total_cost = 30;
        
        let result = find_route(n, resource_limits, edges, start_node, end_node, required_resource, max_total_cost);
        
        let expected_resource_usage = 60;
        let expected_path = vec![0, 4];
        
        assert!(result.is_some(), "Expected a valid route");
        let (res_usage, path) = result.unwrap();
        assert_eq!(res_usage, expected_resource_usage, "Resource usage mismatch in tie-break scenario");
        assert_eq!(path, expected_path, "Path mismatch in tie-break scenario");
    }
}