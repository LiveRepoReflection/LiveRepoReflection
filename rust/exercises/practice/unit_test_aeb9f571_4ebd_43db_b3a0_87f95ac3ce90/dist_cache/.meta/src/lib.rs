use std::{
    collections::HashMap,
    sync::{Arc, Mutex},
    thread,
    time::{Duration, SystemTime, UNIX_EPOCH},
};

pub struct DistributedCache {
    nodes: Vec<Arc<Node>>,
    replication_factor: usize,
}

struct CacheEntry {
    value: String,
    timestamp: u128,
}

pub struct Node {
    capacity: usize,
    store: Mutex<HashMap<String, CacheEntry>>,
    lru: Mutex<Vec<String>>,
    failed: Mutex<bool>,
}

impl Node {
    pub fn new(capacity: usize) -> Self {
        Node {
            capacity,
            store: Mutex::new(HashMap::new()),
            lru: Mutex::new(Vec::new()),
            failed: Mutex::new(false),
        }
    }

    pub fn is_failed(&self) -> bool {
        let f = self.failed.lock().unwrap();
        *f
    }

    pub fn set_failed(&self, val: bool) {
        let mut f = self.failed.lock().unwrap();
        *f = val;
    }

    pub fn put(&self, key: String, value: String, timestamp: u128) {
        let mut store = self.store.lock().unwrap();
        let mut lru = self.lru.lock().unwrap();

        if let Some(entry) = store.get(&key) {
            if timestamp < entry.timestamp {
                // Do not update if the new timestamp is older.
                return;
            }
        }

        store.insert(key.clone(), CacheEntry { value, timestamp });

        // Update LRU: remove the key if it exists, then push it to the back.
        if let Some(pos) = lru.iter().position(|k| k == &key) {
            lru.remove(pos);
        }
        lru.push(key.clone());

        // Evict least recently used item if capacity exceeded.
        if store.len() > self.capacity {
            if let Some(evict_key) = lru.first().cloned() {
                store.remove(&evict_key);
                lru.remove(0);
            }
        }
    }

    pub fn get(&self, key: &str) -> Option<String> {
        let mut store = self.store.lock().unwrap();
        let mut lru = self.lru.lock().unwrap();

        if let Some(entry) = store.get(key) {
            // Update LRU order: move accessed key to the back.
            if let Some(pos) = lru.iter().position(|k| k == key) {
                lru.remove(pos);
                lru.push(key.to_string());
            }
            return Some(entry.value.clone());
        }
        None
    }
}

impl DistributedCache {
    pub fn new(num_nodes: usize, capacity: usize, replication_factor: usize) -> Self {
        let mut nodes = Vec::with_capacity(num_nodes);
        for _ in 0..num_nodes {
            nodes.push(Arc::new(Node::new(capacity)));
        }
        DistributedCache {
            nodes,
            replication_factor,
        }
    }

    fn get_node_for_key(&self, key: &str) -> usize {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        let mut hasher = DefaultHasher::new();
        key.hash(&mut hasher);
        (hasher.finish() as usize) % self.nodes.len()
    }

    pub fn put(&self, key: String, value: String) {
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or(Duration::from_millis(0))
            .as_millis();
        let primary_index = self.get_node_for_key(&key);
        let primary_node = self.nodes[primary_index].clone();

        if !primary_node.is_failed() {
            primary_node.put(key.clone(), value.clone(), timestamp);
        }

        let total_nodes = self.nodes.len();
        let mut replicated = 0;
        let mut next_index = (primary_index + 1) % total_nodes;
        // Deterministic replication: iterate over nodes in order.
        while replicated < self.replication_factor && next_index != primary_index {
            let node = self.nodes[next_index].clone();
            let rep_key = key.clone();
            let rep_value = value.clone();
            let rep_timestamp = timestamp;
            thread::spawn(move || {
                if !node.is_failed() {
                    node.put(rep_key, rep_value, rep_timestamp);
                }
            });
            replicated += 1;
            next_index = (next_index + 1) % total_nodes;
        }
    }

    pub fn get(&self, key: &str) -> Option<String> {
        let primary_index = self.get_node_for_key(key);
        let primary_node = self.nodes[primary_index].clone();
        if primary_node.is_failed() {
            return None;
        }
        primary_node.get(key)
    }

    pub fn fail_node(&self, node_id: usize) {
        if node_id < self.nodes.len() {
            self.nodes[node_id].set_failed(true);
        }
    }

    pub fn recover_node(&self, node_id: usize) {
        if node_id < self.nodes.len() {
            self.nodes[node_id].set_failed(false);
        }
    }
}