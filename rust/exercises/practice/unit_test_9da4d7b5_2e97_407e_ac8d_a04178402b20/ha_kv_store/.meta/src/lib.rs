use std::collections::HashMap;

#[derive(Debug, PartialEq)]
pub enum KVError {
    ReplicationFailure,
    NodeUnavailable,
    KeyNotFound,
}

pub type KVResult<T> = Result<T, KVError>;

#[derive(Clone)]
struct Node {
    store: HashMap<String, (String, u64)>,
    clock: u64,
    available: bool,
}

impl Node {
    fn new() -> Self {
        Node {
            store: HashMap::new(),
            clock: 0,
            available: true,
        }
    }

    fn update_clock(&mut self) -> u64 {
        self.clock += 1;
        self.clock
    }

    fn set_available(&mut self, avail: bool) {
        self.available = avail;
    }

    fn insert(&mut self, key: &str, value: &str) -> u64 {
        let ts = self.update_clock();
        self.store.insert(key.to_string(), (value.to_string(), ts));
        ts
    }

    fn force_insert(&mut self, key: &str, value: &str, ts: u64) {
        if ts > self.clock {
            self.clock = ts;
        }
        self.store.insert(key.to_string(), (value.to_string(), ts));
    }

    fn delete(&mut self, key: &str) {
        self.store.remove(key);
        self.update_clock();
    }

    fn get(&self, key: &str) -> Option<(String, u64)> {
        self.store.get(key).cloned()
    }
}

pub struct Cluster {
    nodes: Vec<Node>,
    majority: usize,
}

impl Cluster {
    pub fn new(num_nodes: usize) -> Self {
        let majority = num_nodes / 2 + 1;
        let nodes = (0..num_nodes).map(|_| Node::new()).collect();
        Cluster { nodes, majority }
    }

    pub fn insert(&mut self, key: &str, value: &str) -> KVResult<()> {
        let mut count = 0;
        for node in self.nodes.iter_mut() {
            if node.available {
                node.insert(key, value);
                count += 1;
            }
        }
        if count < self.majority {
            return Err(KVError::ReplicationFailure);
        }
        self.sync_conflicts(key);
        Ok(())
    }

    pub fn force_insert(&mut self, node_index: usize, key: &str, value: &str, ts: u64) -> KVResult<()> {
        if node_index >= self.nodes.len() {
            return Err(KVError::NodeUnavailable);
        }
        if !self.nodes[node_index].available {
            return Err(KVError::NodeUnavailable);
        }
        self.nodes[node_index].force_insert(key, value, ts);
        self.sync_conflicts(key);
        Ok(())
    }

    pub fn delete(&mut self, key: &str) -> KVResult<()> {
        let mut count = 0;
        for node in self.nodes.iter_mut() {
            if node.available {
                node.delete(key);
                count += 1;
            }
        }
        if count < self.majority {
            return Err(KVError::ReplicationFailure);
        }
        Ok(())
    }

    pub fn get(&self, key: &str) -> KVResult<String> {
        let mut candidate: Option<(String, u64)> = None;
        let mut count = 0;
        for node in self.nodes.iter() {
            if node.available {
                count += 1;
                if let Some((val, ts)) = node.get(key) {
                    candidate = match candidate {
                        None => Some((val, ts)),
                        Some((cval, cts)) => {
                            if ts > cts {
                                Some((val, ts))
                            } else if ts == cts {
                                if val < cval { Some((val, ts)) } else { Some((cval, cts)) }
                            } else {
                                Some((cval, cts))
                            }
                        }
                    }
                }
            }
        }
        if count < self.majority {
            return Err(KVError::ReplicationFailure);
        }
        candidate.map(|(v, _)| v).ok_or(KVError::KeyNotFound)
    }

    pub fn fail_node(&mut self, index: usize) {
        if index < self.nodes.len() {
            self.nodes[index].set_available(false);
        }
    }

    pub fn recover_node(&mut self, index: usize) {
        if index < self.nodes.len() {
            self.nodes[index].set_available(true);
            self.sync_node(index);
        }
    }

    fn sync_node(&mut self, index: usize) {
        let mut consensus: HashMap<String, (String, u64)> = HashMap::new();
        for node in self.nodes.iter() {
            if node.available {
                for (k, v) in &node.store {
                    consensus.entry(k.clone()).and_modify(|existing| {
                        if v.1 > existing.1 {
                            *existing = v.clone();
                        } else if v.1 == existing.1 && v.0 < existing.0 {
                            *existing = v.clone();
                        }
                    }).or_insert(v.clone());
                }
            }
        }
        self.nodes[index].store = consensus;
    }

    fn sync_conflicts(&mut self, key: &str) {
        let mut candidate: Option<(String, u64)> = None;
        for node in self.nodes.iter() {
            if node.available {
                if let Some((val, ts)) = node.get(key) {
                    candidate = match candidate {
                        None => Some((val, ts)),
                        Some((cval, cts)) => {
                            if ts > cts {
                                Some((val, ts))
                            } else if ts == cts {
                                if val < cval { Some((val, ts)) } else { Some((cval, cts)) }
                            } else {
                                Some((cval, cts))
                            }
                        }
                    }
                }
            }
        }
        if let Some(ref consensus) = candidate {
            for node in self.nodes.iter_mut() {
                if node.available {
                    node.store.insert(key.to_string(), consensus.clone());
                }
            }
        }
    }
}