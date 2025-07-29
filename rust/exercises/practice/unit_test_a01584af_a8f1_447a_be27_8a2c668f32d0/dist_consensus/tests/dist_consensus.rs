use std::result::Result;
use std::string::String;
use std::vec::Vec;

// Assuming the student's library exposes the following function:
//
// pub fn simulate_consensus(num_nodes: usize, commands: Vec<String>) -> Result<Vec<i64>, String>
//
// The function should simulate the consensus protocol over a cluster of nodes, apply valid commands,
// and return a vector with the final state of each node's state machine, or an error message if the simulation fails.
use dist_consensus::simulate_consensus;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_empty_commands() {
        // A cluster with valid nodes but no commands.
        let result = simulate_consensus(5, Vec::new());
        assert!(result.is_ok());
        let states = result.unwrap();
        // Each node's state machine should remain at 0.
        assert_eq!(states, vec![0, 0, 0, 0, 0]);
    }

    #[test]
    fn test_valid_commands() {
        // Cluster with 5 nodes and three valid integer commands.
        let commands = vec!["10".to_string(), "20".to_string(), "30".to_string()];
        let result = simulate_consensus(5, commands);
        assert!(result.is_ok());
        let states = result.unwrap();
        // Sum of valid commands is 10 + 20 + 30 = 60.
        for state in states.iter() {
            assert_eq!(*state, 60);
        }
    }

    #[test]
    fn test_invalid_commands_ignored() {
        // Cluster with 5 nodes and a mix of valid and invalid commands.
        let commands = vec![
            "10".to_string(),
            "foo".to_string(),
            "20".to_string(),
            "bar".to_string(),
        ];
        let result = simulate_consensus(5, commands);
        assert!(result.is_ok());
        let states = result.unwrap();
        // Only valid commands "10" and "20" contribute, so expected sum is 30.
        for state in states.iter() {
            assert_eq!(*state, 30);
        }
    }

    #[test]
    fn test_even_number_of_nodes() {
        // For an even number of nodes, majority is defined as strictly more than half.
        // In a cluster of 4 nodes, majority requires at least 3 votes.
        let commands = vec![
            "5".to_string(),
            "15".to_string(),
            "25".to_string(),
            "35".to_string(),
        ];
        let result = simulate_consensus(4, commands);
        assert!(result.is_ok());
        let states = result.unwrap();
        // Sum: 5 + 15 + 25 + 35 = 80.
        for state in states.iter() {
            assert_eq!(*state, 80);
        }
    }

    #[test]
    fn test_unrecoverable_error_with_zero_nodes() {
        // A simulation with zero nodes in the cluster should be treated as an unrecoverable error.
        let commands = vec!["10".to_string(), "20".to_string()];
        let result = simulate_consensus(0, commands);
        assert!(result.is_err());
    }

    #[test]
    fn test_large_simulation() {
        // Test with a larger cluster and a greater number of commands to evaluate performance and consistency.
        let num_nodes = 7;
        let mut commands = Vec::new();
        let mut expected_sum = 0i64;
        for i in 1..=100 {
            let cmd = i.to_string();
            expected_sum += i;
            commands.push(cmd);
        }
        let result = simulate_consensus(num_nodes, commands);
        assert!(result.is_ok());
        let states = result.unwrap();
        // Validate that all nodes have reached the same state.
        for state in states.iter() {
            assert_eq!(*state, expected_sum);
        }
    }
}