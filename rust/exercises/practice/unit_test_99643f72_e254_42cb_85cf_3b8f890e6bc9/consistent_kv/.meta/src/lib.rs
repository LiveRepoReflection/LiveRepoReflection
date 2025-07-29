use std::collections::HashMap;
use std::sync::Mutex;

pub struct Cluster {
    nodes: Mutex<Vec<Node>>,
    n: usize,
}

#[derive(Clone, PartialEq)]
enum NodeStatus {
    Active,
    Failed,
    Isolated,
}

struct Node {
    id: usize,
    status: NodeStatus,
    store: HashMap<String, String>,
}

impl Node {
    fn new(id: usize) -> Self {
        Node {
            id,
            status: NodeStatus::Active,
            store: HashMap::new(),
        }
    }
}

impl Cluster {
    pub fn new(n: usize) -> Self {
        let mut nodes = Vec::new();
        for i in 0..n {
            nodes.push(Node::new(i));
        }
        Cluster {
            nodes: Mutex::new(nodes),
            n,
        }
    }

    fn has_network_partition(&self, nodes: &Vec<Node>) -> bool {
        for node in nodes.iter() {
            if node.status == NodeStatus::Isolated {
                return true;
            }
        }
        false
    }

    fn active_count(&self, nodes: &Vec<Node>) -> usize {
        nodes.iter().filter(|n| n.status == NodeStatus::Active).count()
    }

    fn majority(&self) -> usize {
        (self.n / 2) + 1
    }

    pub fn put(&self, key: &str, value: &str) -> Result<(), String> {
        let mut nodes = self.nodes.lock().unwrap();
        // if any node is isolated, simulate a network partition failure.
        if self.has_network_partition(&nodes) {
            return Err("Network partition: cannot commit put".to_string());
        }
        // Check that the number of active nodes meets the majority requirement.
        let active = self.active_count(&nodes);
        if active < self.majority() {
            return Err("Not enough nodes active to form a majority".to_string());
        }
        // Simulate consensus by writing to all active nodes.
        for node in nodes.iter_mut() {
            if node.status == NodeStatus::Active {
                node.store.insert(key.to_string(), value.to_string());
            }
        }
        Ok(())
    }

    pub fn get(&self, key: &str) -> Result<String, String> {
        let nodes = self.nodes.lock().unwrap();
        if self.has_network_partition(&nodes) {
            return Err("Network partition: cannot perform get".to_string());
        }
        let active = self.active_count(&nodes);
        if active < self.majority() {
            return Err("Not enough nodes active to form a majority".to_string());
        }
        // For strong consistency, assume all active nodes hold the same value.
        // Return the value from the first active node that contains the key.
        for node in nodes.iter() {
            if node.status == NodeStatus::Active {
                if let Some(val) = node.store.get(key) {
                    return Ok(val.clone());
                }
            }
        }
        Err("Key not found".to_string())
    }

    pub fn fail_node(&mut self, id: usize) -> Result<(), String> {
        let mut nodes = self.nodes.lock().unwrap();
        if id >= nodes.len() {
            return Err("Node id out of range".to_string());
        }
        nodes[id].status = NodeStatus::Failed;
        Ok(())
    }

    pub fn recover_node(&mut self, id: usize) -> Result<(), String> {
        let mut nodes = self.nodes.lock().unwrap();
        if id >= nodes.len() {
            return Err("Node id out of range".to_string());
        }
        // When a node recovers, it becomes active and synchronizes its data.
        nodes[id].status = NodeStatus::Active;
        if let Some(active_node) = nodes.iter().find(|n| n.status == NodeStatus::Active && n.id != id) {
            nodes[id].store = active_node.store.clone();
        }
        Ok(())
    }

    pub fn isolate_node(&mut self, id: usize) -> Result<(), String> {
        let mut nodes = self.nodes.lock().unwrap();
        if id >= nodes.len() {
            return Err("Node id out of range".to_string());
        }
        nodes[id].status = NodeStatus::Isolated;
        Ok(())
    }

    pub fn heal_partition(&mut self) -> Result<(), String> {
        let mut nodes = self.nodes.lock().unwrap();
        for node in nodes.iter_mut() {
            if node.status == NodeStatus::Isolated {
                node.status = NodeStatus::Active;
            }
        }
        Ok(())
    }
}