use std::collections::{BinaryHeap, HashMap};
use std::cmp::Ordering;

#[derive(Debug)]
pub struct Network {
    graph: HashMap<u64, Vec<(u64, f64)>>,
}

impl Network {
    pub fn new() -> Self {
        Network {
            graph: HashMap::new(),
        }
    }

    // Adds an edge between node_a and node_b with the given weight.
    // Returns an error if weight is negative.
    pub fn add_edge(&mut self, node_a: u64, node_b: u64, weight: f64) -> Result<(), String> {
        if weight < 0.0 {
            return Err(String::from("Negative weights are not allowed"));
        }
        self.graph.entry(node_a).or_insert(Vec::new()).push((node_b, weight));
        self.graph.entry(node_b).or_insert(Vec::new()).push((node_a, weight));
        Ok(())
    }

    // Removes the edge between node_a and node_b.
    pub fn remove_edge(&mut self, node_a: u64, node_b: u64) -> Result<(), String> {
        if let Some(neighbors) = self.graph.get_mut(&node_a) {
            neighbors.retain(|&(nbr, _)| nbr != node_b);
        }
        if let Some(neighbors) = self.graph.get_mut(&node_b) {
            neighbors.retain(|&(nbr, _)| nbr != node_a);
        }
        Ok(())
    }

    // Updates the weight of the edge between node_a and node_b.
    // Returns an error if the edge does not exist or if weight is negative.
    pub fn update_edge(&mut self, node_a: u64, node_b: u64, new_weight: f64) -> Result<(), String> {
        if new_weight < 0.0 {
            return Err(String::from("Negative weights are not allowed"));
        }
        let mut updated = false;
        if let Some(neighbors) = self.graph.get_mut(&node_a) {
            for neighbor in neighbors.iter_mut() {
                if neighbor.0 == node_b {
                    neighbor.1 = new_weight;
                    updated = true;
                }
            }
        }
        if let Some(neighbors) = self.graph.get_mut(&node_b) {
            for neighbor in neighbors.iter_mut() {
                if neighbor.0 == node_a {
                    neighbor.1 = new_weight;
                    updated = true;
                }
            }
        }
        if !updated {
            return Err(String::from("Edge not found"));
        }
        Ok(())
    }

    // Computes the shortest path from source to destination using Dijkstra's algorithm.
    // Returns Ok(Some((cost, path))) if a path exists, Ok(None) if no path is found.
    pub fn shortest_path(&self, source: u64, destination: u64) -> Result<Option<(f64, Vec<u64>)>, String> {
        if source == destination {
            return Ok(Some((0.0, vec![source])));
        }
        // If either node does not exist in the graph, no path exists.
        if !self.graph.contains_key(&source) || !self.graph.contains_key(&destination) {
            return Ok(None);
        }

        let mut dist: HashMap<u64, f64> = HashMap::new();
        let mut prev: HashMap<u64, u64> = HashMap::new();

        // Priority queue implemented as a min-heap using our State struct.
        let mut heap = BinaryHeap::new();

        // Initialize distance for source.
        dist.insert(source, 0.0);
        heap.push(State { cost: 0.0, node: source });

        while let Some(State { cost, node }) = heap.pop() {
            // If we reached the destination, reconstruct the path.
            if node == destination {
                let mut path = vec![destination];
                let mut current = destination;
                while let Some(&p) = prev.get(&current) {
                    path.push(p);
                    current = p;
                }
                path.reverse();
                return Ok(Some((cost, path)));
            }

            // If the cost is greater than the recorded cost, skip.
            if let Some(&current_dist) = dist.get(&node) {
                if cost > current_dist {
                    continue;
                }
            }

            if let Some(neighbors) = self.graph.get(&node) {
                for &(neighbor, weight) in neighbors.iter() {
                    let next = State { cost: cost + weight, node: neighbor };
                    // If found a shorter path to neighbor, update.
                    if dist.get(&neighbor).map_or(true, |&d| next.cost < d) {
                        dist.insert(neighbor, next.cost);
                        prev.insert(neighbor, node);
                        heap.push(next);
                    }
                }
            }
        }
        Ok(None)
    }
}

#[derive(Copy, Clone, Debug)]
struct State {
    cost: f64,
    node: u64,
}

impl PartialEq for State {
    fn eq(&self, other: &Self) -> bool {
        self.cost == other.cost && self.node == other.node
    }
}

impl Eq for State {}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        // Invert comparison to make BinaryHeap work as min-heap.
        other.cost.partial_cmp(&self.cost)
    }
}

impl Ord for State {
    fn cmp(&self, other: &Self) -> Ordering {
        self.partial_cmp(other).unwrap()
    }
}