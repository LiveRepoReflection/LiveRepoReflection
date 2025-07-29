use std::collections::{HashMap, HashSet, BinaryHeap};
use std::cmp::Reverse;

pub struct NetworkTopology {
    nodes: HashSet<i32>,
    graph: HashMap<i32, Vec<(i32, i32)>>, // mapping: from_node -> Vec<(to_node, latency)>
}

impl NetworkTopology {
    pub fn new() -> Self {
        NetworkTopology {
            nodes: HashSet::new(),
            graph: HashMap::new(),
        }
    }

    pub fn contains_node(&self, node_id: i32) -> bool {
        self.nodes.contains(&node_id)
    }

    pub fn add_node(&mut self, node_id: i32) {
        if self.nodes.insert(node_id) {
            self.graph.entry(node_id).or_insert(Vec::new());
        }
    }

    pub fn remove_node(&mut self, node_id: i32) {
        if !self.nodes.remove(&node_id) {
            return;
        }
        // Remove all outgoing edges from node_id.
        self.graph.remove(&node_id);
        // Remove all incoming edges to node_id.
        for edges in self.graph.values_mut() {
            edges.retain(|(dest, _)| *dest != node_id);
        }
    }

    pub fn add_link(&mut self, from_node: i32, to_node: i32, latency: i32) {
        if latency < 0 {
            return;
        }
        if !self.nodes.contains(&from_node) || !self.nodes.contains(&to_node) {
            return;
        }
        let entry = self.graph.entry(from_node).or_insert(Vec::new());
        if entry.iter().any(|(dest, _)| *dest == to_node) {
            return;
        }
        entry.push((to_node, latency));
    }

    pub fn remove_link(&mut self, from_node: i32, to_node: i32) {
        if !self.nodes.contains(&from_node) || !self.nodes.contains(&to_node) {
            return;
        }
        if let Some(edges) = self.graph.get_mut(&from_node) {
            edges.retain(|(dest, _)| *dest != to_node);
        }
    }

    pub fn shortest_path(&self, start_node: i32, end_node: i32) -> Option<i32> {
        if !self.nodes.contains(&start_node) || !self.nodes.contains(&end_node) {
            return None;
        }
        if start_node == end_node {
            return Some(0);
        }

        let mut distances: HashMap<i32, i32> = HashMap::new();
        let mut heap = BinaryHeap::new();
        distances.insert(start_node, 0);
        heap.push(Reverse((0, start_node)));

        while let Some(Reverse((dist, node))) = heap.pop() {
            if node == end_node {
                return Some(dist);
            }
            if let Some(neighbors) = self.graph.get(&node) {
                for &(neighbor, weight) in neighbors.iter() {
                    let next = dist + weight;
                    if next < *distances.get(&neighbor).unwrap_or(&i32::MAX) {
                        distances.insert(neighbor, next);
                        heap.push(Reverse((next, neighbor)));
                    }
                }
            }
        }
        None
    }

    pub fn is_strongly_connected(&self) -> bool {
        if self.nodes.len() <= 1 {
            return true;
        }
        // Choose an arbitrary node.
        let start = *self.nodes.iter().next().unwrap();
        let mut visited = HashSet::new();
        self.dfs(start, &mut visited);
        if visited.len() != self.nodes.len() {
            return false;
        }
        let mut reverse_graph: HashMap<i32, Vec<i32>> = HashMap::new();
        for &node in &self.nodes {
            reverse_graph.insert(node, Vec::new());
        }
        for (&node, edges) in &self.graph {
            for &(neighbor, _) in edges {
                reverse_graph.entry(neighbor).or_insert(Vec::new()).push(node);
            }
        }
        let mut visited_rev = HashSet::new();
        self.dfs_reverse(start, &reverse_graph, &mut visited_rev);
        visited_rev.len() == self.nodes.len()
    }

    fn dfs(&self, start: i32, visited: &mut HashSet<i32>) {
        let mut stack = vec![start];
        while let Some(node) = stack.pop() {
            if visited.insert(node) {
                if let Some(neighbors) = self.graph.get(&node) {
                    for &(neighbor, _) in neighbors.iter() {
                        if !visited.contains(&neighbor) {
                            stack.push(neighbor);
                        }
                    }
                }
            }
        }
    }

    fn dfs_reverse(&self, start: i32, reverse_graph: &HashMap<i32, Vec<i32>>, visited: &mut HashSet<i32>) {
        let mut stack = vec![start];
        while let Some(node) = stack.pop() {
            if visited.insert(node) {
                if let Some(neighbors) = reverse_graph.get(&node) {
                    for &neighbor in neighbors.iter() {
                        if !visited.contains(&neighbor) {
                            stack.push(neighbor);
                        }
                    }
                }
            }
        }
    }

    pub fn find_critical_links(&mut self) -> Vec<(i32, i32)> {
        let mut critical_links = Vec::new();
        // Collect all links in the network.
        let mut links = Vec::new();
        for (&from, edges) in &self.graph {
            for &(to, latency) in edges {
                links.push((from, to, latency));
            }
        }
        // Test removal for each link.
        for (from, to, latency) in links {
            self.remove_link(from, to);
            let alt = self.shortest_path(from, to);
            if alt.is_none() || alt.unwrap() > latency {
                critical_links.push((from, to));
            }
            self.add_link(from, to, latency);
        }
        critical_links
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_add_and_remove_node() {
        let mut net = NetworkTopology::new();
        assert!(!net.contains_node(1));
        net.add_node(1);
        assert!(net.contains_node(1));
        net.add_node(1);
        assert!(net.contains_node(1));
        net.remove_node(1);
        assert!(!net.contains_node(1));
    }

    #[test]
    fn test_add_and_remove_link() {
        let mut net = NetworkTopology::new();
        net.add_node(1);
        net.add_node(2);
        assert_eq!(net.shortest_path(1, 2), None);
        net.add_link(1, 2, 10);
        assert_eq!(net.shortest_path(1, 2), Some(10));
        net.remove_link(1, 2);
        assert_eq!(net.shortest_path(1, 2), None);
    }

    #[test]
    fn test_shortest_path() {
        let mut net = NetworkTopology::new();
        for i in 1..=5 {
            net.add_node(i);
        }
        net.add_link(1, 2, 3);
        net.add_link(2, 3, 4);
        net.add_link(1, 3, 10);
        net.add_link(3, 4, 2);
        net.add_link(4, 5, 1);
        assert_eq!(net.shortest_path(1, 3), Some(7));
        assert_eq!(net.shortest_path(1, 5), Some(10));
    }

    #[test]
    fn test_strongly_connected_empty_and_single() {
        let mut net = NetworkTopology::new();
        assert!(net.is_strongly_connected());
        net.add_node(42);
        assert!(net.is_strongly_connected());
    }

    #[test]
    fn test_is_strongly_connected() {
        let mut net = NetworkTopology::new();
        for i in 1..=4 {
            net.add_node(i);
        }
        net.add_link(1, 2, 1);
        net.add_link(2, 3, 1);
        net.add_link(3, 4, 1);
        net.add_link(4, 1, 1);
        assert!(net.is_strongly_connected());
        net.add_link(1, 3, 2);
        assert!(net.is_strongly_connected());
        net.remove_link(4, 1);
        assert!(!net.is_strongly_connected());
    }

    #[test]
    fn test_find_critical_links() {
        let mut net = NetworkTopology::new();
        for i in 1..=3 {
            net.add_node(i);
        }
        net.add_link(1, 2, 1);
        net.add_link(2, 3, 1);
        net.add_link(1, 3, 3);
        let critical_links = net.find_critical_links();
        assert!(critical_links.contains(&(1, 2)));
        assert!(critical_links.contains(&(2, 3)));
        assert!(!critical_links.contains(&(1, 3)));
    }

    #[test]
    fn test_edge_cases() {
        let mut net = NetworkTopology::new();
        net.remove_node(10);
        net.remove_link(1, 2);
        net.add_link(1, 2, 5);
        assert_eq!(net.shortest_path(1, 2), None);
        net.add_node(1);
        net.add_node(2);
        net.add_link(1, 1, 0);
        assert_eq!(net.shortest_path(1, 1), Some(0));
        net.remove_link(2, 1);
        net.add_link(1, 2, 5);
        assert_eq!(net.shortest_path(1, 2), Some(5));
        net.remove_node(1);
        assert_eq!(net.shortest_path(1, 2), None);
    }
}