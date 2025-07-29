use std::collections::{BTreeMap, HashMap};
use std::hash::{Hash, Hasher};
use std::collections::hash_map::DefaultHasher;
use std::sync::{Arc, Mutex};
use std::thread;

struct Node {
    id: usize,
    data: Mutex<BTreeMap<String, String>>,
    active: Mutex<bool>,
}

impl Node {
    fn new(id: usize) -> Self {
        Node {
            id,
            data: Mutex::new(BTreeMap::new()),
            active: Mutex::new(true),
        }
    }

    fn is_active(&self) -> bool {
        let active = self.active.lock().unwrap();
        *active
    }
}

pub struct RangeStore {
    nodes: Vec<Arc<Node>>,
    replication: usize,
}

impl RangeStore {
    pub fn new(total_nodes: usize, replication: usize) -> Self {
        let mut nodes = Vec::new();
        for i in 0..total_nodes {
            nodes.push(Arc::new(Node::new(i)));
        }
        RangeStore {
            nodes,
            replication: if replication > total_nodes { total_nodes } else { replication },
        }
    }

    fn hash_key(key: &String) -> u64 {
        let mut hasher = DefaultHasher::new();
        key.hash(&mut hasher);
        hasher.finish()
    }

    fn get_replica_indices(&self, key: &String) -> Vec<usize> {
        let hash = Self::hash_key(key);
        let primary_index = (hash as usize) % self.nodes.len();
        (0..self.replication)
            .map(|i| (primary_index + i) % self.nodes.len())
            .collect()
    }

    pub fn put(&mut self, key: String, value: String) {
        let indices = self.get_replica_indices(&key);
        for idx in indices {
            let node = &self.nodes[idx];
            if node.is_active() {
                let mut data = node.data.lock().unwrap();
                data.insert(key.clone(), value.clone());
            }
        }
    }

    pub fn get(&self, key: String) -> Option<String> {
        let indices = self.get_replica_indices(&key);
        for idx in indices {
            let node = &self.nodes[idx];
            if node.is_active() {
                let data = node.data.lock().unwrap();
                if let Some(val) = data.get(&key) {
                    return Some(val.clone());
                }
            }
        }
        None
    }

    pub fn range_query(&self, start_key: String, end_key: String) -> Vec<(String, String)> {
        let mut handles = vec![];
        for node in &self.nodes {
            let node_clone = Arc::clone(node);
            let start = start_key.clone();
            let end = end_key.clone();
            let handle = thread::spawn(move || -> HashMap<String, String> {
                let mut local_map = HashMap::new();
                if node_clone.is_active() {
                    let data = node_clone.data.lock().unwrap();
                    // Retrieve keys in the inclusive range [start, end]
                    for (k, v) in data.range(start.clone()..=end.clone()) {
                        local_map.insert(k.clone(), v.clone());
                    }
                }
                local_map
            });
            handles.push(handle);
        }

        let mut merged: HashMap<String, String> = HashMap::new();
        for handle in handles {
            let partial = handle.join().unwrap();
            for (k, v) in partial.into_iter() {
                merged.insert(k, v);
            }
        }
        let mut result: Vec<(String, String)> = merged.into_iter().collect();
        result.sort_by(|a, b| a.0.cmp(&b.0));
        result
    }

    pub fn simulate_node_failure(&mut self, node_id: usize) {
        if let Some(node) = self.nodes.get(node_id) {
            let mut active = node.active.lock().unwrap();
            *active = false;
        }
    }
}