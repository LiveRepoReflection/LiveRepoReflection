use std::collections::{HashSet, VecDeque};

pub struct Network {
    nodes: Vec<Option<HashSet<usize>>>,
    k: usize,
}

impl Network {
    /// Creates a new network with `initial_n` nodes (with IDs 0..initial_n) and desired partitions `k`.
    pub fn new(initial_n: usize, k: usize) -> Self {
        let mut nodes = Vec::with_capacity(initial_n);
        for _ in 0..initial_n {
            nodes.push(Some(HashSet::new()));
        }
        Network { nodes, k }
    }

    /// Adds a new node with the given `id`. The id must equal the current number of nodes.
    pub fn add_node(&mut self, id: usize) {
        if id != self.nodes.len() {
            panic!("add_node id must be equal to the current number of nodes");
        }
        self.nodes.push(Some(HashSet::new()));
    }

    /// Removes the node with the given `id` and its associated connections.
    pub fn remove_node(&mut self, id: usize) {
        if id >= self.nodes.len() || self.nodes[id].is_none() {
            return;
        }
        // Remove connections from all neighbors.
        if let Some(neighbors) = self.nodes[id].take() {
            for nbr in neighbors {
                if let Some(ref mut other_set) = self.nodes[nbr] {
                    other_set.remove(&id);
                }
            }
        }
    }

    /// Establishes a bidirectional connection between `id1` and `id2`.
    pub fn connect(&mut self, id1: usize, id2: usize) {
        if id1 >= self.nodes.len() || id2 >= self.nodes.len() {
            return;
        }
        if self.nodes[id1].is_none() || self.nodes[id2].is_none() {
            return;
        }
        if let Some(ref mut set1) = self.nodes[id1] {
            set1.insert(id2);
        }
        if let Some(ref mut set2) = self.nodes[id2] {
            set2.insert(id1);
        }
    }

    /// Breaks the connection between `id1` and `id2`.
    pub fn disconnect(&mut self, id1: usize, id2: usize) {
        if id1 >= self.nodes.len() || id2 >= self.nodes.len() {
            return;
        }
        if let Some(ref mut set1) = self.nodes[id1] {
            set1.remove(&id2);
        }
        if let Some(ref mut set2) = self.nodes[id2] {
            set2.remove(&id1);
        }
    }

    /// Partitions the network into `k` sub-networks.
    ///
    /// The algorithm uses a multi-source breadth-first search (BFS) started from up to `k` seed nodes.
    /// If some nodes are not reached by the initial seeds (i.e. in disconnected components),
    /// they are assigned round-robin to the partitions and traversed via BFS.
    /// Returns a Vec<HashSet<usize>> where each HashSet represents the set of node IDs in that partition.
    pub fn partition(&self) -> Vec<HashSet<usize>> {
        let mut partitions: Vec<HashSet<usize>> = Vec::with_capacity(self.k);
        for _ in 0..self.k {
            partitions.push(HashSet::new());
        }
        let n = self.nodes.len();
        let mut assignment = vec![None; n];

        // Multi-source BFS queue: (node, partition_id).
        let mut queue: VecDeque<(usize, usize)> = VecDeque::new();

        // Select seeds for initial partitions from available nodes.
        let mut seed_count = 0;
        for i in 0..n {
            if self.nodes[i].is_some() {
                if seed_count < self.k {
                    assignment[i] = Some(seed_count);
                    partitions[seed_count].insert(i);
                    queue.push_back((i, seed_count));
                    seed_count += 1;
                }
            }
        }

        // Propagate partition assignments using BFS from the seeds.
        while let Some((node, part)) = queue.pop_front() {
            if let Some(ref neighbors) = self.nodes[node] {
                for &nbr in neighbors {
                    if nbr < n && self.nodes[nbr].is_some() && assignment[nbr].is_none() {
                        assignment[nbr] = Some(part);
                        partitions[part].insert(nbr);
                        queue.push_back((nbr, part));
                    }
                }
            }
        }

        // For any unassigned nodes (disconnected components), assign them round-robin and traverse them.
        let mut current_part = 0;
        for i in 0..n {
            if self.nodes[i].is_some() && assignment[i].is_none() {
                assignment[i] = Some(current_part);
                partitions[current_part].insert(i);
                let mut local_queue = VecDeque::new();
                local_queue.push_back((i, current_part));
                while let Some((node, part)) = local_queue.pop_front() {
                    if let Some(ref neighbors) = self.nodes[node] {
                        for &nbr in neighbors {
                            if nbr < n && self.nodes[nbr].is_some() && assignment[nbr].is_none() {
                                assignment[nbr] = Some(part);
                                partitions[part].insert(nbr);
                                local_queue.push_back((nbr, part));
                            }
                        }
                    }
                }
                current_part = (current_part + 1) % self.k;
            }
        }

        partitions
    }
}