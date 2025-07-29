use std::sync::{Arc, Mutex};

/// Represents a node in the distributed consensus algorithm.
pub struct Node {
    pub id: usize,
    /// The current state of the node.
    pub state: i32,
    /// The highest proposal id this node has promised to.
    pub promised_id: i32,
    /// The highest proposal id that this node has accepted.
    pub accepted_id: i32,
}

impl Node {
    /// Creates a new node with the given id and initial state.
    /// If the initial state is non-zero, it is treated as a previously accepted value, and both
    /// promised_id and accepted_id are set to that value.
    pub fn new(id: usize, initial_state: i32) -> Self {
        if initial_state != 0 {
            Node {
                id,
                state: initial_state,
                promised_id: initial_state,
                accepted_id: initial_state,
            }
        } else {
            Node {
                id,
                state: 0,
                promised_id: 0,
                accepted_id: 0,
            }
        }
    }

    /// Process a Prepare message.
    /// If the proposal_id is greater than the current promised_id, update promised_id and return a Promise.
    /// Otherwise, return None indicating a rejection (i.e. no response).
    pub fn process_prepare(&mut self, proposal_id: i32) -> Option<Promise> {
        if proposal_id > self.promised_id {
            self.promised_id = proposal_id;
            Some(Promise {
                node_id: self.id,
                accepted_id: self.accepted_id,
                state: self.state,
            })
        } else {
            None
        }
    }

    /// Process an Accept message.
    /// If the proposal_id is greater than or equal to the current accepted_id, then accept the proposal
    /// and update the state accordingly.
    pub fn process_accept(&mut self, proposal_id: i32, value: i32) {
        if proposal_id >= self.accepted_id {
            self.accepted_id = proposal_id;
            self.state = value;
            // Also update promised_id to ensure no lower proposals are accepted later.
            self.promised_id = proposal_id;
        }
    }
}

/// Represents a Promise response from a node after a Prepare message.
#[derive(Debug)]
pub struct Promise {
    pub node_id: usize,
    pub accepted_id: i32,
    pub state: i32,
}

/// Runs a single round of the consensus algorithm.
///
/// # Arguments
///
/// * `num_nodes` - The number of nodes in the system (must be greater than 1).
/// * `initial_states` - A vector with the initial state for each node.
/// * `proposed_value` - The new value proposed by the client.
///
/// # Returns
///
/// A vector with the final state of each node after the consensus round.
pub fn run_consensus_round(num_nodes: usize, initial_states: Vec<i32>, proposed_value: i32) -> Vec<i32> {
    assert!(num_nodes > 1, "Must have more than one node");
    assert!(initial_states.len() == num_nodes, "Initial states length must match number of nodes");

    // Create the nodes wrapped in a Mutex inside an Arc for thread-safe access.
    let nodes: Vec<Arc<Mutex<Node>>> = (0..num_nodes)
        .enumerate()
        .map(|(i, _)| Arc::new(Mutex::new(Node::new(i, initial_states[i]))))
        .collect();

    // Determine a proposal id that is higher than any promised id among all nodes.
    let mut max_promised = 0;
    for node in &nodes {
        let n = node.lock().unwrap();
        if n.promised_id > max_promised {
            max_promised = n.promised_id;
        }
    }
    let proposal_id = max_promised + 1;

    // Phase 1: Proposer (node 0) sends Prepare message to all nodes.
    let mut promises: Vec<Promise> = Vec::new();
    for node in &nodes {
        let mut n = node.lock().unwrap();
        if let Some(promise) = n.process_prepare(proposal_id) {
            promises.push(promise);
        }
    }

    // Check for majority (strictly more than num_nodes/2).
    let majority = (num_nodes / 2) + 1;
    if promises.len() < majority {
        // In this simulation, we assume majority is required.
        // If not reached, we return the current states without changes.
        return nodes.iter().map(|node| node.lock().unwrap().state).collect();
    }

    // Phase 2: Proposer chooses value to propose.
    // If any Promise includes a non-zero accepted value, choose the one with the highest accepted_id.
    let mut chosen_value = proposed_value;
    let mut highest_accepted_id = 0;
    for promise in &promises {
        if promise.accepted_id > highest_accepted_id {
            highest_accepted_id = promise.accepted_id;
            chosen_value = promise.state;
        }
    }

    // Phase 3: Proposer sends Accept message to all nodes.
    for node in &nodes {
        let mut n = node.lock().unwrap();
        n.process_accept(proposal_id, chosen_value);
    }

    // Phase 4: All nodes have now learned the chosen value.
    nodes.iter().map(|node| node.lock().unwrap().state).collect()
}