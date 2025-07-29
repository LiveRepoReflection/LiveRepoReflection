use std::collections::{BinaryHeap, HashMap, HashSet};
use std::cmp::Ordering;

#[derive(Copy, Clone, Eq, PartialEq)]
struct State {
    latency: u32,
    node: usize,
    cost: u32,
}

impl Ord for State {
    fn cmp(&self, other: &Self) -> Ordering {
        other.cost.cmp(&self.cost)
            .then_with(|| other.latency.cmp(&self.latency))
            .then_with(|| self.node.cmp(&other.node))
    }
}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

#[derive(Clone)]
struct Graph {
    adj_list: Vec<Vec<(usize, u32)>>,
    node_capacities: Vec<u32>,
    current_loads: Vec<u32>,
}

impl Graph {
    fn new(n: usize, connections: &[(usize, usize, u32)], node_capacities: Vec<u32>) -> Result<Self, String> {
        let mut adj_list = vec![Vec::new(); n];
        
        for &(u, v, latency) in connections {
            if u >= n || v >= n {
                return Err("Invalid node ID in connections".to_string());
            }
            adj_list[u].push((v, latency));
            adj_list[v].push((u, latency));
        }
        
        Ok(Graph {
            adj_list,
            node_capacities,
            current_loads: vec![0; n],
        })
    }

    fn find_path(&mut self, start: usize, end: usize, data_size: u32) -> Option<(Vec<usize>, u32)> {
        let n = self.adj_list.len();
        let mut dist = vec![u32::MAX; n];
        let mut prev = vec![None; n];
        let mut heap = BinaryHeap::new();
        let mut visited = HashSet::new();

        dist[start] = 0;
        heap.push(State {
            latency: 0,
            node: start,
            cost: 0,
        });

        while let Some(State { node, latency, .. }) = heap.pop() {
            if node == end {
                let mut path = Vec::new();
                let mut current = end;
                
                while let Some(p) = prev[current] {
                    path.push(current);
                    current = p;
                }
                path.push(start);
                path.reverse();
                
                // Check capacity constraints
                for window in path.windows(2) {
                    if self.current_loads[window[0]] + data_size > self.node_capacities[window[0]] ||
                       self.current_loads[window[1]] + data_size > self.node_capacities[window[1]] {
                        return None;
                    }
                }
                
                // Update loads
                for window in path.windows(2) {
                    self.current_loads[window[0]] += data_size;
                    self.current_loads[window[1]] += data_size;
                }
                
                return Some((path, latency));
            }

            if visited.contains(&node) {
                continue;
            }
            visited.insert(node);

            for &(next, edge_latency) in &self.adj_list[node] {
                if visited.contains(&next) {
                    continue;
                }

                let next_latency = latency + edge_latency;
                if next_latency < dist[next] {
                    dist[next] = next_latency;
                    prev[next] = Some(node);
                    heap.push(State {
                        latency: next_latency,
                        node: next,
                        cost: next_latency,
                    });
                }
            }
        }
        None
    }
}

pub fn find_optimal_routes(
    n: usize,
    connections: Vec<(usize, usize, u32)>,
    node_capacities: Vec<u32>,
    requests: Vec<(usize, usize, u32)>
) -> Result<HashMap<(usize, usize), Vec<usize>>, String> {
    if n == 0 || n > 1000 {
        return Err("Invalid number of nodes".to_string());
    }
    
    if node_capacities.len() != n {
        return Err("Invalid node capacities length".to_string());
    }
    
    // Validate node capacities
    if node_capacities.iter().any(|&cap| cap > 100 || cap == 0) {
        return Err("Invalid node capacity value".to_string());
    }
    
    // Create graph
    let mut graph = Graph::new(n, &connections, node_capacities)?;
    let mut result = HashMap::new();
    
    // Sort requests by data size (larger first to handle harder constraints first)
    let mut requests = requests;
    requests.sort_by_key(|&(_, _, size)| std::cmp::Reverse(size));
    
    // Process each request
    for (source, dest, data_size) in requests {
        if source >= n || dest >= n {
            return Err("Invalid node ID in requests".to_string());
        }
        
        if data_size > 100 || data_size == 0 {
            return Err("Invalid data size".to_string());
        }
        
        if let Some((path, _)) = graph.find_path(source, dest, data_size) {
            result.insert((source, dest), path);
        } else {
            return Err("No valid routing possible".to_string());
        }
    }
    
    Ok(result)
}