use std::collections::{BTreeMap, HashMap};
use std::sync::{Arc, RwLock};

pub struct DistributedStore {
    nodes: Vec<Arc<RwLock<ServerNode>>>,
    node_count: u64,
}

struct ServerNode {
    data: BTreeMap<u64, Vec<u8>>,
}

impl ServerNode {
    fn new() -> Self {
        ServerNode {
            data: BTreeMap::new(),
        }
    }

    fn put(&mut self, key: u64, value: Vec<u8>) {
        self.data.insert(key, value);
    }

    fn get(&self, key: &u64) -> Option<Vec<u8>> {
        self.data.get(key).cloned()
    }

    fn range_query(&self, start_key: u64, end_key: u64) -> Vec<(u64, Vec<u8>)> {
        self.data
            .range(start_key..=end_key)
            .map(|(k, v)| (*k, v.clone()))
            .collect()
    }
}

impl DistributedStore {
    pub fn new(node_count: u64) -> Self {
        assert!(node_count > 0, "Number of nodes must be greater than 0");
        
        let mut nodes = Vec::with_capacity(node_count as usize);
        for _ in 0..node_count {
            nodes.push(Arc::new(RwLock::new(ServerNode::new())));
        }

        DistributedStore {
            nodes,
            node_count,
        }
    }

    pub fn hash(&self, key: u64) -> u64 {
        // FNV-1a hash
        let mut hash: u64 = 14695981039346656037;
        let bytes = key.to_le_bytes();
        
        for byte in bytes.iter() {
            hash ^= *byte as u64;
            hash = hash.wrapping_mul(1099511628211);
        }
        hash
    }

    fn get_responsible_node(&self, key: u64) -> usize {
        (self.hash(key) % self.node_count) as usize
    }

    pub fn put(&self, key: u64, value: Vec<u8>) -> bool {
        let node_idx = self.get_responsible_node(key);
        if let Ok(mut node) = self.nodes[node_idx].write() {
            node.put(key, value);
            true
        } else {
            false
        }
    }

    pub fn get(&self, key: u64) -> Option<Vec<u8>> {
        let node_idx = self.get_responsible_node(key);
        if let Ok(node) = self.nodes[node_idx].read() {
            node.get(&key)
        } else {
            None
        }
    }

    pub fn range_query(&self, start_key: u64, end_key: u64) -> Vec<(u64, Vec<u8>)> {
        // Calculate which nodes might have our data
        let mut potential_nodes = HashMap::new();
        let mut current_key = start_key;
        
        while current_key <= end_key {
            let node_idx = self.get_responsible_node(current_key);
            potential_nodes.insert(node_idx, true);
            current_key = current_key.saturating_add(1);
            
            // Optimization: if we've found all nodes, break
            if potential_nodes.len() == self.nodes.len() {
                break;
            }
        }

        // Query each potential node and collect results
        let mut results = Vec::new();
        for &node_idx in potential_nodes.keys() {
            if let Ok(node) = self.nodes[node_idx].read() {
                results.extend(node.range_query(start_key, end_key));
            }
        }

        // Sort results by key
        results.sort_by_key(|(k, _)| *k);
        results
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_operations() {
        let store = DistributedStore::new(3);
        
        // Test put and get
        assert!(store.put(1, vec![1, 2, 3]));
        assert_eq!(store.get(1), Some(vec![1, 2, 3]));
        
        // Test nonexistent key
        assert_eq!(store.get(2), None);
        
        // Test range query
        store.put(2, vec![4, 5, 6]);
        store.put(3, vec![7, 8, 9]);
        
        let range_result = store.range_query(1, 3);
        assert_eq!(range_result.len(), 3);
        assert_eq!(range_result[0].1, vec![1, 2, 3]);
        assert_eq!(range_result[1].1, vec![4, 5, 6]);
        assert_eq!(range_result[2].1, vec![7, 8, 9]);
    }

    #[test]
    fn test_hash_distribution() {
        let store = DistributedStore::new(5);
        let mut counts = vec![0; 5];
        
        // Test distribution of 1000 keys
        for i in 0..1000 {
            let node_idx = store.get_responsible_node(i);
            counts[node_idx] += 1;
        }
        
        // Check that each node got a reasonable number of keys
        for count in counts {
            assert!(count > 150); // Should be roughly 200 each
        }
    }
}