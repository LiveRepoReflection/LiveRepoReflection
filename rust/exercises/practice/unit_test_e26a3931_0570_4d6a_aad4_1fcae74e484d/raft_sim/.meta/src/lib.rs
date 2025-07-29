use std::collections::HashMap;
use std::sync::{mpsc, Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

use rand::Rng;

/// The state of a node in the Raft algorithm
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum NodeState {
    Follower,
    Candidate,
    Leader,
}

/// Message types for node communication
#[derive(Debug, Clone)]
pub enum Message {
    RequestVote {
        candidate_id: usize,
        term: u64,
    },
    GrantVote {
        voter_id: usize,
        term: u64,
        granted: bool,
    },
    ProposeValue {
        leader_id: usize,
        term: u64,
        value: u64,
    },
    AcknowledgeValue {
        follower_id: usize,
        term: u64,
        value: u64,
        success: bool,
    },
    Shutdown,
}

/// Configuration for the simulation
#[derive(Debug, Clone, Copy)]
pub struct SimulationConfig {
    pub num_nodes: usize,
    pub network_delay_ms_min: u64,
    pub network_delay_ms_max: u64,
    pub timeout_ms_min: u64,
    pub timeout_ms_max: u64,
    pub simulation_timeout_ms: u64,
    pub message_loss_probability: f64,
}

impl Default for SimulationConfig {
    fn default() -> Self {
        SimulationConfig {
            num_nodes: 3,
            network_delay_ms_min: 10,
            network_delay_ms_max: 50,
            timeout_ms_min: 150,
            timeout_ms_max: 300,
            simulation_timeout_ms: 5000,
            message_loss_probability: 0.1,
        }
    }
}

/// Node structure representing a server in the Raft cluster
struct Node {
    id: usize,
    state: NodeState,
    term: u64,
    voted_for: Option<usize>,
    committed_value: Option<u64>,
    votes_received: HashMap<usize, bool>,
    value_acks: HashMap<usize, bool>,
    proposed_value: Option<u64>,
    receivers: HashMap<usize, mpsc::Sender<Message>>,
    receiver: mpsc::Receiver<Message>,
    config: SimulationConfig,
}

impl Node {
    /// Create a new node
    fn new(
        id: usize,
        receivers: HashMap<usize, mpsc::Sender<Message>>,
        receiver: mpsc::Receiver<Message>,
        config: SimulationConfig,
    ) -> Self {
        Node {
            id,
            state: NodeState::Follower,
            term: 0,
            voted_for: None,
            committed_value: None,
            votes_received: HashMap::new(),
            value_acks: HashMap::new(),
            proposed_value: None,
            receivers,
            receiver,
            config,
        }
    }

    /// Send a message to another node with simulated network conditions
    fn send_message(&self, to_id: usize, message: Message) {
        let mut rng = rand::thread_rng();
        
        // Simulate message loss
        if rng.gen::<f64>() < self.config.message_loss_probability {
            return;
        }
        
        if let Some(sender) = self.receivers.get(&to_id) {
            let message_clone = message.clone();
            let sender_clone = sender.clone();
            let delay = rng.gen_range(self.config.network_delay_ms_min..=self.config.network_delay_ms_max);
            
            thread::spawn(move || {
                thread::sleep(Duration::from_millis(delay));
                let _ = sender_clone.send(message_clone);
            });
        }
    }

    /// Broadcast a message to all other nodes
    fn broadcast_message(&self, message: Message) {
        for node_id in self.receivers.keys() {
            if *node_id != self.id {
                self.send_message(*node_id, message.clone());
            }
        }
    }

    /// Start an election
    fn start_election(&mut self) {
        self.state = NodeState::Candidate;
        self.term += 1;
        self.voted_for = Some(self.id);
        self.votes_received.clear();
        self.votes_received.insert(self.id, true);  // Vote for self
        
        // Request votes from all other nodes
        let request_vote = Message::RequestVote {
            candidate_id: self.id,
            term: self.term,
        };
        self.broadcast_message(request_vote);
    }

    /// Process a vote request
    fn process_vote_request(&mut self, candidate_id: usize, term: u64) {
        let grant_vote = if term < self.term {
            // Reject vote if term is outdated
            false
        } else if term > self.term {
            // Update term and reset voted_for if we see a higher term
            self.term = term;
            self.state = NodeState::Follower;
            self.voted_for = None;
            true
        } else if self.voted_for.is_none() || self.voted_for == Some(candidate_id) {
            // Grant vote if we haven't voted or already voted for this candidate
            true
        } else {
            // Reject if we've already voted for someone else
            false
        };
        
        if grant_vote {
            self.voted_for = Some(candidate_id);
        }
        
        // Send vote response
        let vote_response = Message::GrantVote {
            voter_id: self.id,
            term: self.term,
            granted: grant_vote,
        };
        self.send_message(candidate_id, vote_response);
    }

    /// Process a vote response
    fn process_vote_response(&mut self, voter_id: usize, term: u64, granted: bool) {
        // Ignore if no longer a candidate or term has changed
        if self.state != NodeState::Candidate || term != self.term {
            return;
        }
        
        if granted {
            self.votes_received.insert(voter_id, true);
            
            // Check if we have majority
            let votes_count = self.votes_received.values().filter(|&&granted| granted).count();
            if votes_count > self.config.num_nodes / 2 {
                self.state = NodeState::Leader;
                
                // Propose a random value
                let value = rand::thread_rng().gen::<u64>();
                self.proposed_value = Some(value);
                self.value_acks.clear();
                self.value_acks.insert(self.id, true);  // Count self
                
                // Broadcast the value
                let propose_message = Message::ProposeValue {
                    leader_id: self.id,
                    term: self.term,
                    value,
                };
                self.broadcast_message(propose_message);
            }
        }
    }

    /// Process a value proposal from the leader
    fn process_value_proposal(&mut self, leader_id: usize, term: u64, value: u64) {
        let success = if term < self.term {
            // Reject if term is outdated
            false
        } else {
            // Accept the leader's term and value
            if term > self.term {
                self.term = term;
                self.voted_for = None;
            }
            self.state = NodeState::Follower;
            self.committed_value = Some(value);
            true
        };
        
        // Send acknowledgement
        let ack_message = Message::AcknowledgeValue {
            follower_id: self.id,
            term: self.term,
            value,
            success,
        };
        self.send_message(leader_id, ack_message);
    }

    /// Process a value acknowledgement from a follower
    fn process_value_acknowledgement(&mut self, follower_id: usize, term: u64, value: u64, success: bool) {
        // Ignore if no longer a leader or term has changed or different value
        if self.state != NodeState::Leader || term != self.term || self.proposed_value != Some(value) {
            return;
        }
        
        if success {
            self.value_acks.insert(follower_id, true);
            
            // Check if we have majority acknowledgements
            let acks_count = self.value_acks.values().filter(|&&acked| acked).count();
            if acks_count > self.config.num_nodes / 2 {
                // Commit the value
                self.committed_value = self.proposed_value;
            }
        }
    }

    /// Run the node's main loop
    fn run(&mut self) -> Option<u64> {
        let mut rng = rand::thread_rng();
        let start_time = Instant::now();
        let mut last_activity = Instant::now();
        let mut election_timeout = Duration::from_millis(
            rng.gen_range(self.config.timeout_ms_min..=self.config.timeout_ms_max)
        );
        
        while start_time.elapsed() < Duration::from_millis(self.config.simulation_timeout_ms) {
            // Check for election timeout (follower or candidate)
            if self.state != NodeState::Leader && last_activity.elapsed() > election_timeout {
                self.start_election();
                last_activity = Instant::now();
                election_timeout = Duration::from_millis(
                    rng.gen_range(self.config.timeout_ms_min..=self.config.timeout_ms_max)
                );
            }
            
            // Check for messages
            match self.receiver.recv_timeout(Duration::from_millis(10)) {
                Ok(message) => {
                    last_activity = Instant::now();
                    match message {
                        Message::RequestVote { candidate_id, term } => {
                            self.process_vote_request(candidate_id, term);
                        }
                        Message::GrantVote { voter_id, term, granted } => {
                            self.process_vote_response(voter_id, term, granted);
                        }
                        Message::ProposeValue { leader_id, term, value } => {
                            self.process_value_proposal(leader_id, term, value);
                        }
                        Message::AcknowledgeValue { follower_id, term, value, success } => {
                            self.process_value_acknowledgement(follower_id, term, value, success);
                        }
                        Message::Shutdown => {
                            break;
                        }
                    }
                    
                    // Reset election timeout on any message
                    if self.state == NodeState::Follower {
                        election_timeout = Duration::from_millis(
                            rng.gen_range(self.config.timeout_ms_min..=self.config.timeout_ms_max)
                        );
                    }
                }
                Err(mpsc::RecvTimeoutError::Timeout) => {
                    // Continue to check election timeout
                    continue;
                }
                Err(mpsc::RecvTimeoutError::Disconnected) => {
                    break;
                }
            }
            
            // Return early if we've committed a value
            if let Some(value) = self.committed_value {
                return Some(value);
            }
        }
        
        self.committed_value
    }
}

/// Simulate the Raft consensus algorithm
/// Returns Some((value, committed_nodes)) if consensus is reached, None otherwise
pub fn simulate(config: SimulationConfig) -> Option<(u64, usize)> {
    let mut senders = HashMap::new();
    let mut receivers = HashMap::new();
    
    // Create channels for each node
    for i in 0..config.num_nodes {
        let (sender, receiver) = mpsc::channel();
        senders.insert(i, sender);
        receivers.insert(i, receiver);
    }
    
    // Create a channel map for each node
    let mut node_channels = Vec::new();
    for i in 0..config.num_nodes {
        let mut node_senders = HashMap::new();
        for j in 0..config.num_nodes {
            node_senders.insert(j, senders[&j].clone());
        }
        node_channels.push((i, node_senders, receivers.remove(&i).unwrap()));
    }
    
    // Shared committed values
    let committed_values = Arc::new(Mutex::new(HashMap::new()));
    
    // Create and start each node in its own thread
    let mut handles = vec![];
    
    for (id, senders, receiver) in node_channels {
        let node_committed_values = Arc::clone(&committed_values);
        let node_config = config;
        
        let handle = thread::spawn(move || {
            let mut node = Node::new(id, senders, receiver, node_config);
            if let Some(value) = node.run() {
                let mut values = node_committed_values.lock().unwrap();
                values.insert(id, value);
            }
        });
        
        handles.push(handle);
    }
    
    // Wait for simulation timeout
    thread::sleep(Duration::from_millis(config.simulation_timeout_ms + 500));
    
    // Send shutdown message to all nodes
    for i in 0..config.num_nodes {
        for j in 0..config.num_nodes {
            let _ = senders[&j].send(Message::Shutdown);
        }
    }
    
    // Wait for all threads to finish
    for handle in handles {
        let _ = handle.join();
    }
    
    // Check if consensus was reached
    let committed_values = committed_values.lock().unwrap();
    if committed_values.is_empty() {
        return None;
    }
    
    // Find the most committed value
    let mut value_counts = HashMap::new();
    for &value in committed_values.values() {
        *value_counts.entry(value).or_insert(0) += 1;
    }
    
    let (consensus_value, count) = value_counts
        .into_iter()
        .max_by_key(|&(_, count)| count)
        .unwrap_or((0, 0));
    
    // Check if majority agreed on the value
    if count > config.num_nodes / 2 {
        Some((consensus_value, count))
    } else {
        None
    }
}