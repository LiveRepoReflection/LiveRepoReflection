use std::collections::{HashSet, VecDeque};

#[derive(Debug)]
pub enum Operation {
    Event(usize, usize, bool),
    Request(usize, usize, u32),
}

pub fn process_operations(initial_capacities: Vec<u32>, ops: Vec<Operation>) -> Vec<u32> {
    let n = initial_capacities.len();
    let mut graph: Vec<HashSet<usize>> = vec![HashSet::new(); n];
    let mut results = Vec::new();

    for op in ops {
        match op {
            Operation::Event(a, b, is_connect) => {
                // Validate node indices and ignore self-loop events.
                if a < n && b < n && a != b {
                    if is_connect {
                        graph[a].insert(b);
                        graph[b].insert(a);
                    } else {
                        graph[a].remove(&b);
                        graph[b].remove(&a);
                    }
                }
            }
            Operation::Request(source, target, amount) => {
                // For invalid node indices, or no path, return 0.
                if source >= n || target >= n {
                    results.push(0);
                    continue;
                }
                if source == target {
                    results.push(amount);
                    continue;
                }
                // We will use a modified BFS to find the shortest path from source to target.
                // Among all shortest paths, we pick the one with the maximum bottleneck.
                let mut visited: Vec<Option<(usize, u32)>> = vec![None; n];
                let mut queue = VecDeque::new();
                // Start from source with distance 0 and an initial bottleneck value of u32::MAX.
                visited[source] = Some((0, u32::MAX));
                queue.push_back((source, 0, u32::MAX));

                let mut best_bottleneck: Option<u32> = None;
                let mut best_level: Option<usize> = None;

                while let Some((current, level, curr_bottleneck)) = queue.pop_front() {
                    // Once we have reached the target at a certain level,
                    // we do not process nodes at deeper levels.
                    if let Some(t_level) = best_level {
                        if level > t_level {
                            break;
                        }
                    }
                    for &neighbor in &graph[current] {
                        if neighbor >= n {
                            continue;
                        }
                        let new_level = level + 1;
                        // Compute the new bottleneck for this path.
                        // The capacity constraint applies only to intermediate nodes,
                        // not to the source or target.
                        let new_bottleneck = if current == source {
                            if neighbor == target {
                                u32::MAX
                            } else {
                                initial_capacities[neighbor]
                            }
                        } else {
                            if neighbor == target {
                                curr_bottleneck
                            } else {
                                std::cmp::min(curr_bottleneck, initial_capacities[neighbor])
                            }
                        };

                        if neighbor == target {
                            if best_level.is_none() || new_level < best_level.unwrap() {
                                best_level = Some(new_level);
                                best_bottleneck = Some(new_bottleneck);
                            } else if let Some(b) = best_bottleneck {
                                if new_level == best_level.unwrap() && new_bottleneck > b {
                                    best_bottleneck = Some(new_bottleneck);
                                }
                            }
                            continue;
                        }
                        if let Some((prev_level, prev_bottleneck)) = visited[neighbor] {
                            if new_level < prev_level || (new_level == prev_level && new_bottleneck > prev_bottleneck) {
                                visited[neighbor] = Some((new_level, new_bottleneck));
                                queue.push_back((neighbor, new_level, new_bottleneck));
                            }
                        } else {
                            visited[neighbor] = Some((new_level, new_bottleneck));
                            queue.push_back((neighbor, new_level, new_bottleneck));
                        }
                    }
                }
                if let Some(b) = best_bottleneck {
                    let transfer = std::cmp::min(amount, b);
                    results.push(transfer);
                } else {
                    results.push(0);
                }
            }
        }
    }

    results
}