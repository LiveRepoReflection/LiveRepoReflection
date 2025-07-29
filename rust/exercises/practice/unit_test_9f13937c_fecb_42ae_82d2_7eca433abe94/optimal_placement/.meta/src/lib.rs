use std::collections::HashMap;

const INF: u32 = 10_000; // A large number representing infinity for our latencies.

#[derive(Clone, Debug)]
struct DataCenter {
    id: u32,
    capacity: f64,
    cost: f64,
}

// Public API: allocate function as described.
pub fn allocate(
    data_size: u64,
    replication_factor: u32,
    max_latency: u32,
    data_centers: Vec<(u32, u64, u64)>,
    network_links: Vec<(u32, u32, u32)>,
) -> Option<HashMap<u32, f64>> {
    // Convert data centers to struct and build id->index mapping.
    let n = data_centers.len();
    let mut centers: Vec<DataCenter> = Vec::with_capacity(n);
    let mut id_to_index: HashMap<u32, usize> = HashMap::new();
    for (i, (id, cap, cost)) in data_centers.into_iter().enumerate() {
        centers.push(DataCenter {
            id,
            capacity: cap as f64,
            cost: cost as f64,
        });
        id_to_index.insert(id, i);
    }
    
    // Build distance matrix using Floyd Warshall.
    let mut dist = vec![vec![INF; n]; n];
    for i in 0..n {
        dist[i][i] = 0;
    }
    // For each network link, update the matrix (bidirectional).
    for (a, b, latency) in network_links {
        if let (Some(&i), Some(&j)) = (id_to_index.get(&a), id_to_index.get(&b)) {
            // Use the minimum if there are multiple links.
            dist[i][j] = dist[i][j].min(latency);
            dist[j][i] = dist[j][i].min(latency);
        }
    }
    
    // Floyd Warshall to compute all pairs shortest paths.
    for k in 0..n {
        for i in 0..n {
            for j in 0..n {
                let alt = dist[i][k].saturating_add(dist[k][j]);
                if alt < dist[i][j] {
                    dist[i][j] = alt;
                }
            }
        }
    }
    
    // Generate candidate clusters: each cluster is a vector of indices of data centers,
    // and cluster size must equal replication_factor and all pairs have distance <= max_latency.
    let mut candidates: Vec<(Vec<usize>, f64)> = Vec::new();
    let r = replication_factor as usize;
    let mut combination: Vec<usize> = Vec::new();
    generate_combinations(n, r, 0, &mut combination, &mut candidates, &centers, &dist, max_latency);
    
    if candidates.is_empty() {
        return None;
    }
    
    // Sort candidates by effective cost (sum of cost of centers in the cluster).
    candidates.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap());
    
    // Greedy allocation using candidate clusters.
    // Total required storage across clusters is replication_factor * data_size.
    let required = (replication_factor as f64) * (data_size as f64);
    let mut remaining = data_size as f64;
    // Allocation per data center (by index).
    let mut allocation = vec![0f64; n];
    
    // For each candidate cluster, try to use it until either remaining data is 0
    // or capacity of one of its members is reached.
    for (cluster, _eff_cost) in candidates.iter() {
        // Determine the maximum additional allocation the cluster can take.
        let mut available = std::f64::INFINITY;
        for &i in cluster.iter() {
            available = available.min(centers[i].capacity - allocation[i]);
        }
        if available <= 0.0 {
            continue;
        }
        // Amount to allocate using this cluster
        let alloc = remaining.min(available);
        for &i in cluster.iter() {
            allocation[i] += alloc;
        }
        remaining -= alloc;
        if remaining.abs() < 1e-6 {
            break;
        }
    }
    
    // Check if we managed to allocate all required data (each data chunk replicated replication_factor times,
    // so total allocation across all centers should be replication_factor * data_size).
    let total_alloc: f64 = allocation.iter().sum();
    if (total_alloc - required).abs() > 1e-6 {
        return None;
    }
    
    // Build the resulting HashMap mapping data center id to allocated amount.
    let mut result = HashMap::new();
    for (i, alloc) in allocation.into_iter().enumerate() {
        // We can skip centers with zero allocation.
        if alloc > 1e-6 {
            result.insert(centers[i].id, alloc);
        }
    }
    
    Some(result)
}

// Helper function to generate combinations of indices and check latency constraint.
fn generate_combinations(
    n: usize,
    r: usize,
    start: usize,
    combination: &mut Vec<usize>,
    candidates: &mut Vec<(Vec<usize>, f64)>,
    centers: &[DataCenter],
    dist: &[Vec<u32>],
    max_latency: u32,
) {
    if combination.len() == r {
        // Check that for every pair in the combination, the latency constraint is met.
        let mut valid = true;
        for i in 0..r {
            for j in (i+1)..r {
                let a = combination[i];
                let b = combination[j];
                if dist[a][b] > max_latency {
                    valid = false;
                    break;
                }
            }
            if !valid {
                break;
            }
        }
        if valid {
            // Compute effective cost, i.e., sum of cost of centers in the cluster.
            let eff_cost: f64 = combination.iter().map(|&i| centers[i].cost).sum();
            candidates.push((combination.clone(), eff_cost));
        }
        return;
    }
    for i in start..n {
        combination.push(i);
        generate_combinations(n, r, i + 1, combination, candidates, centers, dist, max_latency);
        combination.pop();
    }
}