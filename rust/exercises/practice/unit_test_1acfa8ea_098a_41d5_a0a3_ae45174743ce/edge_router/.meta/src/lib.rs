use std::collections::VecDeque;

pub fn deploy_edge_routers(
    num_users: usize,
    edges: Vec<(usize, usize)>,
    influence_scores: Vec<usize>,
    hosting_costs: Vec<usize>,
    k: usize,
) -> Vec<usize> {
    // Build the adjacency list for the graph.
    let mut graph: Vec<Vec<usize>> = vec![Vec::new(); num_users];
    for (u, v) in edges.iter() {
        graph[*u].push(*v);
        graph[*v].push(*u);
    }

    // current_distances[u]: The shortest distance from node u to any selected router.
    // None means no router has been reached yet (treat as infinity).
    let mut current_distances: Vec<Option<usize>> = vec![None; num_users];
    let mut routers: Vec<usize> = Vec::new();
    let mut selected = vec![false; num_users];

    // Greedy iterative selection of routers.
    for _ in 0..k {
        let mut best_candidate = None;
        let mut best_gain = std::f64::MIN;
        // Evaluate each node that is not already chosen.
        for candidate in 0..num_users {
            if selected[candidate] {
                continue;
            }
            let gain = evaluate_gain(
                candidate,
                &current_distances,
                &graph,
                &influence_scores,
                hosting_costs[candidate],
            );
            if gain > best_gain {
                best_gain = gain;
                best_candidate = Some(candidate);
            }
        }
        // If no candidate is found (should not happen as we iterate over num_users),
        // break out of the loop to avoid infinite loop.
        let candidate = match best_candidate {
            Some(c) => c,
            None => break,
        };
        routers.push(candidate);
        selected[candidate] = true;
        update_distances(candidate, &mut current_distances, &graph);
    }
    routers
}

fn evaluate_gain(
    candidate: usize,
    current_distances: &Vec<Option<usize>>,
    graph: &Vec<Vec<usize>>,
    influence_scores: &Vec<usize>,
    hosting_cost: usize,
) -> f64 {
    let n = current_distances.len();
    let mut candidate_distance: Vec<Option<usize>> = vec![None; n];
    let mut queue: VecDeque<usize> = VecDeque::new();
    candidate_distance[candidate] = Some(0);
    queue.push_back(candidate);
    let mut total_gain = 0.0;
    while let Some(u) = queue.pop_front() {
        let d = candidate_distance[u].unwrap();
        let old = current_distances[u];
        let old_val = match old {
            Some(old_d) => 1.0 / ((old_d + 1) as f64),
            None => 0.0,
        };
        let new_val = 1.0 / ((d + 1) as f64);
        if new_val > old_val {
            total_gain += (influence_scores[u] as f64) * (new_val - old_val);
        }
        for &nbr in &graph[u] {
            let nd = d + 1;
            if candidate_distance[nbr].is_none() {
                candidate_distance[nbr] = Some(nd);
                queue.push_back(nbr);
            }
        }
    }
    total_gain - (hosting_cost as f64)
}

fn update_distances(candidate: usize, current_distances: &mut Vec<Option<usize>>, graph: &Vec<Vec<usize>>) {
    let n = current_distances.len();
    let mut candidate_distance: Vec<Option<usize>> = vec![None; n];
    let mut queue: VecDeque<usize> = VecDeque::new();
    candidate_distance[candidate] = Some(0);
    queue.push_back(candidate);
    while let Some(u) = queue.pop_front() {
        let d = candidate_distance[u].unwrap();
        if current_distances[u].is_none() || d < current_distances[u].unwrap() {
            current_distances[u] = Some(d);
        }
        for &nbr in &graph[u] {
            if candidate_distance[nbr].is_none() {
                candidate_distance[nbr] = Some(d + 1);
                queue.push_back(nbr);
            }
        }
    }
}