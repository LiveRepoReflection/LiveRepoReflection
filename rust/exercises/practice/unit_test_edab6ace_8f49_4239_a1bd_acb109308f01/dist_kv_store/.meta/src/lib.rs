use std::collections::HashMap;
use std::sync::{Arc, Mutex};

pub struct DistKVStore {
    inner: Arc<DistKVStoreInner>,
}

struct DistKVStoreInner {
    nodes: Vec<Arc<Node>>,
    global_lock: Mutex<()>,
}

struct Node {
    id: usize,
    active: Mutex<bool>,
    storage: Mutex<HashMap<String, String>>,
}

impl Node {
    fn new(id: usize) -> Self {
        Self {
            id,
            active: Mutex::new(true),
            storage: Mutex::new(HashMap::new()),
        }
    }
}

impl DistKVStore {
    pub fn new(node_count: usize) -> Self {
        let mut nodes = Vec::new();
        for i in 0..node_count {
            nodes.push(Arc::new(Node::new(i)));
        }
        Self {
            inner: Arc::new(DistKVStoreInner {
                nodes,
                global_lock: Mutex::new(()),
            }),
        }
    }

    pub async fn put(&self, key: String, value: String) -> Result<(), String> {
        let mut updated = false;
        for node in &self.inner.nodes {
            let active = *node.active.lock().map_err(|_| "Lock poisoned".to_string())?;
            if active {
                let mut storage = node.storage.lock().map_err(|_| "Lock poisoned".to_string())?;
                storage.insert(key.clone(), value.clone());
                updated = true;
            }
        }
        if updated {
            Ok(())
        } else {
            Err("No active nodes available".to_string())
        }
    }

    pub async fn get(&self, key: String) -> Result<Option<String>, String> {
        for node in &self.inner.nodes {
            let active = *node.active.lock().map_err(|_| "Lock poisoned".to_string())?;
            if active {
                let storage = node.storage.lock().map_err(|_| "Lock poisoned".to_string())?;
                if let Some(val) = storage.get(&key) {
                    return Ok(Some(val.clone()));
                }
            }
        }
        Ok(None)
    }

    pub async fn delete(&self, key: String) -> Result<bool, String> {
        let mut deleted = false;
        for node in &self.inner.nodes {
            let active = *node.active.lock().map_err(|_| "Lock poisoned".to_string())?;
            if active {
                let mut storage = node.storage.lock().map_err(|_| "Lock poisoned".to_string())?;
                if storage.remove(&key).is_some() {
                    deleted = true;
                }
            }
        }
        Ok(deleted)
    }

    pub async fn begin_transaction(&self) -> Result<Transaction, String> {
        Ok(Transaction {
            inner: Arc::clone(&self.inner),
            ops: Mutex::new(Vec::new()),
        })
    }

    pub async fn simulate_failure(&self, node_index: usize) -> Result<(), String> {
        if node_index >= self.inner.nodes.len() {
            return Err("Invalid node index".to_string());
        }
        let node = &self.inner.nodes[node_index];
        let mut active = node.active.lock().map_err(|_| "Lock poisoned".to_string())?;
        *active = false;
        Ok(())
    }
}

pub struct Transaction {
    inner: Arc<DistKVStoreInner>,
    ops: Mutex<Vec<TxOperation>>,
}

enum TxOperation {
    Put(String, String),
    Delete(String),
}

impl Transaction {
    pub async fn put(&self, key: String, value: String) -> Result<(), String> {
        let mut ops = self.ops.lock().map_err(|_| "Lock poisoned".to_string())?;
        ops.push(TxOperation::Put(key, value));
        Ok(())
    }

    pub async fn get(&self, key: String) -> Result<Option<String>, String> {
        {
            let ops = self.ops.lock().map_err(|_| "Lock poisoned".to_string())?;
            for op in ops.iter().rev() {
                match op {
                    TxOperation::Put(k, v) if *k == key => return Ok(Some(v.clone())),
                    TxOperation::Delete(k) if *k == key => return Ok(None),
                    _ => {}
                }
            }
        }
        for node in &self.inner.nodes {
            let active = *node.active.lock().map_err(|_| "Lock poisoned".to_string())?;
            if active {
                let storage = node.storage.lock().map_err(|_| "Lock poisoned".to_string())?;
                if let Some(val) = storage.get(&key) {
                    return Ok(Some(val.clone()));
                }
            }
        }
        Ok(None)
    }

    pub async fn delete(&self, key: String) -> Result<bool, String> {
        let mut ops = self.ops.lock().map_err(|_| "Lock poisoned".to_string())?;
        ops.push(TxOperation::Delete(key));
        Ok(true)
    }

    pub async fn commit(self) -> Result<(), String> {
        let _guard = self.inner.global_lock.lock().map_err(|_| "Lock poisoned".to_string())?;
        let ops = self.ops.into_inner().map_err(|_| "Lock poisoned".to_string())?;
        for op in ops {
            match op {
                TxOperation::Put(key, value) => {
                    for node in &self.inner.nodes {
                        let active = *node.active.lock().map_err(|_| "Lock poisoned".to_string())?;
                        if active {
                            let mut storage = node.storage.lock().map_err(|_| "Lock poisoned".to_string())?;
                            storage.insert(key.clone(), value.clone());
                        }
                    }
                }
                TxOperation::Delete(key) => {
                    for node in &self.inner.nodes {
                        let active = *node.active.lock().map_err(|_| "Lock poisoned".to_string())?;
                        if active {
                            let mut storage = node.storage.lock().map_err(|_| "Lock poisoned".to_string())?;
                            storage.remove(&key);
                        }
                    }
                }
            }
        }
        Ok(())
    }

    pub async fn rollback(self) -> Result<(), String> {
        Ok(())
    }
}