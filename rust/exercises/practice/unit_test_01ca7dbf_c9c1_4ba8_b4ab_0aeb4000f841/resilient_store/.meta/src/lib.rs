use std::collections::HashMap;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};

pub struct Store {
    nodes: Vec<Arc<Node>>,
    replication_factor: usize,
}

struct Node {
    data: Mutex<HashMap<String, (Option<String>, u64)>>,
    failed: AtomicBool,
}

impl Node {
    fn new() -> Self {
        Node {
            data: Mutex::new(HashMap::new()),
            failed: AtomicBool::new(false),
        }
    }

    // Attempts to update the key with given value and timestamp.
    // Returns true if the update was applied, false otherwise.
    fn update(&self, key: String, value: Option<String>, timestamp: u64) -> bool {
        // If the node is failed, reject the operation.
        if self.failed.load(Ordering::SeqCst) {
            return false;
        }
        let mut lock = self.data.lock().unwrap();
        let current = lock.get(&key);
        let current_ts = current.map(|&(_, ts)| ts).unwrap_or(0);
        if timestamp > current_ts {
            lock.insert(key, (value, timestamp));
            return true;
        }
        false
    }

    // Retrieves the value for a key, along with its timestamp.
    fn get(&self, key: &String) -> Option<(Option<String>, u64)> {
        if self.failed.load(Ordering::SeqCst) {
            return None;
        }
        let lock = self.data.lock().unwrap();
        lock.get(key).cloned()
    }

    // Overwrite the node data completely with new data.
    fn overwrite_data(&self, new_data: HashMap<String, (Option<String>, u64)>) {
        let mut lock = self.data.lock().unwrap();
        *lock = new_data;
    }
}

impl Store {
    pub fn new(total_nodes: usize, replication_factor: usize) -> Self {
        let mut nodes = Vec::with_capacity(total_nodes);
        for _ in 0..total_nodes {
            nodes.push(Arc::new(Node::new()));
        }
        Store {
            nodes,
            replication_factor,
        }
    }

    // Majority threshold: (replication_factor + 1) / 2
    fn majority(&self) -> usize {
        (self.replication_factor + 1) / 2
    }

    pub fn put(&self, key: String, value: String, timestamp: u64) -> bool {
        let mut success_count = 0;
        // In a real system, only a subset of nodes based on replication strategy
        // would get updated. Here, we simulate by writing to all nodes.
        for node in &self.nodes {
            if node.update(key.clone(), Some(value.clone()), timestamp) {
                success_count += 1;
            }
        }
        success_count >= self.majority()
    }

    pub fn get(&self, key: String) -> Option<String> {
        let mut best: Option<(Option<String>, u64)> = None;
        for node in &self.nodes {
            if let Some((val, ts)) = node.get(&key) {
                match best {
                    None => best = Some((val, ts)),
                    Some((_, best_ts)) if ts > best_ts => best = Some((val, ts)),
                    _ => {}
                }
            }
        }
        // If the best value is a tombstone (None) or not present, return None.
        best.and_then(|(val, _)| val)
    }

    pub fn delete(&self, key: String, timestamp: u64) -> bool {
        let mut success_count = 0;
        // Delete is implemented as writing a tombstone (None value).
        for node in &self.nodes {
            if node.update(key.clone(), None, timestamp) {
                success_count += 1;
            }
        }
        success_count >= self.majority()
    }

    // Fail a node at the given index.
    pub fn fail_node(&mut self, index: usize) {
        if let Some(node) = self.nodes.get(index) {
            node.failed.store(true, Ordering::SeqCst);
        }
    }

    // Recover a node at the given index.
    pub fn recover_node(&mut self, index: usize) {
        if let Some(node) = self.nodes.get(index) {
            node.failed.store(false, Ordering::SeqCst);
        }
    }

    // Sync the recovered node with the latest data from majority of active nodes.
    pub fn sync_node(&self, index: usize) {
        if index >= self.nodes.len() {
            return;
        }
        let mut global_data: HashMap<String, (Option<String>, u64)> = HashMap::new();
        // Collect data from all active nodes.
        for node in &self.nodes {
            if node.failed.load(Ordering::SeqCst) {
                continue;
            }
            let lock = node.data.lock().unwrap();
            for (key, &(ref val, ts)) in lock.iter() {
                let entry = global_data.get(key);
                if entry.is_none() || ts > entry.unwrap().1 {
                    global_data.insert(key.clone(), (val.clone(), ts));
                }
            }
        }
        // Overwrite the node's data with the global data.
        if let Some(node) = self.nodes.get(index) {
            node.overwrite_data(global_data);
        }
    }
}