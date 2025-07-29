pub fn max_population_coverage(
    graph: Vec<(usize, usize, usize)>,
    population: Vec<usize>,
    budget: usize,
    radius: usize,
) -> f64 {
    let n = population.len();
    if n == 0 {
        return 0.0;
    }

    // Build all pairs shortest paths using Floyd–Warshall.
    // Use a large INF value.
    let inf: u64 = 1_000_000_000_000;
    let mut dist = vec![vec![inf; n]; n];
    for i in 0..n {
        dist[i][i] = 0;
    }
    for &(u, v, w) in &graph {
        if u < n && v < n {
            let w_u64 = w as u64;
            if w_u64 < dist[u][v] {
                dist[u][v] = w_u64;
                dist[v][u] = w_u64;
            }
        }
    }
    for k in 0..n {
        for i in 0..n {
            for j in 0..n {
                if dist[i][k] + dist[k][j] < dist[i][j] {
                    dist[i][j] = dist[i][k] + dist[k][j];
                }
            }
        }
    }

    // Greedy heuristic:
    // S will store the indices of selected base stations.
    // interference_counts will store, for each selected node, how many nodes (including itself)
    // are within the interference radius (i.e. number of nodes in S that are "close enough").
    let mut selected: Vec<usize> = Vec::new();
    let mut interferences: Vec<usize> = Vec::new();
    let mut remaining_budget = budget as u64;

    // Define a helper function to calculate the connection cost for a candidate.
    // If no base station is selected, cost is 0.
    let connection_cost = |i: usize, selected: &Vec<usize>| -> u64 {
        if selected.is_empty() {
            0
        } else {
            let mut cost = inf;
            for &s in selected.iter() {
                if dist[i][s] < cost {
                    cost = dist[i][s];
                }
            }
            cost
        }
    };

    // Compute incremental benefit if we add candidate i.
    // Benefit = candidate's effective coverage when added + change in effective coverage for already selected ones.
    let compute_delta = |i: usize,
                           selected: &Vec<usize>,
                           interferences: &Vec<usize>| -> f64 {
        // For candidate i, interference count if added will be:
        let mut cand_interference = 1; // it interferes with itself
        for &s in selected.iter() {
            if dist[i][s] <= radius as u64 {
                cand_interference += 1;
            }
        }
        let cand_eff = population[i] as f64 / (cand_interference as f64);

        // For each already selected node j that is within radius of candidate i,
        // its effective coverage will be reduced.
        let mut delta_existing = 0.0;
        for (idx, &s) in selected.iter().enumerate() {
            if dist[i][s] <= radius as u64 {
                let current = interferences[idx] as f64;
                let new_val = (interferences[idx] + 1) as f64;
                // The effective coverage of node s changes from:
                // population[s] / current to population[s] / new_val.
                delta_existing += (population[s] as f64) / new_val - (population[s] as f64) / current;
            }
        }
        cand_eff + delta_existing
    };

    // Greedily add candidate stations until no candidate can be added or budget runs out.
    loop {
        let mut best_candidate: Option<usize> = None;
        let mut best_ratio: f64 = -1e18;
        let mut best_delta: f64 = 0.0;
        let mut best_cost: u64 = 0;

        for i in 0..n {
            if selected.contains(&i) {
                continue;
            }
            let cost = connection_cost(i, &selected);
            if cost > remaining_budget {
                continue;
            }
            let delta = compute_delta(i, &selected, &interferences);
            // We only consider candidates that improve the overall effective coverage.
            if delta <= 0.0 {
                continue;
            }
            // If connection cost is 0, choose it if delta is positive.
            let ratio = if cost == 0 { delta * 1e6 } else { delta / (cost as f64) };
            if ratio > best_ratio {
                best_ratio = ratio;
                best_candidate = Some(i);
                best_delta = delta;
                best_cost = cost;
            }
        }

        match best_candidate {
            Some(i) => {
                // If the connection cost is within remaining budget, select candidate i.
                if best_cost > remaining_budget {
                    break;
                }
                remaining_budget -= best_cost;
                // Update interference counts for already selected nodes.
                for (idx, &s) in selected.iter().enumerate() {
                    if dist[i][s] <= radius as u64 {
                        interferences[idx] += 1;
                    }
                }
                // For the new candidate, interference count is 1 plus number of selected nodes that are within radius.
                let mut cand_interference = 1;
                for &s in selected.iter() {
                    if dist[i][s] <= radius as u64 {
                        cand_interference += 1;
                    }
                }
                selected.push(i);
                interferences.push(cand_interference);
            }
            None => break,
        }
    }

    // Compute total effective coverage.
    let mut total_effective = 0.0;
    for (idx, &i) in selected.iter().enumerate() {
        total_effective += population[i] as f64 / (interferences[idx] as f64);
    }
    total_effective
}

#[cfg(test)]
mod tests {
    use super::max_population_coverage;
    const EPS: f64 = 1e-6;

    #[test]
    fn test_empty_graph() {
        let graph: Vec<(usize, usize, usize)> = vec![];
        let population: Vec<usize> = vec![];
        let budget = 100;
        let radius = 10;
        let result = max_population_coverage(graph, population, budget, radius);
        let expected = 0.0;
        assert!((result - expected).abs() < EPS, "Expected {}, got {}", expected, result);
    }

    #[test]
    fn test_budget_zero() {
        // With budget 0, only one base station can be chosen (with zero connection cost).
        // The optimal choice is the one with maximum population.
        let graph = vec![(0, 1, 2), (1, 2, 2), (0, 2, 4)];
        let population = vec![30, 10, 20];
        let budget = 0;
        let radius = 3;
        let result = max_population_coverage(graph, population, budget, radius);
        let expected = 30.0;
        assert!((result - expected).abs() < EPS, "Expected {}, got {}", expected, result);
    }

    #[test]
    fn test_single_node() {
        // A single node with no edges should return its own population value.
        let graph: Vec<(usize, usize, usize)> = vec![];
        let population = vec![100];
        let budget = 50;
        let radius = 5;
        let result = max_population_coverage(graph, population, budget, radius);
        let expected = 100.0;
        assert!((result - expected).abs() < EPS, "Expected {}, got {}", expected, result);
    }

    #[test]
    fn test_cycle_graph() {
        // Four nodes arranged in a cycle.
        // Optimal selection in this heuristic should be close to choosing nodes 0 and 2,
        // yielding effective coverage of 100 + 80 = 180.
        let graph = vec![
            (0, 1, 5),
            (1, 2, 5),
            (2, 3, 5),
            (3, 0, 5),
            (0, 2, 8),
            (1, 3, 8)
        ];
        let population = vec![100, 50, 80, 20];
        let budget = 10;
        let radius = 6;
        let result = max_population_coverage(graph, population, budget, radius);
        let expected = 180.0;
        assert!((result - expected).abs() < EPS, "Expected {}, got {}", expected, result);
    }

    #[test]
    fn test_complete_graph() {
        // A complete graph of 3 nodes where every two nodes are connected with cost 1.
        // The MST cost for spanning three nodes is 1+1 = 2 (which is equal to the budget).
        // All nodes interfere with each other because all pairwise distances (1) are within R = 2.
        // Effective coverage of each node becomes 50/3, summing up to 50.
        let graph = vec![(0, 1, 1), (1, 2, 1), (0, 2, 1)];
        let population = vec![50, 50, 50];
        let budget = 2;
        let radius = 2;
        let result = max_population_coverage(graph, population, budget, radius);
        let expected = 50.0;
        assert!((result - expected).abs() < EPS, "Expected {}, got {}", expected, result);
    }

    #[test]
    fn test_chain_graph() {
        // A chain graph of 5 nodes with edges of cost 2.
        // With radius R = 3, adjacent nodes interfere, but nodes separated by one vertex do not.
        // The optimal selection is to deploy nodes 2 and 4:
        // - The cable to connect them goes through the chain within the budget of 6.
        // - Since the distance between nodes 2 and 4 is 4 (> R), they do not interfere.
        // Total effective coverage = 30 + 50 = 80.
        let graph = vec![(0, 1, 2), (1, 2, 2), (2, 3, 2), (3, 4, 2)];
        let population = vec![10, 20, 30, 40, 50];
        let budget = 6;
        let radius = 3;
        let result = max_population_coverage(graph, population, budget, radius);
        let expected = 80.0;
        assert!((result - expected).abs() < EPS, "Expected {}, got {}", expected, result);
    }
}
