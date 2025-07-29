use std::collections::{BTreeMap, HashMap};
use std::sync::RwLock;

pub struct ConsistentHashing {
    inner: RwLock<Inner>,
}

struct Inner {
    replicas: u32,
    ring: BTreeMap<u32, String>, // Maps virtual node hash to physical node id.
    nodes: HashMap<String, Vec<u32>>, // Maps physical node id to its virtual node hashes.
}

#[derive(Debug)]
pub enum ConsistentHashError {
    NodeAlreadyExists,
    NodeNotFound,
    EmptyRing,
}

impl std::fmt::Display for ConsistentHashError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ConsistentHashError::NodeAlreadyExists => write!(f, "Node already exists"),
            ConsistentHashError::NodeNotFound => write!(f, "Node not found"),
            ConsistentHashError::EmptyRing => write!(f, "Hash ring is empty"),
        }
    }
}

impl std::error::Error for ConsistentHashError {}

impl ConsistentHashing {
    pub fn new(replicas: u32) -> Self {
        ConsistentHashing {
            inner: RwLock::new(Inner {
                replicas,
                ring: BTreeMap::new(),
                nodes: HashMap::new(),
            }),
        }
    }

    pub fn add_node(&self, node_id: String) -> Result<(), ConsistentHashError> {
        let mut inner = self.inner.write().unwrap();
        if inner.nodes.contains_key(&node_id) {
            return Err(ConsistentHashError::NodeAlreadyExists);
        }
        let mut vnode_hashes = Vec::new();
        for i in 0..inner.replicas {
            let vnode_id = format!("{}:{}", node_id, i);
            let h = hash_str(&vnode_id);
            inner.ring.insert(h, node_id.clone());
            vnode_hashes.push(h);
        }
        inner.nodes.insert(node_id, vnode_hashes);
        Ok(())
    }

    pub fn remove_node(&self, node_id: &str) -> Result<(), ConsistentHashError> {
        let mut inner = self.inner.write().unwrap();
        if let Some(vnode_hashes) = inner.nodes.remove(node_id) {
            for h in vnode_hashes {
                inner.ring.remove(&h);
            }
            Ok(())
        } else {
            Err(ConsistentHashError::NodeNotFound)
        }
    }

    pub fn get_node(&self, key: &str) -> Result<String, ConsistentHashError> {
        let inner = self.inner.read().unwrap();
        if inner.ring.is_empty() {
            return Err(ConsistentHashError::EmptyRing);
        }
        let key_hash = hash_str(key);
        let mut iter = inner.ring.range(key_hash..);
        if let Some((_hash, node_id)) = iter.next() {
            return Ok(node_id.clone());
        }
        if let Some((_hash, node_id)) = inner.ring.iter().next() {
            return Ok(node_id.clone());
        }
        Err(ConsistentHashError::EmptyRing)
    }

    pub fn rebalance(&self) {
        // In this simulation rebalance is a no-op.
        // The consistent hashing ring remains updated after add/remove.
    }
}

// Implementation of a simple FNV-1a 32-bit hash function
fn hash_str(s: &str) -> u32 {
    let mut hash: u32 = 0x811c9dc5;
    for byte in s.as_bytes() {
        hash ^= *byte as u32;
        hash = hash.wrapping_mul(0x01000193);
    }
    hash
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add_and_get_node() {
        let ch = ConsistentHashing::new(3);
        let res = ch.add_node("node1".to_string());
        assert!(res.is_ok(), "Adding a new node should succeed");
        let node = ch.get_node("my_key");
        assert!(node.is_ok(), "get_node should succeed");
        assert_eq!(node.unwrap(), "node1", "The only node available should be node1");
    }

    #[test]
    fn test_duplicate_node() {
        let ch = ConsistentHashing::new(3);
        let res1 = ch.add_node("node1".to_string());
        assert!(res1.is_ok(), "Adding node1 the first time should succeed");
        let res2 = ch.add_node("node1".to_string());
        assert!(res2.is_err(), "Adding duplicate node1 should return an error");
    }

    #[test]
    fn test_remove_node() {
        let ch = ConsistentHashing::new(3);
        let _ = ch.add_node("node1".to_string());
        let _ = ch.add_node("node2".to_string());
        let key = "test_key";
        let node_before = ch.get_node(key).unwrap();
        assert!(node_before == "node1" || node_before == "node2", "get_node must return one of the added nodes");
        let remove_res = ch.remove_node("node1");
        assert!(remove_res.is_ok(), "Removing an existing node should succeed");
        let node_after = ch.get_node(key).unwrap();
        assert_ne!(node_after, "node1", "After removal, get_node should not return the removed node");
    }

    #[test]
    fn test_rebalance_effect() {
        let ch = ConsistentHashing::new(5);
        let _ = ch.add_node("node1".to_string());
        let _ = ch.add_node("node2".to_string());
        let _ = ch.add_node("node3".to_string());
        let key = "balance_test_key";
        let node_before = ch.get_node(key).unwrap();
        let _ = ch.remove_node(&node_before);
        ch.rebalance();
        let node_after = ch.get_node(key).unwrap();
        assert_ne!(node_before, node_after, "After removal and rebalance, the responsible node must change");
    }

    #[test]
    fn test_empty_ring() {
        let ch = ConsistentHashing::new(3);
        let result = ch.get_node("any_key");
        assert!(result.is_err(), "Getting node from an empty ring should return an error");
    }

    #[test]
    fn test_thread_safety() {
        use std::sync::{Arc};
        use std::thread;
        let ch = Arc::new(ConsistentHashing::new(3));
        {
            let _ = ch.add_node("node1".to_string());
            let _ = ch.add_node("node2".to_string());
            let _ = ch.add_node("node3".to_string());
        }
        let mut handles = vec![];
        for i in 0..10 {
            let ch_clone = Arc::clone(&ch);
            let key = format!("key_{}", i);
            let handle = thread::spawn(move || {
                let node = ch_clone.get_node(&key);
                assert!(node.is_ok(), "get_node should succeed in thread");
                node.unwrap()
            });
            handles.push(handle);
        }
        for handle in handles {
            let _ = handle.join().unwrap();
        }
    }
}