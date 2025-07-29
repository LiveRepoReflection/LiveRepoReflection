use std::collections::{HashMap, HashSet, BinaryHeap};
use std::cmp::Ordering;
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug, Clone)]
pub struct RoutingTable {
    nodes: HashSet<u32>,
    edges: HashMap<u32, HashMap<u32, (u32, u64)>>,
    max_hops: usize,
}

#[derive(Debug, PartialEq, Eq)]
struct Path {
    nodes: Vec<u32>,
    total_weight: u32,
}

impl PartialOrd for Path {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for Path {
    fn cmp(&self, other: &Self) -> Ordering {
        other.total_weight.cmp(&self.total_weight)
    }
}

impl RoutingTable {
    pub fn new() -> Self {
        RoutingTable {
            nodes: HashSet::new(),
            edges: HashMap::new(),
            max_hops: 5,
        }
    }

    pub fn add_node(&mut self, node: u32) {
        self.nodes.insert(node);
        self.edges.entry(node).or_default();
    }

    pub fn add_edge(&mut self, from: u32, to: u32, weight: u32) {
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        self.add_edge_with_timestamp(from, to, weight, timestamp);
    }

    pub fn add_edge_with_timestamp(&mut self, from: u32, to: u32, weight: u32, timestamp: u64) {
        self.add_node(from);
        self.add_node(to);
        
        let entry = self.edges.entry(from).or_default();
        if let Some((_, existing_timestamp)) = entry.get(&to) {
            if *existing_timestamp > timestamp {
                return;
            }
        }
        entry.insert(to, (weight, timestamp));
    }

    pub fn remove_edge(&mut self, from: u32, to: u32) {
        if let Some(targets) = self.edges.get_mut(&from) {
            targets.remove(&to);
        }
    }

    pub fn set_max_hops(&mut self, hops: usize) {
        self.max_hops = hops;
    }

    fn get_neighbors(&self, node: u32) -> Option<&HashMap<u32, (u32, u64)>> {
        self.edges.get(&node)
    }

    fn get_edge_weight(&self, from: u32, to: u32) -> Option<u32> {
        self.edges.get(&from)?.get(&to).map(|(w, _)| *w)
    }
}

pub fn find_k_shortest_paths(
    rt: &RoutingTable,
    start: u32,
    end: u32,
    k: usize,
) -> Result<Vec<Vec<u32>>, String> {
    if !rt.nodes.contains(&start) || !rt.nodes.contains(&end) {
        return Err("Start or end node not found".to_string());
    }

    if start == end {
        return Ok(vec![vec![start]]);
    }

    let mut paths = BinaryHeap::new();
    let mut visited = HashSet::new();
    let mut candidates = BinaryHeap::new();

    candidates.push(Path {
        nodes: vec![start],
        total_weight: 0,
    });

    while let Some(current_path) = candidates.pop() {
        let last_node = *current_path.nodes.last().unwrap();

        if last_node == end {
            paths.push(current_path);
            if paths.len() >= k {
                break;
            }
            continue;
        }

        if visited.contains(&(last_node, current_path.nodes.len())) {
            continue;
        }
        visited.insert((last_node, current_path.nodes.len()));

        if current_path.nodes.len() >= rt.max_hops {
            continue;
        }

        if let Some(neighbors) = rt.get_neighbors(last_node) {
            for (&neighbor, &(weight, _)) in neighbors {
                if !current_path.nodes.contains(&neighbor) {
                    let mut new_nodes = current_path.nodes.clone();
                    new_nodes.push(neighbor);
                    candidates.push(Path {
                        nodes: new_nodes,
                        total_weight: current_path.total_weight + weight,
                    });
                }
            }
        }
    }

    if paths.is_empty() {
        return Err("No path found".to_string());
    }

    let mut result: Vec<Vec<u32>> = paths.into_sorted_vec()
        .into_iter()
        .take(k)
        .map(|p| p.nodes)
        .collect();

    result.sort_by_key(|path| {
        path.iter().skip(1).enumerate().fold(0, |acc, (i, &node)| {
            acc + rt.get_edge_weight(path[i], node).unwrap_or(0)
        })
    });

    Ok(result)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_routing_table_basics() {
        let mut rt = RoutingTable::new();
        rt.add_node(1);
        rt.add_node(2);
        rt.add_edge(1, 2, 10);
        
        assert!(rt.nodes.contains(&1));
        assert!(rt.nodes.contains(&2));
        assert_eq!(rt.get_edge_weight(1, 2), Some(10));
    }
}