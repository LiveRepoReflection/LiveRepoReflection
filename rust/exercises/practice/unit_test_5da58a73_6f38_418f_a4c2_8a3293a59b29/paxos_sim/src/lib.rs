use rand::prelude::*;

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
    pub fn new(
        num_nodes: usize,
        accept_probability: f64,
        fault_percentage: f64,
        max_rounds: usize,
        seed: u64,
        initial_states: Vec<i64>,
    ) -> Self {
        assert!(accept_probability >= 0.0 && accept_probability <= 1.0);
        assert!(fault_percentage >= 0.0 && fault_percentage <= 1.0);
        assert!(max_rounds >= 1);
        
        let mut rng = StdRng::seed_from_u64(seed);
        
        // If initial_states is provided and has the correct length, use it
        // Otherwise, generate random states
        let node_states = if initial_states.len() == num_nodes {
            initial_states
        } else {
            (0..num_nodes).map(|_| rng.gen_range(-1000..1000)).collect()
        };
        
        // Determine which nodes are Byzantine
        let byzantine_count = (num_nodes as f64 * fault_percentage).round() as usize;
        let mut byzantine_nodes = vec![false; num_nodes];
        
        // Randomly select nodes to be Byzantine
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
    
    pub fn run_simulation(&mut self) -> bool {
        if self.num_nodes == 0 {
            return true; // Trivially in consensus
        }
        
        for _ in 0..self.max_rounds {
            // Check if consensus has been reached
            if self.is_consensus_reached() {
                return true;
            }
            
            // Run a single round
            self.run_round();
        }
        
        // After max_rounds, check if consensus was reached
        self.is_consensus_reached()
    }
    
    fn run_round(&mut self) {
        if self.num_nodes == 0 {
            return;
        }
        
        // Select a leader for this round
        let leader_id = self.rng.gen_range(0..self.num_nodes);
        
        // Determine the proposal value
        let proposal = if self.byzantine_nodes[leader_id] {
            // Byzantine node can propose any value
            self.rng.gen_range(-1000..1000)
        } else {
            // Honest node proposes its current state
            self.node_states[leader_id]
        };
        
        // Each node decides whether to accept the proposal
        let mut accept_count = 0;
        
        for node_id in 0..self.num_nodes {
            let accepts = if self.byzantine_nodes[node_id] {
                // Byzantine node might accept or reject unpredictably
                self.rng.gen_bool(0.5)
            } else {
                // Honest node accepts with accept_probability
                self.rng.gen_bool(self.accept_probability)
            };
            
            if accepts {
                accept_count += 1;
            }
        }
        
        // If a majority accepts, update all honest nodes
        if accept_count > self.num_nodes / 2 {
            for node_id in 0..self.num_nodes {
                if !self.byzantine_nodes[node_id] {
                    self.node_states[node_id] = proposal;
                } else {
                    // Byzantine nodes might update or not
                    if self.rng.gen_bool(0.5) {
                        self.node_states[node_id] = proposal;
                    } else {
                        // Byzantine node might set a random state
                        self.node_states[node_id] = self.rng.gen_range(-1000..1000);
                    }
                }
            }
        }
    }
    
    fn is_consensus_reached(&self) -> bool {
        if self.num_nodes == 0 {
            return true;
        }
        
        // Filter out byzantine nodes for consensus check
        let honest_nodes: Vec<(usize, &i64)> = self.node_states.iter()
            .enumerate()
            .filter(|(i, _)| !self.byzantine_nodes[*i])
            .collect();
        
        if honest_nodes.is_empty() {
            return false; // If all nodes are byzantine, consensus is impossible
        }
        
        // Check if all honest nodes have the same state
        let first_state = honest_nodes[0].1;
        honest_nodes.iter().all(|(_, &state)| state == *first_state)
    }
    
    // Getter for testing
    pub fn get_node_states(&self) -> &Vec<i64> {
        &self.node_states
    }
}