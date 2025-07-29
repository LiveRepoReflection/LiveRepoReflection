use rand::prelude::*;
use std::collections::HashSet;

/// A simulator for a simplified distributed consensus algorithm
/// that models aspects of the Paxos consensus protocol.
pub struct ConsensusSimulator {
    num_nodes: usize,
    accept_probability: f64,
    fault_percentage: f64,
    max_rounds: usize,
    rng: StdRng,
    node_states: Vec<i64>,
    byzantine_nodes: Vec<bool>,
}

impl ConsensusSimulator {
    /// Creates a new simulator with the specified parameters.
    ///
    /// # Arguments
    ///
    /// * `num_nodes` - The number of nodes in the simulation
    /// * `accept_probability` - Probability that a non-Byzantine node accepts a proposal
    /// * `fault_percentage` - Percentage of nodes that are Byzantine (malicious)
    /// * `max_rounds` - Maximum number of rounds to run the simulation
    /// * `seed` - Random seed for deterministic behavior
    /// * `initial_states` - Initial state values for each node
    ///
    /// # Returns
    ///
    /// A new `ConsensusSimulator` instance
    pub fn new(
        num_nodes: usize,
        accept_probability: f64,
        fault_percentage: f64,
        max_rounds: usize,
        seed: u64,
        initial_states: Vec<i64>,
    ) -> Self {
        // Validate inputs
        if accept_probability < 0.0 || accept_probability > 1.0 {
            panic!("accept_probability must be between 0.0 and 1.0");
        }
        if fault_percentage < 0.0 || fault_percentage > 1.0 {
            panic!("fault_percentage must be between 0.0 and 1.0");
        }
        if max_rounds < 1 && num_nodes > 0 {
            panic!("max_rounds must be at least 1");
        }

        let mut rng = StdRng::seed_from_u64(seed);

        // Use provided initial states or generate random ones
        let node_states = if initial_states.len() == num_nodes {
            initial_states
        } else {
            (0..num_nodes).map(|_| rng.gen_range(-1000..1000)).collect()
        };

        // Determine which nodes are Byzantine
        let byzantine_count = (num_nodes as f64 * fault_percentage).round() as usize;
        let mut byzantine_nodes = vec![false; num_nodes];

        // Select byzantine nodes randomly
        let mut indices: Vec<usize> = (0..num_nodes).collect();
        indices.shuffle(&mut rng);
        
        for i in 0..byzantine_count.min(num_nodes) {
            byzantine_nodes[indices[i]] = true;
        }

        ConsensusSimulator {
            num_nodes,
            accept_probability,
            fault_percentage,
            max_rounds,
            rng,
            node_states,
            byzantine_nodes,
        }
    }

    /// Runs the consensus simulation for up to max_rounds or until consensus is reached.
    ///
    /// # Returns
    ///
    /// `true` if consensus was reached, `false` otherwise
    pub fn run_simulation(&mut self) -> bool {
        // Edge case: zero nodes
        if self.num_nodes == 0 {
            return true; // Trivially in consensus
        }

        // Check if all nodes are Byzantine
        if self.byzantine_nodes.iter().all(|&is_byzantine| is_byzantine) {
            return false; // Consensus impossible with all Byzantine nodes
        }

        // Check for initial consensus
        if self.is_consensus_reached() {
            return true;
        }

        // Run rounds until consensus or max_rounds
        for _ in 0..self.max_rounds {
            if self.run_round() && self.is_consensus_reached() {
                return true;
            }
        }

        // Final check for consensus
        self.is_consensus_reached()
    }

    /// Runs a single round of the consensus protocol.
    ///
    /// # Returns
    ///
    /// `true` if the round resulted in state changes, `false` otherwise
    fn run_round(&mut self) -> bool {
        // Skip if no nodes
        if self.num_nodes == 0 {
            return false;
        }

        // Select a leader for this round
        let leader_id = self.rng.gen_range(0..self.num_nodes);
        
        // Determine the proposal value
        let proposal = if self.byzantine_nodes[leader_id] {
            // Byzantine leader can propose any value
            self.rng.gen_range(-1000..1000)
        } else {
            // Honest leader proposes its current state
            self.node_states[leader_id]
        };

        // Process votes from all nodes
        let mut accept_count = 0;
        let mut votes = vec![false; self.num_nodes];
        
        for node_id in 0..self.num_nodes {
            let will_accept = if self.byzantine_nodes[node_id] {
                // Byzantine nodes vote unpredictably
                self.rng.gen_bool(0.5)
            } else {
                // Honest nodes accept with accept_probability
                self.rng.gen_bool(self.accept_probability)
            };
            
            votes[node_id] = will_accept;
            if will_accept {
                accept_count += 1;
            }
        }

        // Check if majority accepts
        let majority_threshold = self.num_nodes / 2;
        let proposal_accepted = accept_count > majority_threshold;
        
        if proposal_accepted {
            // Update states of honest nodes and track if changes made
            let mut changes_made = false;
            
            for node_id in 0..self.num_nodes {
                if !self.byzantine_nodes[node_id] {
                    // Honest nodes always adopt the consensus value
                    if self.node_states[node_id] != proposal {
                        self.node_states[node_id] = proposal;
                        changes_made = true;
                    }
                } else {
                    // Byzantine nodes might adopt the value or set random ones
                    if self.rng.gen_bool(0.3) {
                        // Sometimes update to consensus value
                        if self.node_states[node_id] != proposal {
                            self.node_states[node_id] = proposal;
                            changes_made = true;
                        }
                    } else if self.rng.gen_bool(0.5) {
                        // Sometimes set to random value
                        let old_state = self.node_states[node_id];
                        self.node_states[node_id] = self.rng.gen_range(-1000..1000);
                        if old_state != self.node_states[node_id] {
                            changes_made = true;
                        }
                    }
                    // Otherwise don't change
                }
            }
            
            return changes_made;
        }
        
        false // No changes made this round
    }

    /// Checks if consensus has been reached among all honest nodes.
    ///
    /// # Returns
    ///
    /// `true` if all honest nodes have the same state, `false` otherwise
    fn is_consensus_reached(&self) -> bool {
        if self.num_nodes == 0 {
            return true;
        }

        // Find all honest nodes
        let honest_nodes: Vec<usize> = (0..self.num_nodes)
            .filter(|&i| !self.byzantine_nodes[i])
            .collect();
        
        if honest_nodes.is_empty() {
            return false; // No honest nodes, consensus impossible
        }
        
        // Check if all honest nodes have the same state
        let first_state = self.node_states[honest_nodes[0]];
        honest_nodes.iter().all(|&idx| self.node_states[idx] == first_state)
    }

    /// Returns the current state of all nodes.
    ///
    /// # Returns
    ///
    /// A reference to the vector containing the state of each node
    pub fn get_node_states(&self) -> &Vec<i64> {
        &self.node_states
    }
    
    /// Returns which nodes are Byzantine.
    ///
    /// # Returns
    ///
    /// A reference to the vector indicating which nodes are Byzantine
    pub fn get_byzantine_nodes(&self) -> &Vec<bool> {
        &self.byzantine_nodes
    }
    
    /// Returns statistics about the current state distribution.
    ///
    /// # Returns
    ///
    /// A tuple containing (number of unique states, most common state, count of most common state)
    pub fn get_state_statistics(&self) -> (usize, i64, usize) {
        if self.num_nodes == 0 {
            return (0, 0, 0);
        }
        
        // Count occurrences of each state
        let mut state_counts = std::collections::HashMap::new();
        for &state in &self.node_states {
            *state_counts.entry(state).or_insert(0) += 1;
        }
        
        // Find the most common state
        let most_common = state_counts
            .iter()
            .max_by_key(|&(_, count)| count)
            .unwrap_or((&0, &0));
        
        (state_counts.len(), *most_common.0, *most_common.1)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_consensus() {
        let mut simulator = ConsensusSimulator::new(
            5,
            0.8,
            0.0,
            10,
            12345,
            vec![1, 2, 1, 2, 1],
        );
        
        assert!(simulator.run_simulation());
        
        // All nodes should have the same state
        let states = simulator.get_node_states();
        let first_state = states[0];
        for state in states {
            assert_eq!(*state, first_state);
        }
    }
    
    #[test]
    fn test_zero_nodes() {
        let mut simulator = ConsensusSimulator::new(
            0,
            0.5,
            0.0,
            5,
            67890,
            vec![],
        );
        
        assert!(simulator.run_simulation());
    }
    
    #[test]
    fn test_all_byzantine() {
        let mut simulator = ConsensusSimulator::new(
            5,
            0.5,
            1.0,
            10,
            13579,
            vec![1, 1, 1, 1, 1],
        );
        
        assert!(!simulator.run_simulation());
    }
    
    #[test]
    fn test_initial_consensus() {
        let mut simulator = ConsensusSimulator::new(
            5,
            0.5,
            0.0,
            10,
            98765,
            vec![42, 42, 42, 42, 42], // All start with same state
        );
        
        assert!(simulator.run_simulation());
        
        let states = simulator.get_node_states();
        for state in states {
            assert_eq!(*state, 42);
        }
    }
}