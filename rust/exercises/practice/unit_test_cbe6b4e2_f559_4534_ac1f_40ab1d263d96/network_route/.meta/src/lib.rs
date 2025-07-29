use std::collections::{BinaryHeap, HashMap, HashSet};
use std::cmp::Ordering;

#[derive(Copy, Clone, Eq, PartialEq)]
struct State {
    cost: u32,
    node: usize,
}

impl Ord for State {
    fn cmp(&self, other: &Self) -> Ordering {
        other.cost.cmp(&self.cost)
            .then_with(|| self.node.cmp(&other.node))
    }
}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

pub struct Network {
    size: usize,
    // Using HashMap for sparse graph representation
    adjacency_list: Vec<HashMap<usize, u32>>,
    // Cache for frequently queried paths
    path_cache: HashMap<(usize, usize), i32>,
    // Track modified nodes to invalidate cache
    modified_nodes: HashSet<usize>,
}

impl Network {
    pub fn new(size: usize) -> Self {
        Network {
            size,
            adjacency_list: vec![HashMap::new(); size],
            path_cache: HashMap::new(),
            modified_nodes: HashSet::new(),
        }
    }

    pub fn add_link(&mut self, node1: usize, node2: usize, latency: u32) {
        if node1 >= self.size || node2 >= self.size {
            return;
        }
        
        self.adjacency_list[node1].insert(node2, latency);
        self.adjacency_list[node2].insert(node1, latency);
        
        // Mark nodes as modified to invalidate cache
        self.modified_nodes.insert(node1);
        self.modified_nodes.insert(node2);
    }

    pub fn remove_link(&mut self, node1: usize, node2: usize) {
        if node1 >= self.size || node2 >= self.size {
            return;
        }
        
        self.adjacency_list[node1].remove(&node2);
        self.adjacency_list[node2].remove(&node1);
        
        // Mark nodes as modified to invalidate cache
        self.modified_nodes.insert(node1);
        self.modified_nodes.insert(node2);
    }

    pub fn get_shortest_path(&mut self, src: usize, dest: usize) -> i32 {
        if src >= self.size || dest >= self.size {
            return -1;
        }

        if src == dest {
            return 0;
        }

        // Check cache if nodes haven't been modified
        let cache_key = (src, dest);
        if !self.modified_nodes.contains(&src) && !self.modified_nodes.contains(&dest) {
            if let Some(&cached_result) = self.path_cache.get(&cache_key) {
                return cached_result;
            }
        }

        // Initialize distance vector
        let mut distances: Vec<Option<u32>> = vec![None; self.size];
        distances[src] = Some(0);

        // Priority queue for Dijkstra's algorithm
        let mut heap = BinaryHeap::new();
        heap.push(State { cost: 0, node: src });

        while let Some(State { cost, node }) = heap.pop() {
            // If we've reached the destination, we're done
            if node == dest {
                let result = cost as i32;
                self.path_cache.insert(cache_key, result);
                return result;
            }

            // If we've found a longer path, skip
            if let Some(current_dist) = distances[node] {
                if cost > current_dist {
                    continue;
                }
            }

            // Check all neighboring nodes
            for (&next_node, &edge_cost) in &self.adjacency_list[node] {
                let next_cost = match cost.checked_add(edge_cost) {
                    Some(sum) => sum,
                    None => continue, // Skip if overflow would occur
                };

                if let Some(current_dist) = distances[next_node] {
                    if next_cost >= current_dist {
                        continue;
                    }
                }

                distances[next_node] = Some(next_cost);
                heap.push(State {
                    cost: next_cost,
                    node: next_node,
                });
            }
        }

        // No path found
        let result = -1;
        self.path_cache.insert(cache_key, result);
        result
    }
}