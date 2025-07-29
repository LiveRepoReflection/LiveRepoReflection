use std::collections::{HashMap, VecDeque};

#[derive(Clone, Debug)]
pub enum Event {
    AddRequest {
        request_id: i32,
        source: i32,
        destination: i32,
        demand: i32,
    },
    RemoveRequest {
        request_id: i32,
    },
    UpdateRequest {
        request_id: i32,
        demand: i32,
    },
    UpdateCapacity {
        source: i32,
        destination: i32,
        capacity: i32,
    },
}

#[derive(Clone, Debug)]
struct Request {
    request_id: i32,
    source: i32,
    destination: i32,
    demand: i32,
}

pub struct Simulation {
    // graph represented as: node -> Vec<(neighbor, source, destination)>
    graph: HashMap<i32, Vec<(i32, i32, i32)>>,
    // mapping of edge (u,v) to capacity
    capacities: HashMap<(i32, i32), i32>,
    // active requests: request_id -> Request
    requests: HashMap<i32, Request>,
}

impl Simulation {
    pub fn new(
        edges: Vec<(i32, i32, i32)>,
        initial_requests: Vec<(i32, i32, i32, i32)>,
    ) -> Self {
        let mut capacities = HashMap::new();
        let mut graph: HashMap<i32, Vec<(i32, i32, i32)>> = HashMap::new();
        for (u, v, cap) in edges.into_iter() {
            capacities.insert((u, v), cap);
            graph.entry(u).or_default().push((v, u, v));
        }
        let mut requests = HashMap::new();
        for (id, src, dest, demand) in initial_requests.into_iter() {
            requests.insert(
                id,
                Request {
                    request_id: id,
                    source: src,
                    destination: dest,
                    demand,
                },
            );
        }
        Simulation {
            graph,
            capacities,
            requests,
        }
    }

    // Process an event and then return current allocations
    pub fn process_event(&mut self, event: Event) -> Vec<(i32, i32)> {
        match event {
            Event::AddRequest {
                request_id,
                source,
                destination,
                demand,
            } => {
                self.requests.insert(
                    request_id,
                    Request {
                        request_id,
                        source,
                        destination,
                        demand,
                    },
                );
            }
            Event::RemoveRequest { request_id } => {
                self.requests.remove(&request_id);
            }
            Event::UpdateRequest { request_id, demand } => {
                if let Some(req) = self.requests.get_mut(&request_id) {
                    req.demand = demand;
                }
            }
            Event::UpdateCapacity {
                source,
                destination,
                capacity,
            } => {
                self.capacities.insert((source, destination), capacity);
            }
        }
        self.allocations()
    }

    // Compute current allocations for all active requests.
    // Return vector of (request_id, achieved_flow) sorted by request_id.
    pub fn allocations(&mut self) -> Vec<(i32, i32)> {
        // For each active request, find a path (if any)
        let mut req_paths: HashMap<i32, Vec<(i32, i32)>> = HashMap::new();
        for (req_id, req) in self.requests.iter() {
            if let Some(path) = self.find_path(req.source, req.destination) {
                req_paths.insert(*req_id, path);
            } else {
                // No path found; treat allocation as 0 by inserting empty vector
                req_paths.insert(*req_id, Vec::new());
            }
        }

        // For each edge, gather the requests that use that edge and record their demand.
        let mut edge_to_requests: HashMap<(i32, i32), Vec<(i32, i32)>> = HashMap::new();
        for (&req_id, path) in req_paths.iter() {
            // if path is empty, allocation stays 0.
            if path.is_empty() {
                continue;
            }
            // Get demand for the request.
            let demand = self.requests.get(&req_id).unwrap().demand;
            // For each edge in the path, add the (req_id, demand) pair.
            for &edge in path.iter() {
                edge_to_requests.entry(edge).or_default().push((req_id, demand));
            }
        }

        // For each edge, compute the allocation for each request on that edge.
        let mut edge_allocations: HashMap<(i32, i32), HashMap<i32, i32>> = HashMap::new();
        for (edge, req_list) in edge_to_requests.iter() {
            let capacity = *self.capacities.get(edge).unwrap_or(&0);
            let total_demand: i32 = req_list.iter().map(|&(_, d)| d).sum();
            let mut alloc_map: HashMap<i32, i32> = HashMap::new();
            if total_demand == 0 || capacity == 0 {
                // No allocation possible.
                for &(req_id, _) in req_list.iter() {
                    alloc_map.insert(req_id, 0);
                }
            } else {
                // Base allocation: floor(capacity * demand / total_demand)
                let mut base_allocs: Vec<(i32, i32)> = Vec::new();
                let mut sum_alloc = 0;
                for &(req_id, demand) in req_list.iter() {
                    let alloc = capacity * demand / total_demand;
                    base_allocs.push((req_id, alloc));
                    sum_alloc += alloc;
                }
                let mut remainder = capacity - sum_alloc;
                // Distribute remainders to requests in order of request_id if they haven't exceeded their demand.
                base_allocs.sort_by_key(|&(req_id, _)| req_id);
                for &mut (req_id, ref mut alloc) in base_allocs.iter_mut() {
                    let demand = req_list.iter().find(|&&(r_id, _)| r_id == req_id).unwrap().1;
                    if remainder > 0 && *alloc < demand {
                        *alloc += 1;
                        remainder -= 1;
                    }
                    alloc_map.insert(req_id, *alloc);
                }
            }
            edge_allocations.insert(*edge, alloc_map);
        }

        // For each request, its achieved allocation is the minimum allocation along its path,
        // capped by its demand.
        let mut result: Vec<(i32, i32)> = Vec::new();
        for (&req_id, req) in self.requests.iter() {
            let path = req_paths.get(&req_id).unwrap();
            if path.is_empty() {
                result.push((req_id, 0));
            } else {
                let mut achieved = std::i32::MAX;
                for &edge in path.iter() {
                    let alloc = edge_allocations
                        .get(&edge)
                        .and_then(|m| m.get(&req_id))
                        .cloned()
                        .unwrap_or(0);
                    if alloc < achieved {
                        achieved = alloc;
                    }
                }
                if achieved > req.demand {
                    achieved = req.demand;
                }
                result.push((req_id, achieved));
            }
        }
        result.sort_by_key(|&(req_id, _)| req_id);
        result
    }

    // Find any path from source to destination using BFS.
    // Returns a vector of edges (u, v) representing the path, if one exists.
    fn find_path(&self, source: i32, destination: i32) -> Option<Vec<(i32, i32)>> {
        let mut parent: HashMap<i32, (i32, i32)> = HashMap::new();
        let mut visited: HashMap<i32, bool> = HashMap::new();
        let mut queue: VecDeque<i32> = VecDeque::new();
        queue.push_back(source);
        visited.insert(source, true);

        while let Some(node) = queue.pop_front() {
            if node == destination {
                break;
            }
            if let Some(neighbors) = self.graph.get(&node) {
                for &(nbr, u, v) in neighbors.iter() {
                    if !visited.get(&nbr).unwrap_or(&false) {
                        visited.insert(nbr, true);
                        parent.insert(nbr, (node, v));
                        queue.push_back(nbr);
                    }
                }
            }
        }

        if !visited.get(&destination).unwrap_or(&false) {
            return None;
        }

        // Reconstruct path from source to destination.
        let mut path: Vec<(i32, i32)> = Vec::new();
        let mut current = destination;
        while current != source {
            if let Some(&(prev, edge_dest)) = parent.get(&current) {
                path.push((prev, current));
                current = prev;
            } else {
                break;
            }
        }
        path.reverse();
        Some(path)
    }
}
