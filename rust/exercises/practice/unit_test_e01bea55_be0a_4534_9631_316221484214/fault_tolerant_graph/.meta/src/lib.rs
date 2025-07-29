use std::collections::{HashMap, VecDeque};
use std::sync::RwLock;

pub type NodeId = u64;

#[derive(Debug)]
struct Edge {
    to: NodeId,
    payload: String,
}

#[derive(Debug)]
struct Node {
    payload: String,
    available: bool,
    out_edges: Vec<Edge>,
}

pub struct FaultTolerantGraph {
    nodes: RwLock<HashMap<NodeId, Node>>,
}

impl FaultTolerantGraph {
    pub fn new() -> Self {
        FaultTolerantGraph {
            nodes: RwLock::new(HashMap::new()),
        }
    }

    pub fn add_node(&mut self, id: NodeId, payload: String) -> Result<(), String> {
        let mut nodes = self.nodes.write().map_err(|_| "Lock poisoned".to_string())?;
        if nodes.contains_key(&id) {
            return Err(format!("Node {} already exists", id));
        }
        nodes.insert(
            id,
            Node {
                payload,
                available: true,
                out_edges: Vec::new(),
            },
        );
        Ok(())
    }

    pub fn remove_node(&mut self, id: NodeId) -> Result<(), String> {
        let mut nodes = self.nodes.write().map_err(|_| "Lock poisoned".to_string())?;
        if !nodes.contains_key(&id) {
            return Err(format!("Node {} does not exist", id));
        }
        nodes.remove(&id);
        // Remove all incoming edges from all other nodes.
        for (_other_id, node) in nodes.iter_mut() {
            node.out_edges.retain(|edge| edge.to != id);
        }
        Ok(())
    }

    pub fn add_edge(&mut self, from: NodeId, to: NodeId, payload: String) -> Result<(), String> {
        let mut nodes = self.nodes.write().map_err(|_| "Lock poisoned".to_string())?;
        if !nodes.contains_key(&from) {
            return Err(format!("Source node {} does not exist", from));
        }
        if !nodes.contains_key(&to) {
            return Err(format!("Destination node {} does not exist", to));
        }
        if let Some(node) = nodes.get_mut(&from) {
            node.out_edges.push(Edge { to, payload });
            Ok(())
        } else {
            Err("Unexpected error".to_string())
        }
    }

    pub fn remove_edge(&mut self, from: NodeId, to: NodeId, payload: Option<String>) -> Result<(), String> {
        let mut nodes = self.nodes.write().map_err(|_| "Lock poisoned".to_string())?;
        let node = nodes.get_mut(&from).ok_or_else(|| format!("Source node {} does not exist", from))?;
        let original_len = node.out_edges.len();
        if let Some(ref p) = payload {
            let mut removed = false;
            if let Some(pos) = node.out_edges.iter().position(|edge| edge.to == to && edge.payload == *p) {
                node.out_edges.remove(pos);
                removed = true;
            }
            if !removed {
                return Err(format!("Edge from {} to {} with payload '{}' not found", from, to, p));
            }
        } else {
            node.out_edges.retain(|edge| edge.to != to);
            if node.out_edges.len() == original_len {
                return Err(format!("No edges from {} to {} found", from, to));
            }
        }
        Ok(())
    }

    pub fn mark_unavailable(&mut self, id: NodeId) -> Result<(), String> {
        let mut nodes = self.nodes.write().map_err(|_| "Lock poisoned".to_string())?;
        let node = nodes.get_mut(&id).ok_or_else(|| format!("Node {} does not exist", id))?;
        node.available = false;
        Ok(())
    }

    pub fn mark_available(&mut self, id: NodeId) -> Result<(), String> {
        let mut nodes = self.nodes.write().map_err(|_| "Lock poisoned".to_string())?;
        let node = nodes.get_mut(&id).ok_or_else(|| format!("Node {} does not exist", id))?;
        node.available = true;
        Ok(())
    }

    pub fn approximate_shortest_path(&self, start_node: NodeId, end_node: NodeId, max_hops: u32) -> Option<Vec<NodeId>> {
        let nodes = self.nodes.read().ok()?;
        // Check that start and end nodes exist.
        let start = nodes.get(&start_node)?;
        if !start.available {
            return None;
        }
        if start_node == end_node {
            return Some(vec![start_node]);
        }
        let mut queue = VecDeque::new();
        queue.push_back((start_node, vec![start_node]));
        let mut visited = HashMap::new();
        visited.insert(start_node, 0u32);

        while let Some((current, path)) = queue.pop_front() {
            if (path.len() as u32 - 1) >= max_hops {
                continue;
            }
            let current_node = nodes.get(&current)?;
            for edge in &current_node.out_edges {
                if let Some(next_node) = nodes.get(&edge.to) {
                    if !next_node.available {
                        continue;
                    }
                    let next_hops = path.len() as u32;
                    if let Some(&prev_hops) = visited.get(&edge.to) {
                        if next_hops >= prev_hops {
                            continue;
                        }
                    }
                    let mut new_path = path.clone();
                    new_path.push(edge.to);
                    if edge.to == end_node {
                        return Some(new_path);
                    }
                    visited.insert(edge.to, next_hops);
                    queue.push_back((edge.to, new_path));
                }
            }
        }
        None
    }
}