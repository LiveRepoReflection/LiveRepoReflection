use std::collections::{HashMap, HashSet};

pub struct AnalyticsSystem {
    graph: HashMap<u64, HashSet<u64>>,
}

impl AnalyticsSystem {
    pub fn new() -> Self {
        AnalyticsSystem {
            graph: HashMap::new(),
        }
    }

    pub fn add_user(&mut self, user_id: u64) {
        self.graph.entry(user_id).or_insert_with(HashSet::new);
    }

    pub fn add_connection(&mut self, user1: u64, user2: u64) {
        self.graph
            .entry(user1)
            .or_insert_with(HashSet::new)
            .insert(user2);
        self.graph
            .entry(user2)
            .or_insert_with(HashSet::new)
            .insert(user1);
    }

    pub fn remove_connection(&mut self, user1: u64, user2: u64) {
        if let Some(neighbors) = self.graph.get_mut(&user1) {
            neighbors.remove(&user2);
        }
        if let Some(neighbors) = self.graph.get_mut(&user2) {
            neighbors.remove(&user1);
        }
    }

    pub fn degree_centrality(&self, user: u64) -> usize {
        self.graph.get(&user).map_or(0, |neighbors| neighbors.len())
    }

    pub fn mutual_friends(&self, user1: u64, user2: u64) -> usize {
        if let (Some(neighbors1), Some(neighbors2)) =
            (self.graph.get(&user1), self.graph.get(&user2))
        {
            neighbors1.intersection(neighbors2).count()
        } else {
            0
        }
    }

    pub fn khop_neighbors(&self, user: u64, k: usize) -> usize {
        if k == 0 || !self.graph.contains_key(&user) {
            return 0;
        }
        let mut visited = HashSet::new();
        let mut current_level = HashSet::new();
        current_level.insert(user);
        visited.insert(user);
        for _ in 0..k {
            let mut next_level = HashSet::new();
            for &node in &current_level {
                if let Some(neighbors) = self.graph.get(&node) {
                    for &neighbor in neighbors {
                        if !visited.contains(&neighbor) {
                            next_level.insert(neighbor);
                            visited.insert(neighbor);
                        }
                    }
                }
            }
            if next_level.is_empty() {
                break;
            }
            current_level = next_level;
        }
        visited.remove(&user);
        visited.len()
    }
}