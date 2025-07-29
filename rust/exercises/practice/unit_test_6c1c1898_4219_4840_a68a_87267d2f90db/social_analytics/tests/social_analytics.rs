use std::collections::{HashMap, HashSet};

/// A simple in-memory simulation of a distributed social network analytics system.
/// For testing purposes, we assume all data is managed in a single instance.
pub struct AnalyticsSystem {
    /// Each user is mapped to a set of connected user IDs.
    graph: HashMap<u64, HashSet<u64>>,
}

impl AnalyticsSystem {
    /// Creates a new analytics system.
    pub fn new() -> Self {
        AnalyticsSystem {
            graph: HashMap::new(),
        }
    }

    /// Adds a new user to the system.
    pub fn add_user(&mut self, user_id: u64) {
        self.graph.entry(user_id).or_insert_with(HashSet::new);
    }

    /// Adds a bidirectional connection between two users.
    pub fn add_connection(&mut self, user1: u64, user2: u64) {
        self.graph.entry(user1).or_insert_with(HashSet::new).insert(user2);
        self.graph.entry(user2).or_insert_with(HashSet::new).insert(user1);
    }

    /// Removes a bidirectional connection between two users.
    pub fn remove_connection(&mut self, user1: u64, user2: u64) {
        if let Some(neighbors) = self.graph.get_mut(&user1) {
            neighbors.remove(&user2);
        }
        if let Some(neighbors) = self.graph.get_mut(&user2) {
            neighbors.remove(&user1);
        }
    }

    /// Returns the degree centrality (number of direct neighbors) of a user.
    /// If the user does not exist, returns 0.
    pub fn degree_centrality(&self, user: u64) -> usize {
        self.graph.get(&user).map_or(0, |neighbors| neighbors.len())
    }

    /// Returns the number of mutual friends/shared neighbors between two users.
    pub fn mutual_friends(&self, user1: u64, user2: u64) -> usize {
        if let (Some(neighbors1), Some(neighbors2)) = (self.graph.get(&user1), self.graph.get(&user2)) {
            neighbors1.intersection(neighbors2).count()
        } else {
            0
        }
    }

    /// Returns the number of unique users reachable from the given user within k hops.
    /// The starting user is not counted.
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
            current_level = next_level;
            if current_level.is_empty() {
                break;
            }
        }
        // Remove the starting user if present.
        visited.remove(&user);
        visited.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_degree_centrality_no_user() {
        let system = AnalyticsSystem::new();
        // Non-existent user should yield zero connections.
        assert_eq!(system.degree_centrality(42), 0);
    }

    #[test]
    fn test_degree_centrality_single_user() {
        let mut system = AnalyticsSystem::new();
        system.add_user(1);
        assert_eq!(system.degree_centrality(1), 0);
    }

    #[test]
    fn test_degree_centrality_multiple_connections() {
        let mut system = AnalyticsSystem::new();
        // Create users
        for id in 1..=4 {
            system.add_user(id);
        }
        // Connect user 1 with 2, 3, and 4
        system.add_connection(1, 2);
        system.add_connection(1, 3);
        system.add_connection(1, 4);
        assert_eq!(system.degree_centrality(1), 3);
    }

    #[test]
    fn test_mutual_friends_no_overlap() {
        let mut system = AnalyticsSystem::new();
        // Create users
        for id in 1..=4 {
            system.add_user(id);
        }
        system.add_connection(1, 2);
        system.add_connection(3, 4);
        // Users 1 and 3 do not share any friend
        assert_eq!(system.mutual_friends(1, 3), 0);
    }

    #[test]
    fn test_mutual_friends_with_overlap() {
        let mut system = AnalyticsSystem::new();
        // Create users 1, 2, 3, 4
        for id in 1..=4 {
            system.add_user(id);
        }
        // Setup connections:
        // 1 connected to 2 and 3
        // 4 connected to 2 and 3
        system.add_connection(1, 2);
        system.add_connection(1, 3);
        system.add_connection(4, 2);
        system.add_connection(4, 3);
        // Mutual friends between 1 and 4 are {2, 3}
        assert_eq!(system.mutual_friends(1, 4), 2);
    }

    #[test]
    fn test_khop_neighbors_basic() {
        let mut system = AnalyticsSystem::new();
        // Build a linear chain: 1 - 2 - 3 - 4 - 5
        for id in 1..=5 {
            system.add_user(id);
        }
        system.add_connection(1, 2);
        system.add_connection(2, 3);
        system.add_connection(3, 4);
        system.add_connection(4, 5);
        // k=1: Only direct neighbor of 1 is 2.
        assert_eq!(system.khop_neighbors(1, 1), 1);
        // k=2: Reachable nodes from 1 are 2 and 3.
        assert_eq!(system.khop_neighbors(1, 2), 2);
        // k=3: Reachable nodes from 1 are 2,3,4.
        assert_eq!(system.khop_neighbors(1, 3), 3);
        // k=4: Reachable nodes from 1 are all except itself
        assert_eq!(system.khop_neighbors(1, 4), 4);
        // k=5: No additional nodes beyond what is reached in 4 hops.
        assert_eq!(system.khop_neighbors(1, 5), 4);
    }

    #[test]
    fn test_khop_neighbors_disconnected_graph() {
        let mut system = AnalyticsSystem::new();
        // Create two disconnected subgraphs.
        // Subgraph 1: 1 - 2 - 3
        for id in 1..=3 {
            system.add_user(id);
        }
        system.add_connection(1, 2);
        system.add_connection(2, 3);
        // Subgraph 2: 4 - 5
        for id in 4..=5 {
            system.add_user(id);
        }
        system.add_connection(4, 5);
        // k-hop for node 1 should only include subgraph 1.
        assert_eq!(system.khop_neighbors(1, 1), 1);
        assert_eq!(system.khop_neighbors(1, 2), 2);
        // For node 4, only node 5 is reachable.
        assert_eq!(system.khop_neighbors(4, 1), 1);
        // For non-existent user, result is 0.
        assert_eq!(system.khop_neighbors(100, 2), 0);
    }

    #[test]
    fn test_dynamic_connection_changes() {
        let mut system = AnalyticsSystem::new();
        // Create a triangle: 1, 2, 3
        for id in 1..=3 {
            system.add_user(id);
        }
        system.add_connection(1, 2);
        system.add_connection(2, 3);
        system.add_connection(1, 3);
        // Verify degree centrality before removal.
        assert_eq!(system.degree_centrality(1), 2);
        // Remove one connection
        system.remove_connection(1, 3);
        assert_eq!(system.degree_centrality(1), 1);
        // Verify mutual friends between 1 and 3 should now be only 2 if connection still exists.
        assert_eq!(system.mutual_friends(1, 3), 1);
    }

    #[test]
    fn test_complex_graph_khop() {
        let mut system = AnalyticsSystem::new();
        // Build a more complex graph resembling a small social network.
        // Users 1 to 7
        for id in 1..=7 {
            system.add_user(id);
        }
        // Connections:
        // 1: 2, 3
        // 2: 1, 4, 5
        // 3: 1, 6
        // 4: 2, 7
        // 5: 2
        // 6: 3, 7
        // 7: 4, 6
        system.add_connection(1, 2);
        system.add_connection(1, 3);
        system.add_connection(2, 4);
        system.add_connection(2, 5);
        system.add_connection(3, 6);
        system.add_connection(4, 7);
        system.add_connection(6, 7);

        // k = 1 for user 1: should get {2,3}
        assert_eq!(system.khop_neighbors(1, 1), 2);
        // k = 2 for user 1: reachable are {2,3,4,5,6}
        assert_eq!(system.khop_neighbors(1, 2), 5);
        // k = 3 for user 1: reachable are all except itself (7 is reached at level3)
        assert_eq!(system.khop_neighbors(1, 3), 6);
    }
}