use std::collections::{HashMap, HashSet};

pub fn partition(n: usize, edges: Vec<(usize, usize, i32)>, risk_scores: Vec<i32>, k: usize, max_size: usize) -> Vec<usize> {
    // Input validation
    if k == 0 || max_size == 0 || n == 0 {
        panic!("Invalid input parameters");
    }
    if risk_scores.len() != n {
        panic!("Risk scores length doesn't match number of nodes");
    }

    // Build adjacency list representation of the graph
    let mut adj_list: Vec<Vec<(usize, i32)>> = vec![Vec::new(); n];
    for (u, v, weight) in edges {
        adj_list[u].push((v, weight));
        adj_list[v].push((u, weight));
    }

    // Initialize solution using a modified spectral clustering approach
    let mut best_partitioning = initialize_partitioning(n, k, &adj_list, &risk_scores);
    let mut best_score = evaluate_partitioning(&best_partitioning, &adj_list, &risk_scores, k, max_size);

    // Simulated annealing parameters
    let initial_temperature = 100.0;
    let cooling_rate = 0.995;
    let iterations_per_temperature = 100;
    let mut temperature = initial_temperature;

    // Simulated annealing main loop
    while temperature > 0.1 {
        for _ in 0..iterations_per_temperature {
            let mut new_partitioning = best_partitioning.clone();
            
            // Generate neighbor solution by moving a random node to a different partition
            let node = rand_range(0, n);
            let old_partition = new_partitioning[node];
            let new_partition = rand_range(0, k);
            
            if old_partition != new_partition {
                new_partitioning[node] = new_partition;
                
                // Check if the move is valid (respects max_size constraint)
                if is_valid_partitioning(&new_partitioning, k, max_size) {
                    let new_score = evaluate_partitioning(&new_partitioning, &adj_list, &risk_scores, k, max_size);
                    
                    // Accept or reject the new solution based on simulated annealing criteria
                    let delta = new_score as f64 - best_score as f64;
                    if delta < 0.0 || rand_float() < ((-delta) / temperature).exp() {
                        best_partitioning = new_partitioning;
                        best_score = new_score;
                    }
                }
            }
        }
        temperature *= cooling_rate;
    }

    // Local search to improve the solution
    best_partitioning = local_search(best_partitioning, &adj_list, &risk_scores, k, max_size);

    best_partitioning
}

fn initialize_partitioning(n: usize, k: usize, adj_list: &Vec<Vec<(usize, i32)>>, risk_scores: &Vec<i32>) -> Vec<usize> {
    let mut partitioning = vec![0; n];
    let mut sizes = vec![0; k];
    
    // Sort nodes by risk score (highest first)
    let mut nodes: Vec<usize> = (0..n).collect();
    nodes.sort_by_key(|&i| std::cmp::Reverse(risk_scores[i]));
    
    // Distribute nodes across partitions
    for &node in nodes.iter() {
        let mut best_partition = 0;
        let mut min_connected_risk = i32::MAX;
        
        for partition in 0..k {
            if sizes[partition] < n / k + 1 {
                let connected_risk = calculate_connected_risk(node, partition, &partitioning, adj_list, risk_scores);
                if connected_risk < min_connected_risk {
                    min_connected_risk = connected_risk;
                    best_partition = partition;
                }
            }
        }
        
        partitioning[node] = best_partition;
        sizes[best_partition] += 1;
    }
    
    partitioning
}

fn calculate_connected_risk(node: usize, partition: usize, partitioning: &Vec<usize>, 
                          adj_list: &Vec<Vec<(usize, i32)>>, risk_scores: &Vec<i32>) -> i32 {
    let mut risk = 0;
    for &(neighbor, weight) in &adj_list[node] {
        if partitioning[neighbor] == partition {
            risk += weight * risk_scores[neighbor];
        }
    }
    risk
}

fn evaluate_partitioning(partitioning: &Vec<usize>, adj_list: &Vec<Vec<(usize, i32)>>, 
                        risk_scores: &Vec<i32>, k: usize, max_size: usize) -> i32 {
    let mut total_cost = 0;
    let mut partition_risks = vec![0; k];
    let mut cut_edges = 0;
    
    // Calculate partition risks and cut edges
    for node in 0..partitioning.len() {
        let current_partition = partitioning[node];
        partition_risks[current_partition] += risk_scores[node];
        
        for &(neighbor, weight) in &adj_list[node] {
            if partitioning[neighbor] != current_partition {
                cut_edges += weight;
            }
        }
    }
    
    // Calculate total cost
    total_cost = *partition_risks.iter().max().unwrap() + cut_edges / 2;
    
    total_cost
}

fn is_valid_partitioning(partitioning: &Vec<usize>, k: usize, max_size: usize) -> bool {
    let mut sizes = vec![0; k];
    for &partition in partitioning {
        sizes[partition] += 1;
        if sizes[partition] > max_size {
            return false;
        }
    }
    true
}

fn local_search(mut partitioning: Vec<usize>, adj_list: &Vec<Vec<(usize, i32)>>, 
                risk_scores: &Vec<i32>, k: usize, max_size: usize) -> Vec<usize> {
    let n = partitioning.len();
    let mut improved = true;
    
    while improved {
        improved = false;
        for node in 0..n {
            let old_partition = partitioning[node];
            let current_score = evaluate_partitioning(&partitioning, adj_list, risk_scores, k, max_size);
            
            for new_partition in 0..k {
                if new_partition != old_partition {
                    partitioning[node] = new_partition;
                    if is_valid_partitioning(&partitioning, k, max_size) {
                        let new_score = evaluate_partitioning(&partitioning, adj_list, risk_scores, k, max_size);
                        if new_score < current_score {
                            improved = true;
                            break;
                        }
                    }
                    partitioning[node] = old_partition;
                }
            }
        }
    }
    
    partitioning
}

// Helper functions for random number generation
fn rand_range(min: usize, max: usize) -> usize {
    min + (rand_float() * (max - min) as f64) as usize
}

fn rand_float() -> f64 {
    use std::time::{SystemTime, UNIX_EPOCH};
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .subsec_nanos() as f64;
    (nanos / 1_000_000_000.0).fract()
}