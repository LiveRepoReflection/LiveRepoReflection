use std::collections::HashMap;
use std::sync::{Arc, Mutex};

pub struct ReplicaSystem {
    nodes: Vec<Arc<Node>>,
}

struct Node {
    id: usize,
    store: Mutex<HashMap<usize, Vec<u8>>>,
}

impl Node {
    fn new(id: usize) -> Node {
        Node {
            id,
            store: Mutex::new(HashMap::new()),
        }
    }
    
    fn load(&self) -> usize {
        let store = self.store.lock().unwrap();
        store.len()
    }
}

impl ReplicaSystem {
    pub fn new(num_nodes: usize) -> ReplicaSystem {
        let mut nodes = Vec::new();
        for id in 0..num_nodes {
            nodes.push(Arc::new(Node::new(id)));
        }
        ReplicaSystem { nodes }
    }

    pub fn store(&self, node_id: usize, chunk_id: usize, data: Vec<u8>) -> Result<(), String> {
        if node_id >= self.nodes.len() {
            return Err(format!("Invalid node id: {}", node_id));
        }
        let node = &self.nodes[node_id];
        let mut store = node.store.lock().unwrap();
        if store.contains_key(&chunk_id) {
            return Err(format!("Chunk {} already exists on node {}", chunk_id, node_id));
        }
        store.insert(chunk_id, data);
        Ok(())
    }

    pub fn fetch(&self, node_id: usize, chunk_id: usize) -> Result<Vec<u8>, String> {
        if node_id >= self.nodes.len() {
            return Err(format!("Invalid node id: {}", node_id));
        }
        let node = &self.nodes[node_id];
        let store = node.store.lock().unwrap();
        match store.get(&chunk_id) {
            Some(data) => Ok(data.clone()),
            None => Err(format!("Chunk {} not found on node {}", chunk_id, node_id)),
        }
    }

    pub fn replicate(&self, chunk_id: usize, replication_factor: usize) -> Result<Vec<usize>, String> {
        if replication_factor > self.nodes.len() {
            return Err(format!(
                "Replication factor {} is greater than number of available nodes {}",
                replication_factor,
                self.nodes.len()
            ));
        }
        // Find all nodes that already have the chunk.
        let mut nodes_with_chunk = Vec::new();
        for node in &self.nodes {
            let store = node.store.lock().unwrap();
            if store.contains_key(&chunk_id) {
                nodes_with_chunk.push(node.id);
            }
        }
        // If no node holds the chunk, we cannot replicate.
        if nodes_with_chunk.is_empty() {
            return Err(format!("Chunk {} not found on any node", chunk_id));
        }
        // If we already have enough replicas, just return.
        if nodes_with_chunk.len() >= replication_factor {
            nodes_with_chunk.truncate(replication_factor);
            nodes_with_chunk.sort_unstable();
            return Ok(nodes_with_chunk);
        }
        let additional_needed = replication_factor - nodes_with_chunk.len();

        // Gather candidate nodes that do not have the chunk along with their loads.
        let mut candidates: Vec<(usize, usize)> = Vec::new(); // (node_id, load)
        for node in &self.nodes {
            if !nodes_with_chunk.contains(&node.id) {
                let load = node.load();
                candidates.push((node.id, load));
            }
        }
        // Sort candidates by load (ascending) then by node id.
        candidates.sort_by(|a, b| a.1.cmp(&b.1).then(a.0.cmp(&b.0)));

        if candidates.len() < additional_needed {
            return Err(format!("Not enough available nodes to replicate chunk {}", chunk_id));
        }

        // Get the chunk data from an existing node (using the first one found).
        let source_node = &self.nodes[nodes_with_chunk[0]];
        let data = {
            let store = source_node.store.lock().unwrap();
            match store.get(&chunk_id) {
                Some(data) => data.clone(),
                None => return Err(format!("Source node {} lost chunk {}", source_node.id, chunk_id)),
            }
        };

        // Replicate the chunk to additional nodes.
        let mut replicated_nodes = Vec::new();
        for i in 0..additional_needed {
            let node_id = candidates[i].0;
            let candidate_node = &self.nodes[node_id];
            let mut store = candidate_node.store.lock().unwrap();
            store.insert(chunk_id, data.clone());
            replicated_nodes.push(node_id);
        }
        nodes_with_chunk.extend(replicated_nodes);
        nodes_with_chunk.sort_unstable();
        Ok(nodes_with_chunk)
    }

    pub fn delete(&self, chunk_id: usize) -> Result<(), String> {
        let mut found = false;
        for node in &self.nodes {
            let mut store = node.store.lock().unwrap();
            if store.remove(&chunk_id).is_some() {
                found = true;
            }
        }
        if found {
            Ok(())
        } else {
            Err(format!("Chunk {} not found on any node", chunk_id))
        }
    }

    pub fn recover(&self, chunk_id: usize) -> Result<Vec<u8>, String> {
        // Gather all nodes with the chunk along with their loads.
        let mut candidates: Vec<(usize, usize)> = Vec::new(); // (node_id, load)
        for node in &self.nodes {
            let store = node.store.lock().unwrap();
            if store.contains_key(&chunk_id) {
                candidates.push((node.id, store.len()));
            }
        }
        if candidates.is_empty() {
            return Err(format!("Chunk {} not found on any available node", chunk_id));
        }
        // Select the candidate with the lowest load (and smallest node id for tie-breaker).
        candidates.sort_by(|a, b| a.1.cmp(&b.1).then(a.0.cmp(&b.0)));
        let chosen_node = &self.nodes[candidates[0].0];
        let store = chosen_node.store.lock().unwrap();
        match store.get(&chunk_id) {
            Some(data) => Ok(data.clone()),
            None => Err(format!("Chunk {} not found on node {}", chunk_id, chosen_node.id)),
        }
    }
}