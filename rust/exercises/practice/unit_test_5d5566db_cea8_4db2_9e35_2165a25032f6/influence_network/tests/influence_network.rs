use std::collections::{HashMap, HashSet};
use influence_network::propagate_influence;

#[test]
fn test_empty_network() {
    let network: HashMap<usize, Vec<usize>> = HashMap::new();
    let seed: HashSet<usize> = [1].iter().copied().collect();
    let resistances: HashMap<usize, usize> = HashMap::new();
    let final_set = propagate_influence(&network, &seed, &resistances, 1.0, 10);
    let expected: HashSet<usize> = [1].iter().copied().collect();
    assert_eq!(final_set, expected);
}

#[test]
fn test_no_propagation() {
    let mut network = HashMap::new();
    network.insert(1, vec![2, 3]);
    network.insert(2, vec![1]);
    network.insert(3, vec![1]);
    let seed: HashSet<usize> = [1].iter().copied().collect();
    let mut resistances = HashMap::new();
    resistances.insert(1, 1);
    resistances.insert(2, 1);
    resistances.insert(3, 1);
    let final_set = propagate_influence(&network, &seed, &resistances, 0.0, 10);
    let expected: HashSet<usize> = [1].iter().copied().collect();
    assert_eq!(final_set, expected);
}

#[test]
fn test_full_propagation() {
    let mut network = HashMap::new();
    network.insert(1, vec![2]);
    network.insert(2, vec![3]);
    network.insert(3, vec![4]);
    network.insert(4, vec![]);
    let seed: HashSet<usize> = [1].iter().copied().collect();
    let mut resistances = HashMap::new();
    for id in 1..=4 {
        resistances.insert(id, 1);
    }
    let final_set = propagate_influence(&network, &seed, &resistances, 1.0, 10);
    let expected: HashSet<usize> = (1..=4).collect();
    assert_eq!(final_set, expected);
}

#[test]
fn test_rounds_limit() {
    let mut network = HashMap::new();
    network.insert(1, vec![2]);
    network.insert(2, vec![3]);
    network.insert(3, vec![4]);
    network.insert(4, vec![5]);
    network.insert(5, vec![]);
    let seed: HashSet<usize> = [1].iter().copied().collect();
    let mut resistances = HashMap::new();
    for id in 1..=5 {
        resistances.insert(id, 1);
    }
    // With a rounds limit of 2, propagation should only reach the second level (users 1, 2, and 3).
    let final_set = propagate_influence(&network, &seed, &resistances, 1.0, 2);
    let expected: HashSet<usize> = [1, 2, 3].iter().copied().collect();
    assert_eq!(final_set, expected);
}

#[test]
fn test_missing_resistance() {
    let mut network = HashMap::new();
    // 1 influences 2, 2 influences 3.
    network.insert(1, vec![2]);
    network.insert(2, vec![3]);
    network.insert(3, vec![]);
    let seed: HashSet<usize> = [1].iter().copied().collect();
    // Resistances: user 1 is defined, user 2 is missing (should default to 1), and user 3 is defined.
    let mut resistances = HashMap::new();
    resistances.insert(1, 1);
    resistances.insert(3, 1);
    let final_set = propagate_influence(&network, &seed, &resistances, 1.0, 10);
    let expected: HashSet<usize> = (1..=3).collect();
    assert_eq!(final_set, expected);
}

#[test]
fn test_cycle_in_network() {
    let mut network = HashMap::new();
    // Create a cycle: 1 -> 2, 2 -> 3, 3 -> 1, and an additional branch from 3 -> 4 -> 5.
    network.insert(1, vec![2]);
    network.insert(2, vec![3]);
    network.insert(3, vec![1, 4]);
    network.insert(4, vec![5]);
    network.insert(5, vec![]);
    let seed: HashSet<usize> = [1].iter().copied().collect();
    let mut resistances = HashMap::new();
    for id in 1..=5 {
        resistances.insert(id, 1);
    }
    let final_set = propagate_influence(&network, &seed, &resistances, 1.0, 10);
    // All nodes reachable from the seed should be activated despite the cycle.
    let expected: HashSet<usize> = (1..=5).collect();
    assert_eq!(final_set, expected);
}