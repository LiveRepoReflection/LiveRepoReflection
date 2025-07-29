use std::collections::{BinaryHeap, HashSet};
use std::cmp::Ordering;

struct State {
    cost: i32,
    hops: usize,
    position: usize,
}

impl Ord for State {
    fn cmp(&self, other: &Self) -> Ordering {
        // Reverse order to make BinaryHeap a min-heap based on cost first, then hops.
        other.cost.cmp(&self.cost)
            .then_with(|| other.hops.cmp(&self.hops))
    }
}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl PartialEq for State {
    fn eq(&self, other: &Self) -> bool {
        self.cost == other.cost && self.hops == other.hops && self.position == other.position
    }
}

impl Eq for State {}

fn dijkstra(n: usize, graph: &Vec<Vec<(usize, i32)>>, start: usize, end: usize, broken: &HashSet<usize>) -> Option<(Vec<usize>, i32, usize)> {
    let mut dist = vec![i32::MAX; n];
    let mut hops = vec![usize::MAX; n];
    let mut prev = vec![None; n];
    let mut heap = BinaryHeap::new();

    dist[start] = 0;
    hops[start] = 0;
    heap.push(State { cost: 0, hops: 0, position: start });

    while let Some(State { cost, hops: h, position: u }) = heap.pop() {
        if u == end {
            // Early exit since we reached destination.
            break;
        }
        if cost > dist[u] || h > hops[u] {
            continue;
        }
        for &(v, w) in &graph[u] {
            if broken.contains(&v) {
                continue;
            }
            let next_cost = cost + w;
            let next_hops = h + 1;
            if next_cost < dist[v] || (next_cost == dist[v] && next_hops < hops[v]) {
                dist[v] = next_cost;
                hops[v] = next_hops;
                prev[v] = Some(u);
                heap.push(State { cost: next_cost, hops: next_hops, position: v });
            }
        }
    }

    if dist[end] == i32::MAX {
        return None;
    }

    let mut path = Vec::new();
    let mut current = end;
    while current != start {
        path.push(current);
        if let Some(p) = prev[current] {
            current = p;
        } else {
            break;
        }
    }
    path.push(start);
    path.reverse();
    Some((path, dist[end], hops[end]))
}

pub fn find_k_paths(n: usize, edges: Vec<(usize, usize, i32)>, start: usize, end: usize, k: usize, broken_nodes: HashSet<usize>) -> Vec<Vec<usize>> {
    if broken_nodes.contains(&start) || broken_nodes.contains(&end) {
        return Vec::new();
    }

    // Build a mutable undirected graph represented as an adjacency list.
    let mut graph: Vec<Vec<(usize, i32)>> = vec![Vec::new(); n];
    // Insert edges only if both endpoints are not broken.
    for (u, v, w) in edges.iter() {
        if broken_nodes.contains(u) || broken_nodes.contains(v) {
            continue;
        }
        graph[*u].push((*v, *w));
        graph[*v].push((*u, *w));
    }

    let mut found_paths: Vec<(Vec<usize>, i32, usize)> = Vec::new();

    for _ in 0..k {
        if let Some((path, cost, hops)) = dijkstra(n, &graph, start, end, &broken_nodes) {
            found_paths.push((path.clone(), cost, hops));
            // Remove edges used in the found path from the graph to ensure edge-disjointness.
            for i in 0..path.len()-1 {
                let u = path[i];
                let v = path[i+1];
                graph[u].retain(|&(nbr, _)| nbr != v);
                graph[v].retain(|&(nbr, _)| nbr != u);
            }
        } else {
            break;
        }
    }

    // Sort the found paths: first by total decoherence cost (ascending) then by number of hops (ascending).
    found_paths.sort_by(|a, b| {
        a.1.cmp(&b.1).then_with(|| a.2.cmp(&b.2))
    });

    found_paths.into_iter().map(|(path, _, _)| path).collect()
}