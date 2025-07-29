use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq)]
pub enum OperationType {
    Read,
    Write,
}

struct Node {
    id: usize,
    kv: HashMap<String, String>,
    faulty: bool,
}

impl Node {
    fn new(id: usize) -> Self {
        Self {
            id,
            kv: HashMap::new(),
            faulty: false,
        }
    }

    // In a real implementation, this would involve complex communication.
    // Here, an honest node always votes yes, a faulty node always votes no.
    fn prepare(&self, _tx: &[(usize, OperationType, String, Option<String>)]) -> bool {
        if self.faulty {
            false
        } else {
            true
        }
    }
}

pub struct Coordinator {
    nodes: Vec<Node>,
}

impl Coordinator {
    // Constructs a new Coordinator with num_nodes nodes.
    // num_nodes must satisfy (num_nodes - 1)%3 == 0
    pub fn new(num_nodes: usize) -> Self {
        if num_nodes == 0 || (num_nodes - 1) % 3 != 0 {
            panic!("Number of nodes must satisfy N = 3f + 1 for some f >= 0");
        }
        let mut nodes = Vec::with_capacity(num_nodes);
        for i in 0..num_nodes {
            nodes.push(Node::new(i));
        }
        Self { nodes }
    }

    // Sets faulty nodes based on provided vector.
    // Nodes with ids in faulty_node_ids are marked as faulty; others are honest.
    pub fn set_faulty_nodes(&mut self, faulty_node_ids: Vec<usize>) {
        for node in self.nodes.iter_mut() {
            if faulty_node_ids.contains(&node.id) {
                node.faulty = true;
            } else {
                node.faulty = false;
            }
        }
    }

    // Executes a transaction consisting of operations on the nodes.
    // A transaction is a vector of (node_id, OperationType, key, Option<value>).
    // The operation is atomic: either all honest nodes commit the changes, or none do.
    // The function simulates a two-phase commit with a simplified Byzantine fault tolerant consensus.
    pub fn execute_transaction(
        &mut self,
        transaction: Vec<(usize, OperationType, String, Option<String>)>,
    ) -> Result<(), String> {
        let total_nodes = self.nodes.len();
        let f = (total_nodes - 1) / 3;
        let faulty_count = self.nodes.iter().filter(|n| n.faulty).count();
        // If number of faulty nodes exceeds tolerance, reject the transaction.
        if faulty_count > f {
            return Err("Too many faulty nodes".to_string());
        }
        // Validate that all operations target honest nodes.
        for op in &transaction {
            if let Some(node) = self.nodes.get(op.0) {
                if node.faulty {
                    return Err("Operation targets a faulty node".to_string());
                }
            } else {
                return Err("Invalid node id in transaction".to_string());
            }
        }
        // Prepare phase: Collect votes from all nodes.
        let mut yes_count = 0;
        for node in &self.nodes {
            if node.prepare(&transaction) {
                yes_count += 1;
            }
        }
        if yes_count < (2 * f + 1) {
            return Err("Consensus not reached".to_string());
        }
        // Create a simulated global state based on one honest node.
        let honest_node = self
            .nodes
            .iter()
            .find(|n| !n.faulty)
            .ok_or("No honest node available")?;
        let mut new_state = honest_node.kv.clone();
        // Apply transaction operations sequentially in a temporary state.
        for op in &transaction {
            match op.1 {
                OperationType::Read => {
                    // Read operations are used for sequencing; they do not modify state.
                    // In a full implementation, we could validate the read result.
                    // Here, no action is necessary.
                }
                OperationType::Write => {
                    if let Some(ref value) = op.3 {
                        new_state.insert(op.2.clone(), value.clone());
                    } else {
                        return Err("Write operation missing value".to_string());
                    }
                }
            }
        }
        // Commit phase: update the state of each node.
        // Honest nodes are updated to the new committed state.
        // Faulty nodes simulate arbitrary behavior by not updating.
        for node in self.nodes.iter_mut() {
            if !node.faulty {
                node.kv = new_state.clone();
            }
        }
        Ok(())
    }

    // Returns the key-value state of each node.
    // This is used for testing consistency among nodes.
    pub fn get_nodes_state(&self) -> Vec<HashMap<String, String>> {
        self.nodes.iter().map(|node| node.kv.clone()).collect()
    }
}