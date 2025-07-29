use std::collections::HashMap;
use std::hash::{Hash, Hasher};
use std::sync::{Arc, Mutex};
use std::collections::hash_map::DefaultHasher;

pub struct DistKvSystem {
    nodes: Vec<Arc<Mutex<Node>>>,
    replication_factor: usize,
}

pub struct Node {
    pub id: usize,
    pub data: HashMap<String, String>,
    pub failed: bool,
}

impl Node {
    pub fn new(id: usize) -> Self {
        Node {
            id,
            data: HashMap::new(),
            failed: false,
        }
    }
}

impl DistKvSystem {
    // Create a new system with n nodes and replication factor r.
    pub fn new(n: usize, r: usize) -> Self {
        let mut nodes = Vec::with_capacity(n);
        for i in 0..n {
            nodes.push(Arc::new(Mutex::new(Node::new(i))));
        }
        DistKvSystem {
            nodes,
            replication_factor: r,
        }
    }

    // Compute the primary node index for a given key using a simple hash mod scheme.
    fn primary_index(&self, key: &str) -> usize {
        let mut hasher = DefaultHasher::new();
        key.hash(&mut hasher);
        (hasher.finish() as usize) % self.nodes.len()
    }

    // Get the replication group for a key as a vector of node indices.
    // Primary node is first, followed by R replicas in order in the ring.
    fn replication_group(&self, key: &str) -> Vec<usize> {
        let total = self.nodes.len();
        let primary = self.primary_index(key);
        let mut group = Vec::with_capacity(self.replication_factor + 1);
        group.push(primary);
        for i in 1..=self.replication_factor {
            group.push((primary + i) % total);
        }
        group
    }

    // Put key-value pair into the system.
    // The operation must be performed at the primary node.
    // Replicates to R additional nodes if they are operational.
    pub fn put(&self, key: String, value: String) -> Result<(), String> {
        let group = self.replication_group(&key);
        // First, check primary node.
        let primary_id = group[0];
        let primary_node = self.nodes.get(primary_id).ok_or("Invalid primary node")?;
        {
            let mut node = primary_node.lock().map_err(|_| "Lock poisoned")?;
            if node.failed {
                return Err("Primary node is failed".to_string());
            }
            node.data.insert(key.clone(), value.clone());
        }
        // Replicate to other nodes.
        for &node_id in group.iter().skip(1) {
            if let Some(replica) = self.nodes.get(node_id) {
                let mut node = replica.lock().map_err(|_| "Lock poisoned")?;
                if !node.failed {
                    node.data.insert(key.clone(), value.clone());
                }
            }
        }
        Ok(())
    }

    // Get key-value from the system.
    // Query each node in the replication group until found.
    pub fn get(&self, key: String) -> Option<String> {
        let group = self.replication_group(&key);
        for &node_id in &group {
            if let Some(node_arc) = self.nodes.get(node_id) {
                let node = node_arc.lock().ok()?;
                if !node.failed {
                    if let Some(val) = node.data.get(&key) {
                        return Some(val.clone());
                    }
                }
            }
        }
        None
    }

    // Delete key-value pair from the system.
    // Deletes from primary and then replicates deletion to replicas.
    pub fn delete(&self, key: String) -> Result<(), String> {
        let group = self.replication_group(&key);
        let primary_id = group[0];
        let primary_node = self.nodes.get(primary_id).ok_or("Invalid primary node")?;
        {
            let mut node = primary_node.lock().map_err(|_| "Lock poisoned")?;
            if node.failed {
                return Err("Primary node is failed".to_string());
            }
            if node.data.remove(&key).is_none() {
                return Err("Key does not exist".to_string());
            }
        }
        // Delete key from the replicas.
        for &node_id in group.iter().skip(1) {
            if let Some(replica) = self.nodes.get(node_id) {
                let mut node = replica.lock().map_err(|_| "Lock poisoned")?;
                node.data.remove(&key);
            }
        }
        Ok(())
    }

    // Simulate failure of a node identified by its id.
    pub fn fail_node(&self, node_id: usize) -> Result<(), String> {
        if let Some(node_arc) = self.nodes.get(node_id) {
            let mut node = node_arc.lock().map_err(|_| "Lock poisoned")?;
            node.failed = true;
            Ok(())
        } else {
            Err("Node id not found".to_string())
        }
    }

    // For testing: get the primary node id for a given key.
    pub fn get_primary_node(&self, key: String) -> Option<usize> {
        let group = self.replication_group(&key);
        group.first().cloned()
    }

    // For testing: get the replication node ids (replicas) for a given key.
    pub fn get_replication_nodes(&self, key: String) -> Vec<usize> {
        let group = self.replication_group(&key);
        group.into_iter().skip(1).collect()
    }
}