use std::cmp::Ordering;
use std::collections::BinaryHeap;

#[derive(Clone)]
pub struct Edge {
    pub from: usize,   // Index of the origin warehouse
    pub to: usize,     // Index of the destination warehouse
    pub cost: u32,     // Cost per unit
    pub capacity: u32, // Maximum units that can be transported
    pub time: u32,     // Transit time in hours
}

#[derive(Clone)]
pub struct DeliveryRequest {
    pub origin: usize,      // Index of the origin warehouse
    pub destination: usize, // Index of the destination warehouse
    pub quantity: u32,      // Number of units to deliver
    pub deadline: u32,      // Deadline in hours
}

#[derive(Clone)]
pub struct Network {
    pub num_warehouses: usize,
    pub edges: Vec<Edge>,
    pub requests: Vec<DeliveryRequest>,
}

#[derive(Copy, Clone, Eq, PartialEq)]
struct State {
    cost: u64,
    pos: usize,
}

impl Ord for State {
    fn cmp(&self, other: &Self) -> Ordering {
        // Reverse order to make a min-heap.
        other.cost.cmp(&self.cost).then_with(|| self.pos.cmp(&other.pos))
    }
}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

const INF: u64 = 1 << 60;

// Dijkstra based on cost for min-cost path finding. We use a closure "is_allowed" to filter edges.
fn dijkstra_shortest(
    n: usize,
    start: usize,
    is_allowed: &dyn Fn(&Edge) -> bool,
    global_edges: &Vec<Edge>,
) -> (Vec<u64>, Vec<Option<(usize, usize)>>) {
    let mut dist = vec![INF; n];
    let mut prev = vec![None; n];
    let mut heap = BinaryHeap::new();

    dist[start] = 0;
    heap.push(State { cost: 0, pos: start });

    while let Some(State { cost, pos }) = heap.pop() {
        if cost > dist[pos] {
            continue;
        }
        // relax all outgoing edges from pos
        for (i, edge) in global_edges.iter().enumerate() {
            if edge.from == pos && edge.capacity > 0 && is_allowed(edge) {
                let next = edge.to;
                let next_cost = cost + edge.cost as u64;
                if next_cost < dist[next] {
                    dist[next] = next_cost;
                    prev[next] = Some((pos, i));
                    heap.push(State { cost: next_cost, pos: next });
                }
            }
        }
    }
    (dist, prev)
}

// Dijkstra based on transit time for computing earliest arrival times.
fn dijkstra_transit(n: usize, start: usize, edges: &Vec<Edge>, reverse: bool) -> Vec<u64> {
    let mut dist = vec![u64::MAX; n];
    let mut heap = BinaryHeap::new();

    dist[start] = 0;
    heap.push(State { cost: 0, pos: start });

    while let Some(State { cost, pos }) = heap.pop() {
        if cost > dist[pos] {
            continue;
        }
        for edge in edges.iter() {
            if reverse {
                // traversing in reverse: consider edge.to -> edge.from
                if edge.to == pos {
                    let next = edge.from;
                    let next_cost = cost + edge.time as u64;
                    if next_cost < dist[next] {
                        dist[next] = next_cost;
                        heap.push(State { cost: next_cost, pos: next });
                    }
                }
            } else {
                if edge.from == pos {
                    let next = edge.to;
                    let next_cost = cost + edge.time as u64;
                    if next_cost < dist[next] {
                        dist[next] = next_cost;
                        heap.push(State { cost: next_cost, pos: next });
                    }
                }
            }
        }
    }
    dist
}

pub fn optimize_logistics(network: &Network) -> Option<u64> {
    let n = network.num_warehouses;
    if n == 0 {
        return None;
    }
    // Clone global_edges to maintain mutable capacities across requests.
    let mut global_edges = network.edges.clone();
    let mut total_cost: u64 = 0;

    // Process requests sorted by deadline to better respect time constraints.
    let mut requests = network.requests.clone();
    requests.sort_by_key(|r| r.deadline);

    for request in requests.iter() {
        if request.origin >= n || request.destination >= n {
            return None;
        }
        if request.quantity == 0 {
            continue;
        }
        // Compute earliest arrival times from the origin using transit times.
        let d_from = dijkstra_transit(n, request.origin, &global_edges, false);
        // Compute earliest arrival times to the destination in the reverse graph.
        let d_to = dijkstra_transit(n, request.destination, &global_edges, true);

        // If the quickest path (ignoring capacities) exceeds the deadline, it's impossible.
        if d_from[request.destination] == u64::MAX || d_from[request.destination] > request.deadline as u64 {
            return None;
        }

        // Closure to determine if an edge is allowed for this request.
        let allowed = |edge: &Edge| -> bool {
            if d_from[edge.from] == u64::MAX || d_to[edge.to] == u64::MAX {
                return false;
            }
            // Ensure that using this edge can be part of a path that meets the deadline.
            d_from[edge.from] + edge.time as u64 + d_to[edge.to] <= request.deadline as u64
        };

        let mut remaining = request.quantity;
        // Use successive shortest path algorithm to send the required units.
        while remaining > 0 {
            let (dist, prev) = dijkstra_shortest(n, request.origin, &allowed, &global_edges);
            if dist[request.destination] == INF {
                return None;
            }
            // Reconstruct the path from origin to destination.
            let mut path_edges = Vec::new();
            let mut cur = request.destination;
            while cur != request.origin {
                if let Some((prev_node, edge_index)) = prev[cur] {
                    path_edges.push(edge_index);
                    cur = prev_node;
                } else {
                    break;
                }
            }
            if cur != request.origin {
                return None;
            }
            path_edges.reverse();
            // Determine the maximum flow that can be sent along the found path.
            let mut flow = remaining;
            for &ei in path_edges.iter() {
                if global_edges[ei].capacity < flow {
                    flow = global_edges[ei].capacity;
                }
            }
            if flow == 0 {
                return None;
            }
            // Accumulate cost along the path and update capacities.
            let mut path_cost: u64 = 0;
            for &ei in path_edges.iter() {
                path_cost += global_edges[ei].cost as u64;
                global_edges[ei].capacity -= flow;
            }
            total_cost += flow as u64 * path_cost;
            remaining -= flow;
        }
    }
    Some(total_cost)
}