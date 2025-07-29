use std::collections::{HashMap, HashSet};

pub fn propagate_influence(
    network: &HashMap<usize, Vec<usize>>,
    seed_users: &HashSet<usize>,
    resistances: &HashMap<usize, usize>,
    propagation_probability: f64,
    rounds_limit: usize,
) -> HashSet<usize> {
    let mut activated: HashSet<usize> = seed_users.clone();
    let mut frontier: Vec<usize> = seed_users.iter().copied().collect();
    let mut rng = SimpleRng::new(42);
    let mut rounds = 0;

    while !frontier.is_empty() && rounds < rounds_limit {
        let mut next_frontier = Vec::new();
        for &user in frontier.iter() {
            if let Some(neighbors) = network.get(&user) {
                for &neighbor in neighbors.iter() {
                    if activated.contains(&neighbor) {
                        continue;
                    }
                    let resistance = *resistances.get(&neighbor).unwrap_or(&1) as f64;
                    let effective_prob = propagation_probability / resistance;
                    let activated_now = if effective_prob >= 1.0 {
                        true
                    } else {
                        let rand_val = rng.next_f64();
                        rand_val < effective_prob
                    };
                    if activated_now {
                        activated.insert(neighbor);
                        next_frontier.push(neighbor);
                    }
                }
            }
        }
        frontier = next_frontier;
        rounds += 1;
    }
    activated
}

struct SimpleRng {
    seed: u32,
}

impl SimpleRng {
    pub fn new(seed: u32) -> Self {
        SimpleRng { seed }
    }

    fn next_u32(&mut self) -> u32 {
        // Linear congruential generator parameters from Numerical Recipes.
        self.seed = self.seed.wrapping_mul(1664525).wrapping_add(1013904223);
        self.seed
    }

    fn next_f64(&mut self) -> f64 {
        (self.next_u32() as f64) / (u32::MAX as f64)
    }
}