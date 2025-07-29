use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

pub struct Node {
    pub id: usize,
    pub storage: Mutex<HashMap<Vec<u8>, (Vec<u8>, u64)>>, // (value, timestamp)
    pub last_heartbeat: Mutex<SystemTime>,
    pub failed: Mutex<bool>,
}

impl Node {
    pub fn new(id: usize) -> Self {
        Node {
            id,
            storage: Mutex::new(HashMap::new()),
            last_heartbeat: Mutex::new(SystemTime::now()),
            failed: Mutex::new(false),
        }
    }

    pub fn is_failed(&self) -> bool {
        *self.failed.lock().unwrap()
    }
}

pub struct Cluster {
    pub nodes: Vec<Arc<Node>>,
    pub replication_factor: usize,
    pub gossip_interval: Duration,
    pub failure_threshold: u32,
}

impl Cluster {
    pub fn new(num_nodes: usize, replication_factor: usize, gossip_interval: Duration, failure_threshold: u32) -> Self {
        let nodes = (0..num_nodes).map(|i| Arc::new(Node::new(i))).collect();
        let cluster = Cluster {
            nodes,
            replication_factor,
            gossip_interval,
            failure_threshold,
        };
        cluster.start_gossip();
        cluster
    }

    fn start_gossip(&self) {
        let nodes = self.nodes.clone();
        let gossip_interval = self.gossip_interval;
        let failure_threshold = self.failure_threshold;
        thread::spawn(move || loop {
            thread::sleep(gossip_interval);
            let now = SystemTime::now();
            // Simulate heartbeat update for each node that is not failed.
            for node in nodes.iter() {
                if node.is_failed() {
                    continue;
                }
                let mut hb = node.last_heartbeat.lock().unwrap();
                *hb = now;
            }
            // Check for nodes that missed heartbeats.
            for node in nodes.iter() {
                if node.is_failed() {
                    continue;
                }
                let hb = node.last_heartbeat.lock().unwrap();
                if now.duration_since(*hb).unwrap_or(Duration::from_secs(0)) > gossip_interval * failure_threshold {
                    let mut failed = node.failed.lock().unwrap();
                    *failed = true;
                }
            }
        });
    }

    pub fn write(&self, key: &[u8], value: &[u8]) -> Result<(), String> {
        // Choose a leader node (first non-failed node)
        let mut leader_opt = None;
        for node in &self.nodes {
            if !node.is_failed() {
                leader_opt = Some(node.clone());
                break;
            }
        }
        let leader = leader_opt.ok_or("No available nodes for write")?;
        // Timestamp is generated using current system time in nanoseconds.
        let timestamp = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos() as u64;
        {
            let mut storage = leader.storage.lock().unwrap();
            storage.insert(key.to_vec(), (value.to_vec(), timestamp));
        }
        // Replicate to other nodes asynchronously.
        let mut replicas_needed = if self.replication_factor > 0 { self.replication_factor - 1 } else { 0 };
        for node in &self.nodes {
            if Arc::ptr_eq(node, &leader) || node.is_failed() {
                continue;
            }
            if replicas_needed == 0 {
                break;
            }
            let key_vec = key.to_vec();
            let value_vec = value.to_vec();
            let node_clone = node.clone();
            thread::spawn(move || {
                let rep_timestamp = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos() as u64;
                let mut storage = node_clone.storage.lock().unwrap();
                // Insert if key not present or update if timestamp is more recent.
                if let Some((existing_val, existing_ts)) = storage.get(&key_vec) {
                    if rep_timestamp > *existing_ts {
                        storage.insert(key_vec, (value_vec, rep_timestamp));
                    }
                } else {
                    storage.insert(key_vec, (value_vec, rep_timestamp));
                }
            });
            replicas_needed -= 1;
        }
        Ok(())
    }

    pub fn read(&self, key: &[u8]) -> Option<Vec<u8>> {
        // Read from first non-failed node that has the key.
        let mut candidate = None;
        for node in &self.nodes {
            if node.is_failed() {
                continue;
            }
            let storage = node.storage.lock().unwrap();
            if let Some((val, ts)) = storage.get(key) {
                candidate = Some((val.clone(), *ts));
                break;
            }
        }
        if candidate.is_none() {
            return None;
        }
        let (mut best_val, mut best_ts) = candidate.unwrap();
        // Find the most recent value across all nodes.
        for node in &self.nodes {
            if node.is_failed() {
                continue;
            }
            let storage = node.storage.lock().unwrap();
            if let Some((val, ts)) = storage.get(key) {
                if *ts > best_ts {
                    best_ts = *ts;
                    best_val = val.clone();
                }
            }
        }
        // Read repair: update nodes with stale data.
        for node in &self.nodes {
            if node.is_failed() {
                continue;
            }
            let mut storage = node.storage.lock().unwrap();
            if let Some((_, ts)) = storage.get(key) {
                if *ts < best_ts {
                    storage.insert(key.to_vec(), (best_val.clone(), best_ts));
                }
            }
        }
        Some(best_val)
    }

    pub fn simulate_failure(&self, node_id: usize) -> Result<(), String> {
        for node in &self.nodes {
            if node.id == node_id {
                let mut failed = node.failed.lock().unwrap();
                *failed = true;
                return Ok(());
            }
        }
        Err("Node id not found".to_string())
    }

    pub fn failed_nodes(&self) -> Vec<usize> {
        let mut failed = vec![];
        for node in &self.nodes {
            if node.is_failed() {
                failed.push(node.id);
            }
        }
        failed
    }

    pub fn force_update_node(&self, node_id: usize, key: &[u8], value: &[u8]) -> Result<(), String> {
        for node in &self.nodes {
            if node.id == node_id {
                let mut storage = node.storage.lock().unwrap();
                // Use a fixed, low timestamp to simulate stale data.
                storage.insert(key.to_vec(), (value.to_vec(), 0));
                return Ok(());
            }
        }
        Err("Node id not found".to_string())
    }
}

impl Clone for Cluster {
    fn clone(&self) -> Self {
        Cluster {
            nodes: self.nodes.clone(),
            replication_factor: self.replication_factor,
            gossip_interval: self.gossip_interval,
            failure_threshold: self.failure_threshold,
        }
    }
}