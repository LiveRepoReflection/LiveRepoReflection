use std::collections::{HashMap, HashSet};

#[derive(Debug, PartialEq)]
pub enum Error {
    InvalidParameters,
}

pub fn simulate(n: usize, t: usize, commander_value: bool, traitors: &HashSet<usize>) -> Result<HashMap<usize, bool>, Error> {
    // Validate the parameter constraint: 3t + 1 <= n
    if 3 * t + 1 > n {
        return Err(Error::InvalidParameters);
    }
    
    // If there are no generals, return an empty map.
    if n == 0 {
        return Ok(HashMap::new());
    }
    
    // In our simulation, index 0 is the commander and indices 1..n are lieutenants.
    
    // Round 1: Commander sends orders to every lieutenant.
    // If the commander is loyal, he sends the same order to every lieutenant.
    // If the commander is traitorous, he sends alternating orders:
    // For lieutenant with even index, send true; for odd index, send false.
    let mut direct_messages: HashMap<usize, bool> = HashMap::new();
    if traitors.contains(&0) {
        for lieutenant in 1..n {
            direct_messages.insert(lieutenant, lieutenant % 2 == 0);
        }
    } else {
        for lieutenant in 1..n {
            direct_messages.insert(lieutenant, commander_value);
        }
    }
    
    // Round 2: Every lieutenant sends a relay message.
    // Loyal lieutenants relay the message they received unmodified.
    // Traitorous lieutenants deliberately relay false.
    let mut relay_messages: HashMap<usize, bool> = HashMap::new();
    for lieutenant in 1..n {
        if traitors.contains(&lieutenant) {
            relay_messages.insert(lieutenant, false);
        } else {
            let msg = *direct_messages.get(&lieutenant).unwrap_or(&false);
            relay_messages.insert(lieutenant, msg);
        }
    }
    
    // Final decision: Each loyal lieutenant aggregates the direct message from the commander
    // and the relay messages from all other lieutenants. The decision is determined by majority vote.
    // In the event of a tie, the lieutenant defaults to false.
    let mut final_decisions: HashMap<usize, bool> = HashMap::new();
    for lieutenant in 1..n {
        if traitors.contains(&lieutenant) {
            continue;
        }
        let mut true_count = 0;
        let mut false_count = 0;
        
        if let Some(&msg) = direct_messages.get(&lieutenant) {
            if msg {
                true_count += 1;
            } else {
                false_count += 1;
            }
        }
        
        for (&other, &relay_msg) in relay_messages.iter() {
            if other == lieutenant {
                continue;
            }
            if relay_msg {
                true_count += 1;
            } else {
                false_count += 1;
            }
        }
        
        let decision = if true_count > false_count { true } else { false };
        final_decisions.insert(lieutenant, decision);
    }
    
    Ok(final_decisions)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashSet;

    #[test]
    fn test_commander_loyal_no_traitors() {
        let n = 7;
        let t = 0;
        let commander_value = true;
        let traitors = HashSet::new();
        let result = simulate(n, t, commander_value, &traitors).unwrap();
        let mut expected = HashMap::new();
        for lieutenant in 1..n {
            expected.insert(lieutenant, true);
        }
        assert_eq!(result, expected);
    }
    
    #[test]
    fn test_traitorous_commander() {
        let n = 7;
        let t = 1;
        let commander_value = true;
        let mut traitors = HashSet::new();
        traitors.insert(0);
        let result = simulate(n, t, commander_value, &traitors).unwrap();
        let mut expected = HashMap::new();
        for lieutenant in 1..n {
            expected.insert(lieutenant, false);
        }
        assert_eq!(result, expected);
    }
    
    #[test]
    fn test_traitorous_lieutenants() {
        let n = 7;
        let t = 2;
        let commander_value = true;
        let mut traitors = HashSet::new();
        traitors.insert(3);
        traitors.insert(4);
        let result = simulate(n, t, commander_value, &traitors).unwrap();
        let mut expected = HashMap::new();
        // Loyal lieutenants: indices 1, 2, 5, 6.
        for &i in &[1, 2, 5, 6] {
            expected.insert(i, true);
        }
        assert_eq!(result, expected);
    }
    
    #[test]
    fn test_invalid_traitor_condition() {
        let n = 5;
        let t = 2;
        let commander_value = true;
        let traitors = HashSet::new();
        let result = simulate(n, t, commander_value, &traitors);
        assert!(result.is_err());
    }
    
    #[test]
    fn test_single_commander_only() {
        let n = 1;
        let t = 0;
        let commander_value = false;
        let traitors = HashSet::new();
        let result = simulate(n, t, commander_value, &traitors).unwrap();
        let expected: HashMap<usize, bool> = HashMap::new();
        assert_eq!(result, expected);
    }
}