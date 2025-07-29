use std::sync::{Arc, Mutex};

#[derive(Debug, Clone, PartialEq)]
enum NodeState {
    Leader,
    Follower,
    Candidate,
}

#[derive(Debug, Clone)]
struct LogEntry {
    term: usize,
    command: i64,
}

#[derive(Debug)]
struct Node {
    id: usize,
    current_term: usize,
    state: NodeState,
    log: Vec<LogEntry>,
    state_machine: i64,
}

impl Node {
    fn new(id: usize, term: usize, state: NodeState) -> Self {
        Node {
            id,
            current_term: term,
            state,
            log: Vec::new(),
            state_machine: 0,
        }
    }

    // Append a log entry to the node's log if there are no conflicts.
    // For this simplified simulation, we assume that the logs are applied in order
    // and that any previously committed log entries do not conflict.
    fn append_entry(&mut self, entry: LogEntry) -> bool {
        // In a complete implementation, we would check index and term conflict.
        // In our simulation, assume append always succeeds.
        self.log.push(entry);
        true
    }

    // Apply a command from a log entry to the state machine.
    fn apply_entry(&mut self, entry: &LogEntry) {
        self.state_machine += entry.command;
    }
}

// The Cluster simulates a set of nodes participating in a consensus protocol.
struct Cluster {
    nodes: Vec<Arc<Mutex<Node>>>,
    majority: usize,
}

impl Cluster {
    fn new(num_nodes: usize) -> Self {
        let mut nodes = Vec::with_capacity(num_nodes);
        // All nodes start with term 1.
        // For simulation, select node 0 as the leader.
        for i in 0..num_nodes {
            let state = if i == 0 { NodeState::Leader } else { NodeState::Follower };
            nodes.push(Arc::new(Mutex::new(Node::new(i, 1, state))));
        }
        Cluster {
            majority: (num_nodes / 2) + 1,
            nodes,
        }
    }

    // Get the current leader. In this simulation, assume node 0 is always the leader.
    fn get_leader(&self) -> Option<Arc<Mutex<Node>>> {
        for node in &self.nodes {
            if node.lock().unwrap().state == NodeState::Leader {
                return Some(Arc::clone(node));
            }
        }
        None
    }

    // Replicate the log entry from leader to followers.
    // In this simplified model, assume replication always succeeds.
    fn replicate_entry(&self, entry: &LogEntry) -> bool {
        let mut success_count = 0;
        for node in &self.nodes {
            // Leader already has the entry, so we count replication success for leader automatically.
            let mut node_guard = node.lock().unwrap();
            if node_guard.state == NodeState::Leader {
                success_count += 1;
                continue;
            }
            // Attempt to append the entry on follower.
            if node_guard.append_entry(entry.clone()) {
                success_count += 1;
            }
        }
        // Check if replication has reached majority.
        success_count >= self.majority
    }

    // Once an entry is committed (replicated to majority), apply the entry to state machines.
    fn apply_entry(&self, entry: &LogEntry) {
        for node in &self.nodes {
            let mut node_guard = node.lock().unwrap();
            // In an actual raft protocol, nodes ensure
            // that entries are applied in order and only once.
            // Here, we simplify by applying if not already applied.
            // We assume that if the node log length is at least as long as the number
            // of committed entries, then the entry at the corresponding index has been applied.
            // For simulation, we just apply it.
            node_guard.apply_entry(entry);
        }
    }
}

/// Simulate a distributed consensus consensus protocol based on a simplified Raft algorithm.
///
/// # Parameters
/// * `num_nodes`: The number of nodes in the cluster.
/// * `commands`: A vector of strings representing the commands; each command is attempted to be parsed into an i64.
///
/// # Returns
/// * `Ok(Vec<i64>)`: A vector containing the final state machine values for each node if the consensus is successful.
/// * `Err(String)`: An error message if the simulation fails (e.g., no nodes in the cluster).
///
/// # Behavior
/// * A leader is elected automatically (node with id 0). The leader processes commands sequentially.
/// * For each command, the leader parses the command into an i64. If parsing fails, the command is ignored.
/// * If the command is valid, the leader appends the command as a log entry with the current term.
/// * The leader replicates the log entry to a majority of nodes. If replication fails,
///   the simulation aborts with an error (simulating an unrecoverable partition error).
/// * Once the entry is committed, all nodes apply the log entry to their local state machines.
/// * Finally, the simulation returns the state machine values for all nodes.
pub fn simulate_consensus(num_nodes: usize, commands: Vec<String>) -> Result<Vec<i64>, String> {
    if num_nodes == 0 {
        return Err("No nodes available in the cluster.".to_string());
    }

    let cluster = Cluster::new(num_nodes);

    let leader_arc = match cluster.get_leader() {
        Some(node) => node,
        None => return Err("No leader found in the cluster.".to_string()),
    };

    // Process each command sequentially.
    for cmd in commands {
        // Parse the command as i64.
        if let Ok(value) = cmd.parse::<i64>() {
            // Create a new log entry in the leader.
            let entry = {
                let mut leader = leader_arc.lock().unwrap();
                let new_entry = LogEntry {
                    term: leader.current_term,
                    command: value,
                };
                leader.append_entry(new_entry.clone());
                new_entry
            };

            // Replicate the entry to the cluster.
            if !cluster.replicate_entry(&entry) {
                return Err("Failed to replicate log entry to majority of nodes.".to_string());
            }

            // Once replicated to a majority, commit the entry by applying it to the state machine.
            cluster.apply_entry(&entry);
        }
        // If the command can't be parsed to an i64, ignore it.
    }

    // Retrieve the final state machine values for all nodes.
    let mut results = Vec::with_capacity(num_nodes);
    for node in &cluster.nodes {
        results.push(node.lock().unwrap().state_machine);
    }
    Ok(results)
}