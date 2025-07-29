use std::collections::HashMap;
use std::hash::{Hash, Hasher};
use std::collections::hash_map::DefaultHasher;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

pub struct Node {
    pub id: usize,
    store: Mutex<HashMap<String, String>>,
    is_down: Mutex<bool>,
}

impl Node {
    pub fn new(id: usize) -> Self {
        Self {
            id,
            store: Mutex::new(HashMap::new()),
            is_down: Mutex::new(false),
        }
    }

    pub fn write(&self, key: String, value: String) {
        if !self.is_down() {
            let mut store = self.store.lock().unwrap();
            store.insert(key, value);
        }
    }

    pub fn read(&self, key: &String) -> Option<String> {
        if self.is_down() {
            thread::sleep(Duration::from_millis(110));
            return None;
        }
        thread::sleep(Duration::from_millis(10));
        let store = self.store.lock().unwrap();
        store.get(key).cloned()
    }

    pub fn set_down(&self, down: bool) {
        let mut is_down = self.is_down.lock().unwrap();
        *is_down = down;
    }

    pub fn is_down(&self) -> bool {
        *self.is_down.lock().unwrap()
    }
}

pub struct DecentralizedKV {
    nodes: Vec<Arc<Node>>,
    replication_factor: usize,
}

impl DecentralizedKV {
    pub fn new(num_nodes: usize, replication_factor: usize) -> Self {
        let mut nodes = Vec::new();
        for i in 0..num_nodes {
            nodes.push(Arc::new(Node::new(i)));
        }
        Self { nodes, replication_factor }
    }

    fn hash_key(&self, key: &String) -> usize {
        let mut hasher = DefaultHasher::new();
        key.hash(&mut hasher);
        (hasher.finish() as usize) % self.nodes.len()
    }

    pub fn put(&self, key: String, value: String) {
        let primary_index = self.hash_key(&key);
        let total_nodes = self.nodes.len();
        let mut targets = Vec::new();
        targets.push(self.nodes[primary_index].clone());
        for i in 1..=self.replication_factor {
            let replica_index = (primary_index + i) % total_nodes;
            targets.push(self.nodes[replica_index].clone());
        }
        for node in targets {
            if !node.is_down() {
                node.write(key.clone(), value.clone());
            }
        }
    }

    pub fn get(&self, key: String) -> Option<String> {
        let primary_index = self.hash_key(&key);
        let total_nodes = self.nodes.len();
        let mut targets = Vec::new();
        targets.push(self.nodes[primary_index].clone());
        for i in 1..=self.replication_factor {
            let replica_index = (primary_index + i) % total_nodes;
            targets.push(self.nodes[replica_index].clone());
        }
        for node in targets {
            if let Some(val) = node.read(&key) {
                return Some(val);
            }
        }
        None
    }

    pub fn set_node_down(&self, node_id: usize) {
        if let Some(node) = self.nodes.iter().find(|n| n.id == node_id) {
            node.set_down(true);
        }
    }
    
    pub fn set_node_up(&self, node_id: usize) {
        if let Some(node) = self.nodes.iter().find(|n| n.id == node_id) {
            node.set_down(false);
        }
    }
}