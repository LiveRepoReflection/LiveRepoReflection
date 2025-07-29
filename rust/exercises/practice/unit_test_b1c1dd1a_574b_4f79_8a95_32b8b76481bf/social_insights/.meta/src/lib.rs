use std::collections::HashSet;

pub trait Network {
    fn get_friends(&self, user_id: u64) -> Option<Vec<u64>>;
    fn get_age(&self, user_id: u64) -> Option<u8>;
}

pub fn average_friend_age(network: &impl Network, user_id: u64) -> Option<f64> {
    let friends = network.get_friends(user_id)?;
    if friends.is_empty() {
        return None;
    }
    let mut total = 0u64;
    let mut count = 0;
    for friend in friends {
        if let Some(age) = network.get_age(friend) {
            total += age as u64;
            count += 1;
        }
    }
    if count == 0 {
        None
    } else {
        Some(total as f64 / count as f64)
    }
}

pub fn mutual_friends_count(network: &impl Network, user_id1: u64, user_id2: u64) -> u64 {
    let friends1 = network.get_friends(user_id1).unwrap_or_else(|| vec![]);
    let friends2 = network.get_friends(user_id2).unwrap_or_else(|| vec![]);
    let set1: HashSet<u64> = friends1.into_iter().collect();
    let set2: HashSet<u64> = friends2.into_iter().collect();
    set1.intersection(&set2).count() as u64
}

pub fn k_hop_friend_suggestion(network: &impl Network, user_id: u64, k: u32) -> Option<u64> {
    if k == 0 {
        return Some(user_id);
    }
    let mut current_level: HashSet<u64> = HashSet::new();
    let mut visited: HashSet<u64> = HashSet::new();
    current_level.insert(user_id);
    visited.insert(user_id);
    for _ in 1..=k {
        let mut next_level: HashSet<u64> = HashSet::new();
        for uid in current_level.iter() {
            if let Some(friends) = network.get_friends(*uid) {
                for friend in friends {
                    if !visited.contains(&friend) {
                        next_level.insert(friend);
                    }
                }
            }
        }
        if next_level.is_empty() {
            return None;
        }
        for node in &next_level {
            visited.insert(*node);
        }
        current_level = next_level;
    }
    current_level.into_iter().min()
}

pub fn approximate_influencers(network: &impl Network, p: f64, sample_size: usize) -> HashSet<u64> {
    let threshold = (p * sample_size as f64).ceil() as usize;
    let mut influencers = HashSet::new();
    for user_id in 1..=(sample_size as u64) {
        let friends = network.get_friends(user_id).unwrap_or_else(Vec::new);
        if friends.len() >= threshold {
            influencers.insert(user_id);
        }
    }
    influencers
}