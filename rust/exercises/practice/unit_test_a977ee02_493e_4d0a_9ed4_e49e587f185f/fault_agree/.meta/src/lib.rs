use std::collections::HashSet;

pub struct ConsensusSystem {
    num_nodes: usize,
    fault: usize,
    proposals: Vec<(usize, String)>,
    per_node_seen: Vec<HashSet<String>>,
    final_log: Option<Vec<String>>,
}

impl ConsensusSystem {
    pub fn new(num_nodes: usize, fault: usize) -> Self {
        let mut per_node_seen = Vec::with_capacity(num_nodes);
        for _ in 0..num_nodes {
            per_node_seen.push(HashSet::new());
        }
        ConsensusSystem {
            num_nodes,
            fault,
            proposals: Vec::new(),
            per_node_seen,
            final_log: None,
        }
    }

    pub fn propose(&mut self, node_id: usize, event: String) {
        if node_id >= self.num_nodes {
            return;
        }
        // Only add the event if it has not already been proposed by this node
        if !self.per_node_seen[node_id].contains(&event) {
            self.per_node_seen[node_id].insert(event.clone());
            self.proposals.push((node_id, event));
        }
    }

    pub fn run_consensus(&mut self) {
        // Simulate a consensus process by preserving the global order of accepted proposals.
        // In a real system, this would involve more complex algorithms to handle faulty nodes,
        // message ordering, and asynchronous network conditions.
        let mut consensus_log = Vec::new();
        for (_node, event) in &self.proposals {
            consensus_log.push(event.clone());
        }
        self.final_log = Some(consensus_log);
    }

    pub fn get_log(&self, _node_id: usize) -> Option<&Vec<String>> {
        // In this simplified simulation, every non-faulty node obtains the same final log.
        self.final_log.as_ref()
    }
}