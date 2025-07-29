use std::collections::HashMap;
use std::collections::hash_map::DefaultHasher;
use std::fs::{OpenOptions, create_dir_all};
use std::hash::{Hash, Hasher};
use std::io::{BufReader, BufRead, Write};
use std::sync::{Arc, Mutex};
use std::time::{SystemTime, UNIX_EPOCH};

pub struct Node {
    index: usize,
    store: Mutex<HashMap<String, (String, u64)>>,
    log_path: String,
}

impl Node {
    pub fn new(index: usize, storage_path: &str) -> Self {
        let log_path = format!("{}/node_{}.log", storage_path, index);
        // Ensure log file exists
        let _ = OpenOptions::new().create(true).append(true).open(&log_path);
        let node = Node {
            index,
            store: Mutex::new(HashMap::new()),
            log_path,
        };
        node.recover();
        node
    }
    
    fn recover(&self) {
        let file = OpenOptions::new().read(true).open(&self.log_path);
        if let Ok(file) = file {
            let reader = BufReader::new(file);
            let mut store = self.store.lock().unwrap();
            for line in reader.lines() {
                if let Ok(line) = line {
                    let parts: Vec<&str> = line.split('|').collect();
                    if parts.len() >= 3 {
                        let op = parts[0];
                        let key = parts[1].to_string();
                        if op == "PUT" && parts.len() == 4 {
                            let value = parts[2].to_string();
                            let ts: u64 = parts[3].parse().unwrap_or(0);
                            store.insert(key, (value, ts));
                        } else if op == "DEL" && parts.len() == 3 {
                            store.remove(&key);
                        }
                    }
                }
            }
        }
    }
    
    fn append_log(&self, entry: &str) {
        if let Ok(mut file) = OpenOptions::new().create(true).append(true).open(&self.log_path) {
            let _ = writeln!(file, "{}", entry);
        }
    }
    
    pub fn put(&self, key: String, value: String, timestamp: u64) {
        {
            let mut store = self.store.lock().unwrap();
            store.insert(key.clone(), (value.clone(), timestamp));
        }
        let entry = format!("PUT|{}|{}|{}", key, value, timestamp);
        self.append_log(&entry);
    }
    
    pub fn get(&self, key: &String) -> Option<(String, u64)> {
        let store = self.store.lock().unwrap();
        store.get(key).cloned()
    }
    
    pub fn delete(&self, key: &String, timestamp: u64) {
        {
            let mut store = self.store.lock().unwrap();
            store.remove(key);
        }
        let entry = format!("DEL|{}|{}", key, timestamp);
        self.append_log(&entry);
    }
}

pub struct KVStore {
    nodes: Vec<Arc<Node>>,
    replication: usize,
    node_count: usize,
}

impl KVStore {
    pub fn new(node_count: usize, replication: usize, storage_path: &str) -> Result<Self, String> {
        if replication > node_count {
            return Err("Replication factor cannot be greater than node count".to_string());
        }
        create_dir_all(storage_path).map_err(|e| e.to_string())?;
        let mut nodes = Vec::with_capacity(node_count);
        for i in 0..node_count {
            nodes.push(Arc::new(Node::new(i, storage_path)));
        }
        Ok(KVStore { nodes, replication, node_count })
    }
    
    fn get_replica_nodes(&self, key: &String) -> Vec<Arc<Node>> {
        let mut hasher = DefaultHasher::new();
        key.hash(&mut hasher);
        let primary = (hasher.finish() as usize) % self.node_count;
        let mut replicas = Vec::new();
        for i in 0..self.replication {
            let index = (primary + i) % self.node_count;
            replicas.push(Arc::clone(&self.nodes[index]));
        }
        replicas
    }
    
    fn current_timestamp() -> u64 {
        let start = SystemTime::now();
        let since_epoch = start.duration_since(UNIX_EPOCH).unwrap();
        since_epoch.as_millis() as u64
    }
    
    pub fn put(&self, key: String, value: String) {
        let timestamp = Self::current_timestamp();
        let replicas = self.get_replica_nodes(&key);
        for node in replicas {
            node.put(key.clone(), value.clone(), timestamp);
        }
    }
    
    pub fn get(&self, key: String) -> Option<String> {
        let replicas = self.get_replica_nodes(&key);
        let mut best: Option<(String, u64)> = None;
        for node in replicas.iter() {
            if let Some((value, ts)) = node.get(&key) {
                if best.is_none() || ts > best.as_ref().unwrap().1 {
                    best = Some((value, ts));
                }
            }
        }
        if let Some((ref best_value, best_ts)) = best {
            for node in replicas {
                if let Some((val, ts)) = node.get(&key) {
                    if ts < best_ts {
                        node.put(key.clone(), best_value.clone(), best_ts);
                    }
                } else {
                    node.put(key.clone(), best_value.clone(), best_ts);
                }
            }
            Some(best_value.clone())
        } else {
            None
        }
    }
    
    pub fn delete(&self, key: String) {
        let timestamp = Self::current_timestamp();
        let replicas = self.get_replica_nodes(&key);
        for node in replicas {
            node.delete(&key, timestamp);
        }
    }
}