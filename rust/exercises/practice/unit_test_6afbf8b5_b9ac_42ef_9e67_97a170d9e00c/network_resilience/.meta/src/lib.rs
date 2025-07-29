use std::collections::{HashMap, VecDeque};

pub type NodeId = char;
pub type Edge = (NodeId, NodeId, u64);

#[derive(Debug, Clone)]
pub struct Graph {
    pub nodes: Vec<NodeId>,
    pub adjacency: HashMap<NodeId, Vec<(NodeId, u64)>>,
}

impl Graph {
    pub fn new(nodes: Vec<NodeId>) -> Self {
        let mut adjacency = HashMap::new();
        for &n in &nodes {
            adjacency.insert(n, Vec::new());
        }
        Graph { nodes, adjacency }
    }

    pub fn add_edge(&mut self, u: NodeId, v: NodeId, cost: u64) {
        if self.has_edge(u, v) {
            return;
        }
        if let Some(neighbors) = self.adjacency.get_mut(&u) {
            neighbors.push((v, cost));
        }
        if let Some(neighbors) = self.adjacency.get_mut(&v) {
            neighbors.push((u, cost));
        }
    }

    pub fn has_edge(&self, u: NodeId, v: NodeId) -> bool {
        if let Some(neighbors) = self.adjacency.get(&u) {
            for &(nbr, _) in neighbors {
                if nbr == v {
                    return true;
                }
            }
        }
        false
    }

    pub fn is_connected_after_removal(&self, removed: NodeId) -> bool {
        let remaining_nodes: Vec<NodeId> = self.nodes.iter().cloned().filter(|&n| n != removed).collect();
        if remaining_nodes.is_empty() {
            return true;
        }
        let start = remaining_nodes[0];
        let mut visited = HashMap::new();
        let mut queue = VecDeque::new();
        queue.push_back(start);
        visited.insert(start, true);
        while let Some(curr) = queue.pop_front() {
            if let Some(neighbors) = self.adjacency.get(&curr) {
                for &(nbr, _) in neighbors {
                    if nbr == removed {
                        continue;
                    }
                    if !visited.contains_key(&nbr) {
                        visited.insert(nbr, true);
                        queue.push_back(nbr);
                    }
                }
            }
        }
        visited.len() == remaining_nodes.len()
    }

    pub fn disconnected_pairs_after_removal(&self, removed: NodeId) -> u64 {
        let remaining: Vec<NodeId> = self.nodes.iter().cloned().filter(|&n| n != removed).collect();
        let total = remaining.len() as u64;
        if total < 2 {
            return 0;
        }
        let mut visited = HashMap::new();
        let mut components: Vec<u64> = Vec::new();
        for &node in &remaining {
            if visited.contains_key(&node) {
                continue;
            }
            let mut size = 0;
            let mut queue = VecDeque::new();
            queue.push_back(node);
            visited.insert(node, true);
            while let Some(curr) = queue.pop_front() {
                size += 1;
                if let Some(neighbors) = self.adjacency.get(&curr) {
                    for &(nbr, _) in neighbors {
                        if nbr == removed {
                            continue;
                        }
                        if remaining.contains(&nbr) && !visited.contains_key(&nbr) {
                            visited.insert(nbr, true);
                            queue.push_back(nbr);
                        }
                    }
                }
            }
            components.push(size);
        }
        let total_pairs = total * (total - 1) / 2;
        let mut connected_pairs = 0;
        for s in components {
            connected_pairs += s * (s - 1) / 2;
        }
        total_pairs - connected_pairs
    }
}

pub fn is_resilient(graph: &Graph) -> bool {
    for &node in &graph.nodes {
        if !graph.is_connected_after_removal(node) {
            return false;
        }
    }
    true
}

pub fn minimize_disruption(graph: &mut Graph, facility_failure_probability: &HashMap<NodeId, f64>, mut budget: u64) -> Vec<Edge> {
    let mut added_edges: Vec<Edge> = Vec::new();

    fn expected_disruption(graph: &Graph, failure_prob: &HashMap<NodeId, f64>) -> f64 {
        let mut total = 0.0;
        for &node in &graph.nodes {
            let fp = *failure_prob.get(&node).unwrap_or(&0.0);
            let dp = graph.disconnected_pairs_after_removal(node) as f64;
            total += fp * dp;
        }
        total
    }

    let mut current_metric = expected_disruption(graph, facility_failure_probability);

    loop {
        let mut best_improvement = 0.0;
        let mut best_candidate: Option<Edge> = None;

        for i in 0..graph.nodes.len() {
            for j in (i + 1)..graph.nodes.len() {
                let u = graph.nodes[i];
                let v = graph.nodes[j];
                if graph.has_edge(u, v) {
                    continue;
                }
                let cost = (u as u64) + (v as u64);
                if cost > budget {
                    continue;
                }
                graph.add_edge(u, v, cost);
                let new_metric = expected_disruption(graph, facility_failure_probability);
                let improvement = current_metric - new_metric;
                if let Some(neighbors) = graph.adjacency.get_mut(&u) {
                    if let Some(pos) = neighbors.iter().position(|&(nbr, c)| nbr == v && c == cost) {
                        neighbors.remove(pos);
                    }
                }
                if let Some(neighbors) = graph.adjacency.get_mut(&v) {
                    if let Some(pos) = neighbors.iter().position(|&(nbr, c)| nbr == u && c == cost) {
                        neighbors.remove(pos);
                    }
                }
                if improvement > best_improvement {
                    best_improvement = improvement;
                    best_candidate = Some((u, v, cost));
                } else if (improvement - best_improvement).abs() < 1e-9 {
                    if let Some((bu, bv, _)) = best_candidate {
                        if u < bu || (u == bu && v < bv) {
                            best_candidate = Some((u, v, cost));
                        }
                    }
                }
            }
        }

        if let Some((u, v, cost)) = best_candidate {
            if cost > budget || best_improvement <= 0.0 {
                break;
            }
            graph.add_edge(u, v, cost);
            added_edges.push((u, v, cost));
            current_metric = expected_disruption(graph, facility_failure_probability);
            budget -= cost;
        } else {
            break;
        }
    }

    added_edges
}