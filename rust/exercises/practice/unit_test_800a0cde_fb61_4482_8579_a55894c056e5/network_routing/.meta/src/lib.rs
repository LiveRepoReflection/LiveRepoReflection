use std::cmp::Ordering;
use std::collections::BinaryHeap;

pub fn network_routing(
    n: usize,
    updates: Vec<(usize, usize, i32)>,
    queries: Vec<(usize, usize, usize)>
) -> Vec<i32> {
    // Build graph with n nodes, each represented by a vector of (neighbor, weight)
    let mut graph: Vec<Vec<(usize, i32)>> = vec![Vec::new(); n];
    
    for &(u, v, w) in &updates {
        if w == -1 {
            // Removal update: remove edge between u and v if exists.
            if let Some(pos) = graph[u].iter().position(|&(nbr, _)| nbr == v) {
                graph[u].remove(pos);
            }
            if let Some(pos) = graph[v].iter().position(|&(nbr, _)| nbr == u) {
                graph[v].remove(pos);
            }
        } else {
            // Update or add: For bidirectional edge, update both sides.
            if let Some(pos) = graph[u].iter().position(|&(nbr, _)| nbr == v) {
                graph[u][pos].1 = w;
            } else {
                graph[u].push((v, w));
            }
            if let Some(pos) = graph[v].iter().position(|&(nbr, _)| nbr == u) {
                graph[v][pos].1 = w;
            } else {
                graph[v].push((u, w));
            }
        }
    }
    
    // Process each query on the final graph state.
    let mut results = Vec::with_capacity(queries.len());
    for (start, end, max_hops) in queries {
        let res = dijkstra_limited(&graph, start, end, max_hops);
        results.push(res);
    }
    results
}

#[derive(Eq, PartialEq)]
struct State {
    cost: i32,
    position: usize,
    hops: usize,
}

// Reverse order so that the BinaryHeap acts as a min-heap.
impl Ord for State {
    fn cmp(&self, other: &Self) -> Ordering {
        other.cost
            .cmp(&self.cost)
            .then_with(|| self.hops.cmp(&other.hops))
            .then_with(|| self.position.cmp(&other.position))
    }
}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

// Dijkstra's algorithm modified to only search paths with at most max_hops edges.
fn dijkstra_limited(
    graph: &Vec<Vec<(usize, i32)>>,
    start: usize,
    end: usize,
    max_hops: usize
) -> i32 {
    if start == end {
        return 0;
    }
    // Create a distance table: dist[node][hops] = minimum cost to reach node with exactly hops edges.
    let mut dist = vec![vec![i32::MAX; max_hops + 1]; graph.len()];
    let mut heap = BinaryHeap::new();
    
    dist[start][0] = 0;
    heap.push(State { cost: 0, position: start, hops: 0 });
    
    while let Some(State { cost, position, hops }) = heap.pop() {
        if position == end {
            return cost;
        }
        if cost > dist[position][hops] {
            continue;
        }
        if hops == max_hops {
            continue;
        }
        for &(neighbor, weight) in &graph[position] {
            let next_hops = hops + 1;
            let next_cost = cost + weight;
            if next_cost < dist[neighbor][next_hops] {
                dist[neighbor][next_hops] = next_cost;
                heap.push(State { cost: next_cost, position: neighbor, hops: next_hops });
            }
        }
    }
    -1
}