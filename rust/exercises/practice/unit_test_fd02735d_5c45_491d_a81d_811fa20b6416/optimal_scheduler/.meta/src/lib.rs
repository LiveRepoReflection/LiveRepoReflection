use std::collections::HashMap;

pub fn schedule(n: usize, time: &Vec<u64>, deadline: &Vec<u64>, penalty: &Vec<u64>, dependencies: &Vec<Vec<usize>>) -> u64 {
    if n == 0 {
        return 0;
    }

    // Precompute prerequisites bitmask for each task.
    // Note: This solution uses a bitmask representation assuming n <= 64.
    let mut pre_mask = vec![0u64; n];
    for i in 0..n {
        let mut mask = 0u64;
        for &dep in &dependencies[i] {
            mask |= 1 << dep;
        }
        pre_mask[i] = mask;
    }
    
    let full_mask = if n < 64 { (1u64 << n) - 1 } else { u64::MAX };

    // Memoization cache: key (mask, current_time) -> minimum penalty achievable.
    let mut memo = HashMap::new();

    fn dp(mask: u64, current_time: u64, n: usize, full_mask: u64, time: &Vec<u64>, deadline: &Vec<u64>, penalty: &Vec<u64>, pre_mask: &Vec<u64>, memo: &mut HashMap<(u64, u64), u64>) -> u64 {
        if mask == full_mask {
            return 0;
        }
        if let Some(&result) = memo.get(&(mask, current_time)) {
            return result;
        }
        let mut best = u64::MAX;
        // Try scheduling each available task next.
        for i in 0..n {
            if (mask & (1 << i)) == 0 {
                // Check if task i's prerequisites are all completed.
                if (mask & pre_mask[i]) == pre_mask[i] {
                    let finish_time = current_time + time[i];
                    let incurred = if finish_time > deadline[i] { penalty[i] } else { 0 };
                    let next_mask = mask | (1 << i);
                    let total = incurred + dp(next_mask, finish_time, n, full_mask, time, deadline, penalty, pre_mask, memo);
                    if total < best {
                        best = total;
                    }
                }
            }
        }
        memo.insert((mask, current_time), best);
        best
    }
    
    dp(0, 0, n, full_mask, time, deadline, penalty, &pre_mask, &mut memo)
}