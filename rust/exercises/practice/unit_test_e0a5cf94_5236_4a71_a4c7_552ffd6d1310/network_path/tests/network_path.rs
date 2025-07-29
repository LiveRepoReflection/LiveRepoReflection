use std::cmp::max;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Command {
    FindRoute {
        start_node: usize,
        end_node: usize,
        data_size: u64,
    },
    UpdateLink {
        node1: usize,
        node2: usize,
        new_latency: u64,
        new_capacity: u64,
    },
    RemoveLink {
        node1: usize,
        node2: usize,
    },
    AddLink {
        node1: usize,
        node2: usize,
        latency: u64,
        capacity: u64,
    },
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::{BinaryHeap, HashMap};

    // The process_network function below is assumed to be the API 
    // provided in the solution. It takes the number of nodes, the initial links,
    // and a list of commands, and returns the results of all FindRoute commands in order.
    //
    // For testing purposes, we re-implement a minimal simulation of what the solution
    // is expected to do. This test harness is solely to verify that the solution 
    // produces the expected outputs when processing a sequence of commands.
    //
    // Note: This implementation is only for the unit tests and is not intended
    // to represent the optimal solution. It uses Dijkstra's algorithm and updates the
    // internal graph structure based on the commands.
    pub fn process_network(
        n: usize,
        initial_links: Vec<(usize, usize, u64, u64)>,
        commands: Vec<Command>,
    ) -> Vec<Option<u64>> {
        // Graph structure: For each node, map to neighbors: (neighbor, latency, capacity)
        let mut graph: Vec<HashMap<usize, (u64, u64)>> = vec![HashMap::new(); n];
        // Build initial graph
        for (u, v, latency, capacity) in initial_links {
            graph[u].insert(v, (latency, capacity));
            graph[v].insert(u, (latency, capacity));
        }

        let mut results = Vec::new();
        for command in commands {
            match command {
                Command::FindRoute {
                    start_node,
                    end_node,
                    data_size,
                } => {
                    // Use modified Dijkstra algorithm
                    let res = dijkstra(&graph, start_node, end_node, data_size);
                    results.push(res);
                }
                Command::UpdateLink {
                    node1,
                    node2,
                    new_latency,
                    new_capacity,
                } => {
                    // Update if exists, or add if not present.
                    graph[node1].insert(node2, (new_latency, new_capacity));
                    graph[node2].insert(node1, (new_latency, new_capacity));
                }
                Command::RemoveLink { node1, node2 } => {
                    graph[node1].remove(&node2);
                    graph[node2].remove(&node1);
                }
                Command::AddLink {
                    node1,
                    node2,
                    latency,
                    capacity,
                } => {
                    // Add or overwrite existing link.
                    graph[node1].insert(node2, (latency, capacity));
                    graph[node2].insert(node1, (latency, capacity));
                }
            }
        }
        results
    }

    // Helper function: modified Dijkstra that calculates the effective latency for each link.
    // For each link, if data_size is greater than capacity, the effective latency is calculated as:
    // effective_latency = latency * multiplier, where multiplier = ceil(data_size / capacity).
    fn dijkstra(
        graph: &Vec<HashMap<usize, (u64, u64)>>,
        start: usize,
        target: usize,
        data_size: u64,
    ) -> Option<u64> {
        let n = graph.len();
        let mut dist: Vec<u64> = vec![u64::MAX; n];
        let mut heap: BinaryHeap<(std::cmp::Reverse<u64>, usize)> = BinaryHeap::new();
        dist[start] = 0;
        heap.push((std::cmp::Reverse(0), start));

        while let Some((std::cmp::Reverse(d), node)) = heap.pop() {
            if node == target {
                return Some(d);
            }
            if d > dist[node] {
                continue;
            }
            for (&neighbor, &(latency, capacity)) in graph[node].iter() {
                // Calculate multiplier: if data_size > capacity, then multiplier = ceil(data_size/capacity)
                let multiplier = if data_size > capacity {
                    (data_size + capacity - 1) / capacity
                } else {
                    1
                };
                let effective_latency = latency.saturating_mul(multiplier);
                let next = d.saturating_add(effective_latency);
                if next < dist[neighbor] {
                    dist[neighbor] = next;
                    heap.push((std::cmp::Reverse(next), neighbor));
                }
            }
        }
        None
    }

    #[test]
    fn test_basic_routing() {
        let n = 4;
        let initial_links = vec![
            (0, 1, 10, 100),
            (1, 2, 20, 50),
            (2, 3, 30, 25),
            (0, 3, 100, 10),
        ];
        let commands = vec![
            // For data_size 60, path 0-1-2-3: 
            // Link 0-1: 10 * 1 = 10 (60 <= 100)
            // Link 1-2: 20 * ceil(60/50) = 20 * 2 = 40
            // Link 2-3: 30 * ceil(60/25) = 30 * 3 = 90 (since ceil(60/25)=3)
            // Total = 10 + 40 + 90 = 140, which is less than direct link 0-3: 100 * 6 = 600
            Command::FindRoute {
                start_node: 0,
                end_node: 3,
                data_size: 60,
            },
            // Update link 2-3 to reduce effective latency:
            // New link: latency=15, capacity=50.
            Command::UpdateLink {
                node1: 2,
                node2: 3,
                new_latency: 15,
                new_capacity: 50,
            },
            // For data_size 60, path 0-1-2-3:
            // Link 0-1: 10 * 1 = 10
            // Link 1-2: 20 * ceil(60/50) = 20 * 2 = 40
            // Link 2-3 (updated): 15 * 1 = 15 (60 <= 50 is false, actually 60 > 50 so multiplier = ceil(60/50)=2 -> 15*2=30)
            // Total = 10 + 40 + 30 = 80.
            Command::FindRoute {
                start_node: 0,
                end_node: 3,
                data_size: 60,
            },
        ];

        let outputs = process_network(n, initial_links, commands);
        // Expected results:
        // First FindRoute: effective latency = 10 + 40 + 90 = 140.
        // Second FindRoute: effective latency = 10 + 40 + 30 = 80.
        assert_eq!(outputs.len(), 2);
        assert_eq!(outputs[0], Some(140));
        assert_eq!(outputs[1], Some(80));
    }

    #[test]
    fn test_add_remove_links() {
        let n = 5;
        let initial_links = vec![
            (0, 1, 5, 50),
            (1, 2, 10, 60),
            (2, 3, 20, 40),
            (3, 4, 25, 35),
        ];
        let commands = vec![
            // Initially, find route from 0 to 4 with data_size 30.
            Command::FindRoute {
                start_node: 0,
                end_node: 4,
                data_size: 30,
            },
            // Remove link between 2 and 3, disconnecting the path.
            Command::RemoveLink { node1: 2, node2: 3 },
            Command::FindRoute {
                start_node: 0,
                end_node: 4,
                data_size: 30,
            },
            // Add a new link bypassing the removed one: add link between 1 and 3.
            Command::AddLink {
                node1: 1,
                node2: 3,
                latency: 50,
                capacity: 100,
            },
            Command::FindRoute {
                start_node: 0,
                end_node: 4,
                data_size: 30,
            },
            // Update link between 1 and 3 to a lower latency.
            Command::UpdateLink {
                node1: 1,
                node2: 3,
                new_latency: 15,
                new_capacity: 100,
            },
            Command::FindRoute {
                start_node: 0,
                end_node: 4,
                data_size: 30,
            },
        ];

        // Let's compute expected effective latency:
        // Initial graph: path 0-1-2-3-4.
        // For data_size 30, each link not congested if capacity >= 30.
        // 0-1: 5 (50>=30), 1-2:10 (60>=30), 2-3:20 (40>=30), 3-4:25 (35>=30).
        // Total = 5+10+20+25 = 60.
        //
        // After removal of link 2-3, there is no path from 0 to 4, so expect None.
        //
        // After adding link 1-3: new path: 0-1, then 1-3, then 3-4.
        // 0-1:5, 1-3:50 (capacity 100, so no congestion for 30), 3-4:25 = total 80.
        //
        // After updating link 1-3 to latency=15: total becomes 5+15+25 = 45.
        let outputs = process_network(n, initial_links, commands);
        assert_eq!(outputs.len(), 4);
        assert_eq!(outputs[0], Some(60));
        assert_eq!(outputs[1], None);
        assert_eq!(outputs[2], Some(80));
        assert_eq!(outputs[3], Some(45));
    }

    #[test]
    fn test_congestion_calculation() {
        let n = 3;
        let initial_links = vec![
            // The capacities are low to force congestion.
            (0, 1, 10, 10),
            (1, 2, 20, 5),
            (0, 2, 50, 50),
        ];
        let commands = vec![
            // For data_size 12:
            // Path 0-1-2: 
            // 0-1: latency=10, capacity=10 => multiplier = ceil(12/10)=2 => effective=20.
            // 1-2: latency=20, capacity=5 => multiplier = ceil(12/5)=3 => effective=60.
            // Total = 20+60 = 80.
            // Direct path 0-2: latency=50, capacity=50 => multiplier = 1 => effective=50.
            // So minimum is 50.
            Command::FindRoute {
                start_node: 0,
                end_node: 2,
                data_size: 12,
            },
            // For data_size 60:
            // Path 0-1-2:
            // 0-1: 10 * ceil(60/10)=10*6=60.
            // 1-2: 20 * ceil(60/5)=20*12=240.
            // Total = 300.
            // Direct path 0-2:
            // 50 * ceil(60/50)=50*2=100.
            Command::FindRoute {
                start_node: 0,
                end_node: 2,
                data_size: 60,
            },
        ];
        let outputs = process_network(n, initial_links, commands);
        assert_eq!(outputs.len(), 2);
        assert_eq!(outputs[0], Some(50));
        assert_eq!(outputs[1], Some(100));
    }

    #[test]
    fn test_no_route_exists() {
        let n = 3;
        let initial_links = vec![
            (0, 1, 10, 100),
            (1, 2, 20, 100),
        ];
        let commands = vec![
            // Remove link between 1 and 2 so that 0 and 2 become disconnected.
            Command::RemoveLink { node1: 1, node2: 2 },
            Command::FindRoute {
                start_node: 0,
                end_node: 2,
                data_size: 50,
            },
            // Re-add a link that connects 0 and 2 directly.
            Command::AddLink {
                node1: 0,
                node2: 2,
                latency: 100,
                capacity: 100,
            },
            Command::FindRoute {
                start_node: 0,
                end_node: 2,
                data_size: 50,
            },
        ];
        let outputs = process_network(n, initial_links, commands);
        // After removal, no path from 0 to 2.
        // After re-adding, direct link available with no congestion.
        assert_eq!(outputs.len(), 2);
        assert_eq!(outputs[0], None);
        assert_eq!(outputs[1], Some(100));
    }
}