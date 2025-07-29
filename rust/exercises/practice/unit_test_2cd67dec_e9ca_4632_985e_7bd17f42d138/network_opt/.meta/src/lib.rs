use std::collections::{HashMap, HashSet};
use std::cmp::{min, max};

type ServerId = u32;
type ServerCapacity = u32;
type TrafficAmount = u32;
type LinkCost = u32;

pub fn optimize_network(
    servers: &[(ServerId, ServerCapacity)],
    traffic_demands: &HashMap<(ServerId, ServerId), TrafficAmount>,
    link_costs: &HashMap<(ServerId, ServerId), LinkCost>,
    bandwidth_per_link: u32,
) -> Result<HashSet<(ServerId, ServerId)>, String> {
    // Validate input
    if servers.is_empty() {
        return Err("No servers provided".to_string());
    }

    let server_ids: HashSet<ServerId> = servers.iter().map(|(id, _)| *id).collect();
    let mut server_capacities: HashMap<ServerId, ServerCapacity> = servers.iter().copied().collect();

    // Check traffic demands validity
    for &(src, dst) in traffic_demands.keys() {
        if !server_ids.contains(&src) || !server_ids.contains(&dst) {
            return Err(format!("Invalid server ID in traffic demands: ({}, {})", src, dst));
        }
    }

    // Check link costs validity
    for &(s1, s2) in link_costs.keys() {
        if !server_ids.contains(&s1) || !server_ids.contains(&s2) {
            return Err(format!("Invalid server ID in link costs: ({}, {})", s1, s2));
        }
    }

    // Create a list of all possible links (sorted to avoid duplicates)
    let mut possible_links: Vec<(ServerId, ServerId)> = link_costs
        .keys()
        .map(|&(s1, s2)| if s1 < s2 { (s1, s2) } else { (s2, s1) })
        .collect();
    possible_links.sort_unstable();
    possible_links.dedup();

    // Check if the network can be connected
    if possible_links.len() < servers.len() - 1 {
        return Err("Not enough links to connect all servers".to_string());
    }

    // Calculate total traffic per server
    let mut total_traffic: HashMap<ServerId, TrafficAmount> = HashMap::new();
    for (&(src, dst), &amount) in traffic_demands {
        *total_traffic.entry(src).or_insert(0) += amount;
        *total_traffic.entry(dst).or_insert(0) += amount;
    }

    // Check server capacities
    for (&server, &capacity) in &server_capacities {
        if let Some(&traffic) = total_traffic.get(&server) {
            if traffic > capacity {
                return Err(format!(
                    "Server {} cannot handle traffic demand ({} > {})",
                    server, traffic, capacity
                ));
            }
        }
    }

    // Prim's algorithm for MST (minimum spanning tree) as a baseline
    let mut selected_links = HashSet::new();
    let mut connected_servers = HashSet::new();
    
    // Start with the first server
    if let Some(&(first_server, _)) = servers.first() {
        connected_servers.insert(first_server);
    } else {
        return Err("No servers available".to_string());
    }

    while connected_servers.len() < server_ids.len() {
        let mut min_cost_link = None;
        let mut min_cost = u32::MAX;

        for &(s1, s2) in &possible_links {
            let cost = *link_costs.get(&(s1, s2)).unwrap_or(&u32::MAX);
            let s1_connected = connected_servers.contains(&s1);
            let s2_connected = connected_servers.contains(&s2);

            if (s1_connected && !s2_connected) || (!s1_connected && s2_connected) {
                if cost < min_cost {
                    min_cost = cost;
                    min_cost_link = Some((s1, s2));
                }
            }
        }

        if let Some((s1, s2)) = min_cost_link {
            selected_links.insert((min(s1, s2), max(s1, s2)));
            connected_servers.insert(s1);
            connected_servers.insert(s2);
        } else {
            return Err("Cannot connect all servers with available links".to_string());
        }
    }

    // Verify bandwidth constraints
    let mut link_traffic: HashMap<(ServerId, ServerId), TrafficAmount> = HashMap::new();
    
    for &(src, dst) in traffic_demands.keys() {
        let amount = traffic_demands[&(src, dst)];
        
        // Simple shortest path routing (BFS)
        if let Some(path) = find_path(&selected_links, src, dst) {
            for i in 0..path.len() - 1 {
                let s1 = min(path[i], path[i + 1]);
                let s2 = max(path[i], path[i + 1]);
                *link_traffic.entry((s1, s2)).or_insert(0) += amount;
            }
        } else {
            return Err(format!("No path found between servers {} and {}", src, dst));
        }
    }

    // Check bandwidth constraints
    for (&link, &traffic) in &link_traffic {
        if traffic > bandwidth_per_link {
            return Err(format!(
                "Link between {} and {} exceeds bandwidth ({} > {})",
                link.0, link.1, traffic, bandwidth_per_link
            ));
        }
    }

    Ok(selected_links)
}

fn find_path(
    links: &HashSet<(ServerId, ServerId)>,
    start: ServerId,
    end: ServerId,
) -> Option<Vec<ServerId>> {
    let mut visited = HashSet::new();
    let mut queue = std::collections::VecDeque::new();
    queue.push_back(vec![start]);

    while let Some(path) = queue.pop_front() {
        let last_node = path[path.len() - 1];
        if last_node == end {
            return Some(path);
        }

        if visited.contains(&last_node) {
            continue;
        }
        visited.insert(last_node);

        for &(s1, s2) in links {
            if s1 == last_node {
                let mut new_path = path.clone();
                new_path.push(s2);
                queue.push_back(new_path);
            } else if s2 == last_node {
                let mut new_path = path.clone();
                new_path.push(s1);
                queue.push_back(new_path);
            }
        }
    }

    None
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_find_path() {
        let mut links = HashSet::new();
        links.insert((1, 2));
        links.insert((2, 3));
        links.insert((3, 4));

        assert_eq!(find_path(&links, 1, 4), Some(vec![1, 2, 3, 4]));
        assert_eq!(find_path(&links, 1, 5), None);
    }
}