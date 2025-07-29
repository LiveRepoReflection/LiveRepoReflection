use std::collections::{BinaryHeap, HashMap};
use std::cmp::Reverse;

#[derive(Clone, Debug)]
pub enum Event {
    BlockPath { src: usize, dst: usize, duration: u32 },
    UnblockPath { src: usize, dst: usize },
    AddPath { src: usize, dst: usize, cost: u32 },
    RemovePath { src: usize, dst: usize },
    NavigationRequest { start: usize, destination: usize, start_time: u32, end_time: u32, result: Option<u32> },
}

#[derive(Clone)]
struct Edge {
    dst: usize,
    cost: u32,
}

pub struct NavigationSystem {
    num_nodes: usize,
    graph: Vec<Vec<Edge>>,
    // For each edge (src, dst), store a block expiry time.
    // The block is effective if the traversal time is less than the expiry.
    blocked: HashMap<(usize, usize), u32>,
}

impl NavigationSystem {
    pub fn new(num_nodes: usize) -> NavigationSystem {
        NavigationSystem {
            num_nodes,
            graph: vec![Vec::new(); num_nodes],
            blocked: HashMap::new(),
        }
    }

    pub fn handle_event(&mut self, event: &mut Event) {
        match event {
            Event::BlockPath { src, dst, duration } => {
                // Set the block expiry time.
                self.blocked.insert((*src, *dst), *duration);
            }
            Event::UnblockPath { src, dst } => {
                self.blocked.remove(&(*src, *dst));
            }
            Event::AddPath { src, dst, cost } => {
                if *src < self.num_nodes && *dst < self.num_nodes {
                    self.graph[*src].push(Edge { dst: *dst, cost: *cost });
                }
            }
            Event::RemovePath { src, dst } => {
                if *src < self.num_nodes {
                    self.graph[*src].retain(|edge| edge.dst != *dst);
                }
                self.blocked.remove(&(*src, *dst));
            }
            Event::NavigationRequest { start, destination, start_time, end_time, result } => {
                let travel_cost = self.find_shortest_path(*start, *destination, *start_time, *end_time);
                *result = travel_cost;
            }
        }
    }

    fn find_shortest_path(&self, start: usize, destination: usize, start_time: u32, end_time: u32) -> Option<u32> {
        // If starting at the destination, cost is 0.
        if start == destination {
            return Some(0);
        }
        // Initialize distances: the time of arrival at each node.
        let mut dist = vec![u32::MAX; self.num_nodes];
        dist[start] = start_time;
        let mut heap = BinaryHeap::new();
        heap.push(Reverse((start_time, start)));

        while let Some(Reverse((current_time, u))) = heap.pop() {
            if current_time != dist[u] {
                continue;
            }
            if u == destination {
                // Return travel cost as arrival time minus start time.
                return Some(current_time - start_time);
            }
            for edge in &self.graph[u] {
                let mut departure_time = current_time;
                if let Some(&block_expiry) = self.blocked.get(&(u, edge.dst)) {
                    // If current time is less than the block expiry, we must wait.
                    if departure_time < block_expiry {
                        departure_time = block_expiry;
                    }
                }
                // Compute arrival time at the neighboring node.
                let arrival_time = departure_time.saturating_add(edge.cost);
                if arrival_time > end_time {
                    continue;
                }
                if arrival_time < dist[edge.dst] {
                    dist[edge.dst] = arrival_time;
                    heap.push(Reverse((arrival_time, edge.dst)));
                }
            }
        }
        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_no_available_path() {
        let mut nav = NavigationSystem::new(3);
        let mut req = Event::NavigationRequest { start: 0, destination: 1, start_time: 0, end_time: 10, result: None };
        nav.handle_event(&mut req);
        if let Event::NavigationRequest { result, .. } = req {
            assert!(result.is_none(), "Expected no valid path, but got {:?}", result);
        } else {
            panic!("Event type mismatch");
        }
    }

    #[test]
    fn test_simple_navigation() {
        let mut nav = NavigationSystem::new(2);
        let mut add_event = Event::AddPath { src: 0, dst: 1, cost: 5 };
        nav.handle_event(&mut add_event);
        
        let mut req = Event::NavigationRequest { start: 0, destination: 1, start_time: 0, end_time: 10, result: None };
        nav.handle_event(&mut req);
        if let Event::NavigationRequest { result, .. } = req {
            assert_eq!(result, Some(5), "Expected path cost 5, but got {:?}", result);
        } else {
            panic!("Event type mismatch");
        }
    }

    #[test]
    fn test_alternative_route_after_block() {
        let mut nav = NavigationSystem::new(3);
        // Setup paths:
        // Path 0->1 cost 2, Path 1->2 cost 2, Direct path 0->2 cost 10.
        let mut add_e1 = Event::AddPath { src: 0, dst: 1, cost: 2 };
        let mut add_e2 = Event::AddPath { src: 1, dst: 2, cost: 2 };
        let mut add_e3 = Event::AddPath { src: 0, dst: 2, cost: 10 };
        nav.handle_event(&mut add_e1);
        nav.handle_event(&mut add_e2);
        nav.handle_event(&mut add_e3);

        // Block the cheaper route edge: block 0->1 for duration 10.
        let mut block_event = Event::BlockPath { src: 0, dst: 1, duration: 10 };
        nav.handle_event(&mut block_event);

        // Navigation request from 0 to 2 with time window [0, 12]:
        let mut req = Event::NavigationRequest { start: 0, destination: 2, start_time: 0, end_time: 12, result: None };
        nav.handle_event(&mut req);
        if let Event::NavigationRequest { result, .. } = req {
            assert_eq!(result, Some(10), "Expected path cost 10 using direct route, but got {:?}", result);
        } else {
            panic!("Event type mismatch");
        }
    }

    #[test]
    fn test_navigation_after_unblock() {
        let mut nav = NavigationSystem::new(3);
        // Setup paths:
        // Path 0->1 cost 2, Path 1->2 cost 2, Direct path 0->2 cost 10.
        let mut add_e1 = Event::AddPath { src: 0, dst: 1, cost: 2 };
        let mut add_e2 = Event::AddPath { src: 1, dst: 2, cost: 2 };
        let mut add_e3 = Event::AddPath { src: 0, dst: 2, cost: 10 };
        nav.handle_event(&mut add_e1);
        nav.handle_event(&mut add_e2);
        nav.handle_event(&mut add_e3);

        // Block the edge 0->1 for duration 10, then immediately unblock it.
        let mut block_event = Event::BlockPath { src: 0, dst: 1, duration: 10 };
        nav.handle_event(&mut block_event);
        let mut unblock_event = Event::UnblockPath { src: 0, dst: 1 };
        nav.handle_event(&mut unblock_event);

        // Navigation request from 0 to 2 with time window [0, 10]:
        let mut req = Event::NavigationRequest { start: 0, destination: 2, start_time: 0, end_time: 10, result: None };
        nav.handle_event(&mut req);
        if let Event::NavigationRequest { result, .. } = req {
            assert_eq!(result, Some(4), "Expected path cost 4 using unblocked route, but got {:?}", result);
        } else {
            panic!("Event type mismatch");
        }
    }

    #[test]
    fn test_remove_path() {
        let mut nav = NavigationSystem::new(3);
        // Setup paths:
        // Path 0->1 cost 3, Path 1->2 cost 3.
        let mut add_e1 = Event::AddPath { src: 0, dst: 1, cost: 3 };
        let mut add_e2 = Event::AddPath { src: 1, dst: 2, cost: 3 };
        nav.handle_event(&mut add_e1);
        nav.handle_event(&mut add_e2);

        // Remove the path 0->1.
        let mut remove_event = Event::RemovePath { src: 0, dst: 1 };
        nav.handle_event(&mut remove_event);

        // Navigation request from 0 to 2 with time window [0, 10]:
        let mut req = Event::NavigationRequest { start: 0, destination: 2, start_time: 0, end_time: 10, result: None };
        nav.handle_event(&mut req);
        if let Event::NavigationRequest { result, .. } = req {
            assert!(result.is_none(), "Expected no valid path after removal, but got {:?}", result);
        } else {
            panic!("Event type mismatch");
        }
    }
}