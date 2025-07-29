pub fn max_weighted_throughput(
    n: usize,
    processing_capacities: Vec<usize>,
    data_flows: Vec<(usize, usize, usize, usize)>
) -> usize {
    // Group flows by source server.
    // Each flow is represented as (volume, weighted_value) where weighted_value = volume * priority.
    let mut groups: Vec<Vec<(usize, usize)>> = vec![Vec::new(); n];
    for flow in data_flows {
        let (src, _dst, volume, priority) = flow;
        if src < n {
            groups[src].push((volume, volume * priority));
        }
    }
    let mut total: usize = 0;
    // For each server, solve the 0/1 knapsack problem with capacity equal to its processing capacity.
    for i in 0..n {
        let cap = processing_capacities[i];
        let items = &groups[i];
        // dp[w] will hold the max weighted throughput achievable in server i with capacity w.
        let mut dp = vec![0; cap + 1];
        for &(vol, value) in items {
            // Only consider this flow if its volume is <= capacity.
            if vol <= cap {
                for w in (vol..=cap).rev() {
                    let candidate = dp[w - vol] + value;
                    if candidate > dp[w] {
                        dp[w] = candidate;
                    }
                }
            }
        }
        total += dp[cap];
    }
    total
}