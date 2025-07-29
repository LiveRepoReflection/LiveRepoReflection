use std::collections::{HashMap, HashSet, VecDeque};

pub fn find_paths(
    nodes: &HashMap<u64, Vec<(u64, u64)>>,
    start_user: u64,
    end_user: u64,
    path_length: u32,
) -> Vec<Vec<u64>> {
    if path_length == 0 {
        return if start_user == end_user {
            vec![vec![start_user]]
        } else {
            vec![]
        };
    }

    // Build adjacency list from all nodes
    let mut adj_list: HashMap<u64, Vec<u64>> = HashMap::new();
    for edges in nodes.values() {
        for &(u, v) in edges {
            adj_list.entry(u).or_default().push(v);
        }
    }

    let mut paths = Vec::new();
    let mut queue = VecDeque::new();
    queue.push_back((start_user, vec![start_user]));

    while let Some((current_user, current_path)) = queue.pop_front() {
        if current_path.len() - 1 == path_length as usize {
            if current_user == end_user {
                paths.push(current_path);
            }
            continue;
        }

        if let Some(neighbors) = adj_list.get(&current_user) {
            for &neighbor in neighbors {
                let mut new_path = current_path.clone();
                new_path.push(neighbor);
                queue.push_back((neighbor, new_path));
            }
        }
    }

    paths
}