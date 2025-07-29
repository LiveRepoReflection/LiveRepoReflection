use std::collections::{HashMap, HashSet};
use byzantine_agreement::simulate;

#[test]
fn test_commander_loyal_no_traitors() {
    // n = 7, no traitors, commander (index 0) loyal, commander_value = true.
    let n = 7;
    let t = 0;
    let commander_value = true;
    let traitors: HashSet<usize> = HashSet::new();
    let result = simulate(n, t, commander_value, &traitors).unwrap();
    
    // Loyal lieutenants are indices 1..6 (commander excluded).
    let mut expected = HashMap::new();
    for i in 1..n {
        expected.insert(i, true);
    }
    assert_eq!(result, expected);
}

#[test]
fn test_traitorous_commander() {
    // n = 7, one traitor allowed, traitorous commander (index 0)
    // In this simulation, when the commander is traitorous,
    // he sends alternating orders: false to odd-index lieutenants, true to even-index lieutenants.
    // Loyal lieutenants relay what they receive.
    // The majority vote for each loyal lieutenant becomes a tie, defaulting to false.
    let n = 7;
    let t = 1;
    let commander_value = true; // provided value is ignored since commander is traitorous.
    let mut traitors = HashSet::new();
    traitors.insert(0); // commander is traitor
    let result = simulate(n, t, commander_value, &traitors).unwrap();

    // All lieutenants (1 through 6) are loyal.
    // Each lieutenant receives mixed messages resulting in a tie, so default decision is false.
    let mut expected = HashMap::new();
    for i in 1..n {
        expected.insert(i, false);
    }
    assert_eq!(result, expected);
}

#[test]
fn test_traitorous_lieutenants() {
    // n = 7, commander is loyal and sends true.
    // Traitorous lieutenants (indices 3 and 4) always relay false.
    // Loyal lieutenants (indices 1, 2, 5, 6) relay true.
    // Each loyal lieutenant receives: direct true from commander + from relays:
    // 3 loyal trues + 2 traitor falses. Total: 4 trues, 2 falses.
    // Majority => true.
    let n = 7;
    let t = 2;
    let commander_value = true;
    let mut traitors = HashSet::new();
    traitors.insert(3);
    traitors.insert(4);
    let result = simulate(n, t, commander_value, &traitors).unwrap();

    let mut expected = HashMap::new();
    // Loyal lieutenants: indices 1,2,5,6.
    for &i in &[1, 2, 5, 6] {
        expected.insert(i, true);
    }
    assert_eq!(result, expected);
}

#[test]
fn test_invalid_traitor_condition() {
    // n = 5 and t = 2; condition 3t + 1 <= n is violated (7 > 5).
    // The simulation should return an error.
    let n = 5;
    let t = 2;
    let commander_value = true;
    let traitors: HashSet<usize> = HashSet::new();
    let result = simulate(n, t, commander_value, &traitors);
    assert!(result.is_err());
}

#[test]
fn test_all_lieutenants_traitors() {
    // n = 7, commander is loyal, but all lieutenants (indices 1..6) are traitors.
    // Loyal lieutenants list is empty so result should be an empty map.
    let n = 7;
    let t = 6; // maximum allowed since 3*6+1 == 19 > 7, but the condition for t must be respected.
    // To satisfy 3t+1 <= n, this scenario cannot occur.
    // Instead, we simulate a scenario where n = 13 and t = 6 (3*6+1 = 19 > 13) is still invalid.
    // We need a valid scenario where all lieutenants are traitors.
    // Let n = 7 and t = 6 is not valid by the constraints.
    // So we change it: Let n = 7 and make lieutenants all traitors except commander.
    let n = 7;
    let t = 6; // To satisfy 3t + 1 <= n, this test would be invalid.
    // Instead, we use n = 13 and traitors = {1,2,3,4,5,6,7,8,9,10,11,12} leaving commander loyal.
    // But then t = 12 and 3*12+1 = 37, we need to satisfy 37 <= 13, which is not possible.
    // Correct approach: In a valid scenario, the maximum number of traitors is limited.
    // Therefore, test the scenario: commander loyal, and all allowed lieutenants are traitors.
    // For n = 7, maximum allowed traitors is t such that 3t+1 <= n. For t = 2, 3*2+1=7, scenario valid.
    // Now set traitors as all lieutenants except one.
    let n = 7;
    let t = 2; // Maximum traitors allowed.
    // Make lieutenants traitorous except one loyal lieutenant.
    // For instance, traitors are {1, 2, 3, 4, 6}, but that makes 5 traitors, not allowed.
    // We want to simulate the extreme where none of the lieutenants are loyal.
    // Under the constraint 3t+1 <= n, with n = 7, maximum t = 2.
    // So we simulate where lieutenants in set {1,2} are traitors, and others are loyal.
    // But then not all lieutenants are traitors.
    // Instead, test the edge where no loyal lieutenants exist:
    // For n = 1, only commander exists.
    let n = 1;
    let t = 0;
    let commander_value = true;
    let traitors: HashSet<usize> = HashSet::new();
    let result = simulate(n, t, commander_value, &traitors).unwrap();
    let expected: HashMap<usize, bool> = HashMap::new();
    assert_eq!(result, expected);
}

#[test]
fn test_single_commander_only() {
    // n = 1, only the commander exists, so there are no lieutenants.
    let n = 1;
    let t = 0;
    let commander_value = false;
    let traitors: HashSet<usize> = HashSet::new();
    let result = simulate(n, t, commander_value, &traitors).unwrap();
    let expected: HashMap<usize, bool> = HashMap::new();
    assert_eq!(result, expected);
}