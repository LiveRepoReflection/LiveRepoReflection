use std::collections::HashMap;
use std::hash::{Hash, Hasher};
use std::sync::{Arc, Mutex};
use std::collections::hash_map::DefaultHasher;

/// A Node represents a single node in the cluster with tiered storage.
pub struct Node {
    cache: Mutex<Vec<(String, String)>>,
    persistent: Mutex<HashMap<String, String>>,
    capacity: usize,
}

impl Node {
    /// Create a new node with given cache capacity.
    pub fn new(capacity: usize) -> Self {
        Node {
            cache: Mutex::new(Vec::new()),
            persistent: Mutex::new(HashMap::new()),
            capacity,
        }
    }

    /// Put a key-value pair into both Tier1 (cache) and Tier2 (persistent storage).
    pub fn put(&self, key: String, value: String) {
        {
            // Write-through cache: update persistent storage first.
            let mut persist_lock = self.persistent.lock().unwrap();
            persist_lock.insert(key.clone(), value.clone());
        }
        {
            let mut cache_lock = self.cache.lock().unwrap();
            // Check if key exists in cache and remove it if found.
            if let Some(pos) = cache_lock.iter().position(|(k, _)| k == &key) {
                cache_lock.remove(pos);
            }
            // Insert the key-value pair at the front to mark it as most recently used.
            cache_lock.insert(0, (key, value));
            // Evict least recently used if capacity exceeded.
            if cache_lock.len() > self.capacity {
                cache_lock.pop();
            }
        }
    }

    /// Get value for a given key.
    pub fn get(&self, key: String) -> Option<String> {
        {
            let mut cache_lock = self.cache.lock().unwrap();
            // Search in cache.
            if let Some(pos) = cache_lock.iter().position(|(k, _)| k == &key) {
                // Retrieve the value and update recency: move to front.
                let (_, value) = cache_lock.remove(pos);
                cache_lock.insert(0, (key.clone(), value.clone()));
                return Some(value);
            }
        }
        // If not found in cache, check persistent storage (Tier2).
        let value_opt = {
            let persist_lock = self.persistent.lock().unwrap();
            persist_lock.get(&key).cloned()
        };
        if let Some(v) = value_opt.clone() {
            // Promote to cache.
            let mut cache_lock = self.cache.lock().unwrap();
            if let Some(pos) = cache_lock.iter().position(|(k, _)| k == &key) {
                cache_lock.remove(pos);
            }
            cache_lock.insert(0, (key, v.clone()));
            if cache_lock.len() > self.capacity {
                cache_lock.pop();
            }
        }
        value_opt
    }

    /// Simulate a node restart by clearing the in-memory cache (Tier1) while keeping persistent storage (Tier2) intact.
    pub fn restart(&self) {
        let mut cache_lock = self.cache.lock().unwrap();
        cache_lock.clear();
    }
}

/// A Cluster manages multiple nodes and distributes requests among them.
pub struct Cluster {
    nodes: Vec<Arc<Node>>,
}

impl Cluster {
    /// Create a new cluster with given number of nodes and cache capacity per node.
    pub fn new(num_nodes: usize, cache_size_per_node: usize) -> Self {
        let mut nodes = Vec::with_capacity(num_nodes);
        for _ in 0..num_nodes {
            nodes.push(Arc::new(Node::new(cache_size_per_node)));
        }
        Cluster { nodes }
    }

    /// Hash a key to select a node.
    fn hash_key(&self, key: &str) -> usize {
        let mut hasher = DefaultHasher::new();
        key.hash(&mut hasher);
        (hasher.finish() as usize) % self.nodes.len()
    }

    /// Put a key-value pair into the appropriate node.
    pub fn put(&self, key: String, value: String) {
        let index = self.hash_key(&key);
        self.nodes[index].put(key, value);
    }

    /// Get value for a key from the appropriate node.
    pub fn get(&self, key: String) -> Option<String> {
        let index = self.hash_key(&key);
        self.nodes[index].get(key)
    }

    /// Restart the node at the given index (simulate clearing Tier1 cache).
    pub fn restart_node(&mut self, index: usize) {
        if let Some(node) = self.nodes.get(index) {
            node.restart();
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::Arc;
    use std::thread;

    #[test]
    fn test_put_get_single_node() {
        let cluster = Cluster::new(1, 3);
        cluster.put("key1".to_string(), "value1".to_string());
        let result = cluster.get("key1".to_string());
        assert_eq!(result, Some("value1".to_string()));
    }

    #[test]
    fn test_non_existing_key() {
        let cluster = Cluster::new(2, 2);
        assert_eq!(cluster.get("nonexistent".to_string()), None);
    }

    #[test]
    fn test_cache_eviction() {
        // Create a cluster with one node and a small cache to force eviction.
        let cluster = Cluster::new(1, 2);
        // Insert two keys to fill the cache.
        cluster.put("key1".to_string(), "value1".to_string());
        cluster.put("key2".to_string(), "value2".to_string());
        // Access key1 to mark it as recently used.
        assert_eq!(cluster.get("key1".to_string()), Some("value1".to_string()));
        // Inserting a new key should evict the least recently used key from Tier1.
        cluster.put("key3".to_string(), "value3".to_string());
        // key2 should be evicted from the in-memory cache.
        // However, it should still be retrievable from Tier2 (disk), and then promoted to the cache.
        let value = cluster.get("key2".to_string());
        assert_eq!(value, Some("value2".to_string()));
    }

    #[test]
    fn test_multiple_nodes_distribution() {
        // Create a cluster with three nodes.
        let cluster = Cluster::new(3, 2);
        cluster.put("a".to_string(), "alpha".to_string());
        cluster.put("b".to_string(), "beta".to_string());
        cluster.put("c".to_string(), "gamma".to_string());
        cluster.put("d".to_string(), "delta".to_string());

        let keys = vec!["a", "b", "c", "d"];
        let values = vec!["alpha", "beta", "gamma", "delta"];

        for (k, v) in keys.iter().zip(values.iter()) {
            assert_eq!(cluster.get(k.to_string()), Some(v.to_string()));
        }
    }

    #[test]
    fn test_concurrent_put_get() {
        let cluster = Arc::new(Cluster::new(3, 3));
        let mut handles = vec![];

        // Spawn threads to perform concurrent put operations.
        for i in 0..10 {
            let cluster_clone = Arc::clone(&cluster);
            handles.push(thread::spawn(move || {
                let key = format!("key{}", i);
                let value = format!("value{}", i);
                cluster_clone.put(key, value);
            }));
        }
        for handle in handles {
            handle.join().unwrap();
        }

        // Spawn threads to perform concurrent get operations.
        let mut read_handles = vec![];
        for i in 0..10 {
            let cluster_clone = Arc::clone(&cluster);
            read_handles.push(thread::spawn(move || {
                let key = format!("key{}", i);
                let value = format!("value{}", i);
                for _ in 0..5 {
                    if let Some(v) = cluster_clone.get(key.clone()) {
                        assert_eq!(v, value);
                    }
                }
            }));
        }
        for handle in read_handles {
            handle.join().unwrap();
        }
    }

    #[test]
    fn test_disk_persistence_simulation() {
        // Simulate disk persistence by using a single-node cluster.
        // We assume that the underlying implementation persists data in Tier2.
        // For this test, we simulate a node restart by invoking a restart method on the cluster.
        let mut cluster = Cluster::new(1, 2);
        cluster.put("persist_key".to_string(), "persist_value".to_string());
        // Simulate a node restart to clear the in-memory cache.
        cluster.restart_node(0);
        // The key should still be retrievable due to Tier2 persistence.
        assert_eq!(cluster.get("persist_key".to_string()), Some("persist_value".to_string()));
    }
}