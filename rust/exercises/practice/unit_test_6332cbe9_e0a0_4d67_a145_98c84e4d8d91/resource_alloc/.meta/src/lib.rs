use std::collections::HashMap;

pub fn allocate(
    rm_capacities: &Vec<HashMap<String, u64>>,
    request: &HashMap<String, u64>,
) -> Result<HashMap<usize, HashMap<String, u64>>, String> {
    // If request is empty, return an empty allocation.
    if request.is_empty() {
        return Ok(HashMap::new());
    }

    // Check if aggregate resources are sufficient.
    for (res, &needed) in request.iter() {
        let total: u64 = rm_capacities
            .iter()
            .map(|rm| *rm.get(res).unwrap_or(&0))
            .sum();
        if total < needed {
            return Err("Insufficient resources".to_string());
        }
    }

    let n = rm_capacities.len();

    // Try to find combinations of RMs with increasing size.
    for k in 1..=n {
        let combs = combinations(n, k);
        for comb in combs {
            if combination_satisfies(&comb, rm_capacities, request) {
                let allocation = build_allocation(&comb, rm_capacities, request);
                return Ok(allocation);
            }
        }
    }
    Err("No allocation found".to_string())
}

fn combination_satisfies(
    indices: &Vec<usize>,
    rm_capacities: &Vec<HashMap<String, u64>>,
    request: &HashMap<String, u64>,
) -> bool {
    // For each requested resource, check if the sum of capacities in the selected RMs meets or exceeds the request.
    for (res, &needed) in request.iter() {
        let sum: u64 = indices
            .iter()
            .map(|&idx| *rm_capacities[idx].get(res).unwrap_or(&0))
            .sum();
        if sum < needed {
            return false;
        }
    }
    true
}

fn build_allocation(
    indices: &Vec<usize>,
    rm_capacities: &Vec<HashMap<String, u64>>,
    request: &HashMap<String, u64>,
) -> HashMap<usize, HashMap<String, u64>> {
    let mut allocation: HashMap<usize, HashMap<String, u64>> = HashMap::new();
    // Initialize allocation for each RM in the combination.
    for &rm_idx in indices.iter() {
        allocation.insert(rm_idx, HashMap::new());
    }
    // For each resource type, allocate from RMs in the order of the combination.
    for (res, &needed_total) in request.iter() {
        let mut remaining = needed_total;
        for &rm_idx in indices.iter() {
            let available = *rm_capacities[rm_idx].get(res).unwrap_or(&0);
            if available > 0 && remaining > 0 {
                let alloc_amount = if available >= remaining { remaining } else { available };
                allocation.entry(rm_idx)
                    .and_modify(|alloc_map| {
                        alloc_map.insert(res.clone(), alloc_amount);
                    });
                remaining -= alloc_amount;
            }
            if remaining == 0 {
                break;
            }
        }
    }
    allocation
}

fn combinations(n: usize, k: usize) -> Vec<Vec<usize>> {
    let mut result = Vec::new();
    let mut comb = Vec::new();
    generate_combinations(0, n, k, &mut comb, &mut result);
    result
}

fn generate_combinations(
    start: usize,
    n: usize,
    k: usize,
    comb: &mut Vec<usize>,
    result: &mut Vec<Vec<usize>>,
) {
    if comb.len() == k {
        result.push(comb.clone());
        return;
    }
    for i in start..n {
        comb.push(i);
        generate_combinations(i + 1, n, k, comb, result);
        comb.pop();
    }
}