use std::collections::{HashMap, HashSet};

#[derive(Clone, Debug)]
struct Edge {
    to: u32,
    travel_time: u32,
    capacity: u32,
}

#[derive(Clone)]
struct PathCandidate {
    route: Vec<u32>,
    travel_time: u32,
    bottleneck: u32,
}

#[derive(Debug, PartialEq)]
pub enum RoutingResult {
    Single(Vec<u32>),
    Split(Vec<(Vec<u32>, u32)>),
}

pub struct Network {
    graph: HashMap<u32, Vec<Edge>>,
    blocked: HashSet<(u32, u32)>,
}

impl Network {
    pub fn new() -> Self {
        Network {
            graph: HashMap::new(),
            blocked: HashSet::new(),
        }
    }

    pub fn add_route(&mut self, from: u32, to: u32, travel_time: u32, capacity: u32) -> String {
        let edge = Edge { to, travel_time, capacity };
        self.graph.entry(from).or_insert_with(Vec::new).push(edge);
        "Trade route added".to_string()
    }

    pub fn remove_route(&mut self, from: u32, to: u32, travel_time: u32, capacity: u32) -> String {
        if let Some(edges) = self.graph.get_mut(&from) {
            let original_len = edges.len();
            edges.retain(|e| !(e.to == to && e.travel_time == travel_time && e.capacity == capacity));
            if edges.len() < original_len {
                return "Trade route removed".to_string();
            }
        }
        "Trade route removal failed".to_string()
    }

    pub fn block_route(&mut self, from: u32, to: u32) -> String {
        self.blocked.insert((from, to));
        "Trade route blocked".to_string()
    }

    pub fn unblock_route(&mut self, from: u32, to: u32) -> String {
        self.blocked.remove(&(from, to));
        "Trade route unblocked".to_string()
    }

    pub fn find_route(&self, origin: u32, destination: u32, cargo: u32, extra_blocked: &Vec<(u32, u32)>) -> Result<RoutingResult, String> {
        // Combine internal and extra blocked routes.
        let mut blocked_union = self.blocked.clone();
        for &(f, t) in extra_blocked.iter() {
            blocked_union.insert((f, t));
        }
        let candidates = self.find_all_paths(origin, destination, &blocked_union);
        if candidates.is_empty() {
            return Err("No route available".to_string());
        }
        // First try to find a single route that satisfies cargo.
        let mut single_candidates: Vec<PathCandidate> = candidates
            .iter()
            .cloned()
            .filter(|p| p.bottleneck >= cargo)
            .collect();
        if !single_candidates.is_empty() {
            single_candidates.sort_by_key(|p| p.travel_time);
            return Ok(RoutingResult::Single(single_candidates[0].route.clone()));
        }
        // Otherwise, try to find combinations of candidate routes.
        // First, check overall capacity available.
        let total_capacity: u32 = candidates.iter().map(|p| p.bottleneck).sum();
        if total_capacity < cargo {
            return Err("Cargo exceeds network capacity".to_string());
        }
        // Try combinations with increasing number of splits.
        // We use a helper to generate combinations.
        for k in 2..=candidates.len() {
            let combos = combinations(&candidates, k);
            // Filter valid combinations: sum of bottlenecks >= cargo.
            let mut valid: Vec<(Vec<PathCandidate>, u32)> = Vec::new();
            for combo in combos {
                let sum_cap: u32 = combo.iter().map(|p| p.bottleneck).sum();
                if sum_cap >= cargo {
                    let max_time = combo.iter().map(|p| p.travel_time).max().unwrap_or(0);
                    valid.push((combo, max_time));
                }
            }
            if !valid.is_empty() {
                // Choose the combination with minimal maximum travel time.
                valid.sort_by_key(|&(_, max_time)| max_time);
                let chosen = &valid[0].0;
                // Assign cargo splitting. We try to minimize the number of splits.
                let mut remaining = cargo;
                let mut splits: Vec<(Vec<u32>, u32)> = Vec::new();
                for candidate in chosen.iter() {
                    let assign = if candidate.bottleneck >= remaining { remaining } else { candidate.bottleneck };
                    splits.push((candidate.route.clone(), assign));
                    remaining = remaining.saturating_sub(assign);
                    if remaining == 0 {
                        break;
                    }
                }
                return Ok(RoutingResult::Split(splits));
            }
        }
        Err("Cargo exceeds network capacity".to_string())
    }

    fn find_all_paths(&self, origin: u32, destination: u32, blocked: &HashSet<(u32,u32)>) -> Vec<PathCandidate> {
        let mut results = Vec::new();
        let mut visited = HashSet::new();
        let mut current_route = Vec::new();
        self.dfs(origin, destination, blocked, 0, u32::MAX, &mut visited, &mut current_route, &mut results);
        results
    }

    fn dfs(&self, current: u32, destination: u32, blocked: &HashSet<(u32,u32)>, current_time: u32, current_bottleneck: u32, visited: &mut HashSet<u32>, current_route: &mut Vec<u32>, results: &mut Vec<PathCandidate>) {
        visited.insert(current);
        current_route.push(current);
        if current == destination {
            results.push(PathCandidate {
                route: current_route.clone(),
                travel_time: current_time,
                bottleneck: current_bottleneck,
            });
        } else {
            if let Some(neighbors) = self.graph.get(&current) {
                for edge in neighbors.iter() {
                    if visited.contains(&edge.to) {
                        continue;
                    }
                    if blocked.contains(&(current, edge.to)) {
                        continue;
                    }
                    let next_time = current_time.saturating_add(edge.travel_time);
                    let next_bottleneck = current_bottleneck.min(edge.capacity);
                    self.dfs(edge.to, destination, blocked, next_time, next_bottleneck, visited, current_route, results);
                }
            }
        }
        current_route.pop();
        visited.remove(&current);
    }
}

// Helper function to generate all combinations of k elements from a slice.
fn combinations<T: Clone>(elements: &Vec<T>, k: usize) -> Vec<Vec<T>> {
    let n = elements.len();
    let mut result = Vec::new();
    let mut combo = Vec::new();
    combine_helper(elements, k, 0, &mut combo, &mut result);
    result
}

fn combine_helper<T: Clone>(elements: &Vec<T>, k: usize, start: usize, combo: &mut Vec<T>, result: &mut Vec<Vec<T>>) {
    if combo.len() == k {
        result.push(combo.clone());
        return;
    }
    for i in start..elements.len() {
        combo.push(elements[i].clone());
        combine_helper(elements, k, i + 1, combo, result);
        combo.pop();
    }
}