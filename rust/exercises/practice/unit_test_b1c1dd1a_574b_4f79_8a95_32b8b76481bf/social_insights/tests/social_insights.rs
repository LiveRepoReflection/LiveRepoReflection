use std::collections::{HashMap, HashSet};
use social_insights::{average_friend_age, mutual_friends_count, k_hop_friend_suggestion, approximate_influencers, Network};

struct TestNetwork {
    friends: HashMap<u64, Vec<u64>>,
    ages: HashMap<u64, u8>,
}

impl TestNetwork {
    fn new() -> Self {
        TestNetwork {
            friends: HashMap::new(),
            ages: HashMap::new(),
        }
    }

    fn add_user(&mut self, user_id: u64, age: u8) {
        self.ages.insert(user_id, age);
    }

    fn add_connection(&mut self, user_id: u64, friend_id: u64) {
        self.friends.entry(user_id).or_insert(Vec::new()).push(friend_id);
    }
}

impl Network for TestNetwork {
    fn get_friends(&self, user_id: u64) -> Option<Vec<u64>> {
        self.friends.get(&user_id).cloned()
    }

    fn get_age(&self, user_id: u64) -> Option<u8> {
        self.ages.get(&user_id).cloned()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_average_friend_age_normal() {
        let mut net = TestNetwork::new();
        net.add_user(1, 30);
        net.add_user(2, 25);
        net.add_user(3, 35);
        // Setup: User 1 is friends with 2 and 3
        net.add_connection(1, 2);
        net.add_connection(1, 3);
        let avg = average_friend_age(&net, 1);
        assert!(avg.is_some());
        let avg_val = avg.unwrap();
        // Expected average: (25 + 35) / 2.0 = 30.0
        assert!((avg_val - 30.0).abs() < 1e-6);
    }

    #[test]
    fn test_average_friend_age_no_friends() {
        let mut net = TestNetwork::new();
        net.add_user(1, 30);
        // User 1 has no friends
        assert_eq!(None, average_friend_age(&net, 1));
    }

    #[test]
    fn test_average_friend_age_non_existing_user() {
        let net = TestNetwork::new();
        // User 1 does not exist in the network
        assert_eq!(None, average_friend_age(&net, 1));
    }

    #[test]
    fn test_mutual_friends_count_normal() {
        let mut net = TestNetwork::new();
        // Create users with IDs 1, 2, 3, 4
        net.add_user(1, 30);
        net.add_user(2, 25);
        net.add_user(3, 35);
        net.add_user(4, 40);
        // Setup: 
        // User 1: friends: 2, 3
        net.add_connection(1, 2);
        net.add_connection(1, 3);
        // User 2: friends: 3, 4
        net.add_connection(2, 3);
        net.add_connection(2, 4);
        // Mutual friend for users 1 and 2 is 3
        assert_eq!(1, mutual_friends_count(&net, 1, 2));
    }

    #[test]
    fn test_mutual_friends_count_no_mutual() {
        let mut net = TestNetwork::new();
        net.add_user(1, 30);
        net.add_user(2, 25);
        net.add_user(3, 35);
        net.add_user(4, 40);
        // Setup:
        // User 1: friend: 3
        net.add_connection(1, 3);
        // User 2: friend: 4
        net.add_connection(2, 4);
        // No mutual friends between users 1 and 2
        assert_eq!(0, mutual_friends_count(&net, 1, 2));
    }

    #[test]
    fn test_mutual_friends_count_non_existing() {
        let mut net = TestNetwork::new();
        net.add_user(1, 30);
        // User 2 does not exist
        assert_eq!(0, mutual_friends_count(&net, 1, 2));
    }

    #[test]
    fn test_k_hop_friend_suggestion_k1() {
        let mut net = TestNetwork::new();
        // Create network:
        // User 1: friends: 2, 5
        // User 2: friend: 3
        // User 3: friend: 4
        // Users 4 and 5: no friends
        net.add_user(1, 30);
        net.add_user(2, 25);
        net.add_user(3, 35);
        net.add_user(4, 40);
        net.add_user(5, 20);
        net.add_connection(1, 2);
        net.add_connection(1, 5);
        net.add_connection(2, 3);
        net.add_connection(3, 4);
        // For k = 1, suggestion should be the smallest direct friend (which is 2)
        let suggestion = k_hop_friend_suggestion(&net, 1, 1);
        assert_eq!(Some(2), suggestion);
    }

    #[test]
    fn test_k_hop_friend_suggestion_k2() {
        let mut net = TestNetwork::new();
        // Create network:
        // User 1: friend: 2
        // User 2: friends: 3, 6
        // User 3: friend: 4
        // User 6: friend: 5
        // Users 4 and 5: no friends
        net.add_user(1, 30);
        net.add_user(2, 25);
        net.add_user(3, 35);
        net.add_user(4, 40);
        net.add_user(5, 20);
        net.add_user(6, 28);
        net.add_connection(1, 2);
        net.add_connection(2, 3);
        net.add_connection(2, 6);
        net.add_connection(3, 4);
        net.add_connection(6, 5);
        // For user 1 with k = 2, reachable nodes at level 2 are {3, 6}.
        // Suggestion should be the smallest id: 3.
        let suggestion = k_hop_friend_suggestion(&net, 1, 2);
        assert_eq!(Some(3), suggestion);
    }

    #[test]
    fn test_k_hop_friend_suggestion_cycle() {
        let mut net = TestNetwork::new();
        // Create a cycle in the network:
        // 1 -> 2, 2 -> 3, 3 -> 1
        net.add_user(1, 30);
        net.add_user(2, 25);
        net.add_user(3, 35);
        net.add_connection(1, 2);
        net.add_connection(2, 3);
        net.add_connection(3, 1);
        // For user 1 with k = 2, reachable node should be 3.
        let suggestion = k_hop_friend_suggestion(&net, 1, 2);
        assert_eq!(Some(3), suggestion);
    }

    #[test]
    fn test_k_hop_friend_suggestion_none() {
        let mut net = TestNetwork::new();
        // User 1 exists but has no friends.
        net.add_user(1, 30);
        let suggestion = k_hop_friend_suggestion(&net, 1, 1);
        assert_eq!(None, suggestion);
    }

    #[test]
    fn test_approximate_influencers() {
        let mut net = TestNetwork::new();
        // Create a network of 5 users.
        for i in 1..=5 {
            net.add_user(i, 20 + i as u8);
        }
        // Setup connections:
        // User 1: [2, 3]
        net.add_connection(1, 2);
        net.add_connection(1, 3);
        // User 2: [1, 3, 4]
        net.add_connection(2, 1);
        net.add_connection(2, 3);
        net.add_connection(2, 4);
        // User 3: [1, 2, 4, 5]
        net.add_connection(3, 1);
        net.add_connection(3, 2);
        net.add_connection(3, 4);
        net.add_connection(3, 5);
        // User 4: [2, 3]
        net.add_connection(4, 2);
        net.add_connection(4, 3);
        // User 5: [3]
        net.add_connection(5, 3);

        // In this network of 5 users:
        // Friend counts: user1: 2, user2: 3, user3: 4, user4: 2, user5: 1.
        // With threshold p = 0.5, user must have at least 3 friends to be an influencer.
        // Expected influencers: {2, 3}
        let influencers = approximate_influencers(&net, 0.5, 5);
        let expected: HashSet<u64> = [2, 3].iter().cloned().collect();
        assert_eq!(expected, influencers);
    }
}