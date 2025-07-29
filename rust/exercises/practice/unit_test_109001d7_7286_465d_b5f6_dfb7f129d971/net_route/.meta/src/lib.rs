use std::cmp::Ordering;
use std::collections::BinaryHeap;

const INF: i64 = 1_000_000_000;

#[derive(Clone)]
struct Edge {
    to: usize,
    cap: i64,
    cost: i64,
    rev: usize,
}

pub struct MinCostFlow {
    graph: Vec<Vec<Edge>>,
    n: usize,
}

impl MinCostFlow {
    pub fn new(n: usize) -> Self {
        Self {
            graph: vec![Vec::new(); n],
            n,
        }
    }

    pub fn add_edge(&mut self, from: usize, to: usize, cap: i64, cost: i64) {
        let from_rev = self.graph[to].len();
        let to_rev = self.graph[from].len();
        self.graph[from].push(Edge {
            to,
            cap,
            cost,
            rev: from_rev,
        });
        self.graph[to].push(Edge {
            to: from,
            cap: 0,
            cost: -cost,
            rev: to_rev,
        });
    }

    // Returns (flow, cost)
    pub fn min_cost_flow(&mut self, s: usize, t: usize, mut f: i64) -> Option<i64> {
        let n = self.n;
        let mut res = 0;
        let mut h = vec![0; n]; // potential
        let mut dist = vec![0; n];
        let mut prev_v = vec![0; n];
        let mut prev_e = vec![0; n];

        while f > 0 {
            // Use Dijkstra to find shortest path from s to t
            for i in 0..n {
                dist[i] = INF;
            }
            dist[s] = 0;
            let mut heap = BinaryHeap::new();
            heap.push(State { cost: 0, position: s });
            while let Some(State { cost, position }) = heap.pop() {
                let cost = -cost;
                if dist[position] < cost {
                    continue;
                }
                for (i, edge) in self.graph[position].iter().enumerate() {
                    if edge.cap > 0 && dist[edge.to] > dist[position] + edge.cost + h[position] - h[edge.to] {
                        dist[edge.to] = dist[position] + edge.cost + h[position] - h[edge.to];
                        prev_v[edge.to] = position;
                        prev_e[edge.to] = i;
                        heap.push(State { cost: -dist[edge.to], position: edge.to });
                    }
                }
            }
            if dist[t] == INF {
                return None;
            }
            for v in 0..n {
                if dist[v] < INF {
                    h[v] += dist[v];
                }
            }
            let mut d = f;
            let mut v = t;
            while v != s {
                let pv = prev_v[v];
                let pe = prev_e[v];
                d = d.min(self.graph[pv][pe].cap);
                v = pv;
            }
            f -= d;
            res += d * h[t];
            let mut v = t;
            while v != s {
                let pv = prev_v[v];
                let pe = prev_e[v];
                // Reduce capacity along edge, increase capacity in reverse edge
                self.graph[pv][pe].cap -= d;
                let rev = self.graph[pv][pe].rev;
                self.graph[v][rev].cap += d;
                v = pv;
            }
        }
        Some(res)
    }
}

struct State {
    cost: i64,
    position: usize,
}

impl Eq for State {}

impl PartialEq for State {
    fn eq(&self, other: &Self) -> bool {
        self.cost == other.cost && self.position == other.position
    }
}

impl Ord for State {
    fn cmp(&self, other: &Self) -> Ordering {
        self.cost.cmp(&other.cost)
    }
}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

fn to_i64(v: usize) -> i64 {
    v as i64
}

/// optimal_route computes the minimum total cost to route all packets in the network.
/// 
/// Parameters:
/// - n: number of nodes in the original network.
/// - edges: list of tuples (u, v, w) representing a bidirectional edge with cost w.
/// - capacities: vector where capacities[i] is the processing capacity of node i.
/// - packets: list of tuples (source, destination, packet_size, packet_priority).
///
/// Returns:
/// - Some(minimum_cost) if all packets can be routed, None otherwise.
pub fn optimal_route(
    n: usize,
    edges: Vec<(usize, usize, u64)>,
    capacities: Vec<u64>,
    packets: Vec<(usize, usize, u64, u64)>,
) -> Option<u64> {
    // Total number of nodes in our flow network:
    // For each original node i, split into i_in and i_out.
    // Also add super source S and super sink T.
    let total_nodes = 2 * n + 2;
    let s = 2 * n;
    let t = 2 * n + 1;
    let mut mcf = MinCostFlow::new(total_nodes);

    // For each original node, add edge from i_in to i_out with capacity = node capacity.
    for i in 0..n {
        mcf.add_edge(i, i + n, capacities[i] as i64, 0);
    }

    // For each bidirectional edge, add edges from u_out to v_in and v_out to u_in.
    // Capacity on these edges can be large (set to sum of all packet sizes).
    let mut total_packet_size = 0;
    for &(_, _, p, _) in packets.iter() {
        total_packet_size += p;
    }
    let edge_cap = total_packet_size as i64;
    for &(u, v, w) in edges.iter() {
        // u_out -> v_in
        mcf.add_edge(u + n, v, edge_cap, w as i64);
        // v_out -> u_in
        mcf.add_edge(v + n, u, edge_cap, w as i64);
    }

    // Add edges from super source s to each packet's source_in and from packet's destination_out to sink t.
    let mut demand = 0;
    // We need sum of all packet flows.
    for &(src, dst, size, _priority) in packets.iter() {
        let packet_size = size as i64;
        demand += packet_size;
        // S -> src_in; src_in is node src.
        mcf.add_edge(s, src, packet_size, 0);
        // dst_out -> T; dst_out is node dst + n.
        mcf.add_edge(dst + n, t, packet_size, 0);
    }

    // Compute min cost flow from s to t.
    let cost = mcf.min_cost_flow(s, t, demand)?;
    Some(cost as u64)
}