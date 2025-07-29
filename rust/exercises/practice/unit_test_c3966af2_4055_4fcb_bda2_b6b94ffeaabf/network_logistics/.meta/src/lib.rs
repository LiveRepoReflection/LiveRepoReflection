use std::collections::{HashMap, BinaryHeap};
use std::cmp::Ordering;

pub struct Warehouse {
    pub id: usize,
    pub x: i32,
    pub y: i32,
    pub capacity: u32,
}

pub struct Customer {
    pub id: usize,
    pub x: i32,
    pub y: i32,
    pub demand: u32,
}

pub struct Route {
    pub from: usize,
    pub to: usize,
    pub cost: f64,
}

#[derive(Clone)]
struct Edge {
    to: usize,
    rev: usize,
    cap: u32,
    cost: f64,
    initial_cap: u32,
    orig: bool,
}

struct State {
    cost: f64,
    position: usize,
}

impl PartialEq for State {
    fn eq(&self, other: &Self) -> bool {
        self.cost.eq(&other.cost)
    }
}

impl Eq for State {}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        // Reverse order for min-heap
        other.cost.partial_cmp(&self.cost)
    }
}

impl Ord for State {
    fn cmp(&self, other: &Self) -> Ordering {
        // Reverse order for min-heap
        other.cost.partial_cmp(&self.cost).unwrap_or(Ordering::Equal)
    }
}

const INF: f64 = 1e18;

pub fn optimize_network(
    warehouses: &Vec<Warehouse>,
    customers: &Vec<Customer>,
    routes: &Vec<Route>,
    disruption_prob: f64,
    simulations: u32,
) -> Result<(Vec<(usize, usize, u32)>, f64, f64), String> {
    // Build set of all node ids from warehouses, customers, and routes.
    let mut node_set = std::collections::HashSet::new();
    for w in warehouses {
        node_set.insert(w.id);
    }
    for c in customers {
        node_set.insert(c.id);
    }
    for r in routes {
        node_set.insert(r.from);
        node_set.insert(r.to);
    }
    // Create mapping from node id to index.
    let mut node_ids: Vec<usize> = node_set.into_iter().collect();
    node_ids.sort();
    let n = node_ids.len();
    let mut id_to_index: HashMap<usize, usize> = HashMap::new();
    for (i, id) in node_ids.iter().enumerate() {
        id_to_index.insert(*id, i);
    }
    // Total demand from customers.
    let total_demand: u32 = customers.iter().map(|c| c.demand).sum();
    let total_supply: u32 = warehouses.iter().map(|w| w.capacity).sum();
    if total_demand > total_supply {
        return Err("Total demand exceeds available warehouse capacity.".to_string());
    }
    // Define super source and super sink.
    let s = n;
    let t = n + 1;
    let total_nodes = n + 2;

    // Build graph.
    let mut graph = vec![vec![]; total_nodes];
    // Function to add edge.
    fn add_edge(
        graph: &mut Vec<Vec<Edge>>,
        from: usize,
        to: usize,
        cap: u32,
        cost: f64,
        is_original: bool,
    ) {
        let from_len = graph[from].len();
        let to_len = graph[to].len();
        graph[from].push(Edge {
            to,
            rev: to_len,
            cap,
            cost,
            initial_cap: cap,
            orig: is_original,
        });
        graph[to].push(Edge {
            to: from,
            rev: from_len,
            cap: 0,
            cost: -cost,
            initial_cap: 0,
            orig: false,
        });
    }

    // Super source to warehouses.
    for w in warehouses {
        if let Some(&u) = id_to_index.get(&w.id) {
            add_edge(&mut graph, s, u, w.capacity, 0.0, false);
        }
    }
    // Customers to super sink.
    for c in customers {
        if let Some(&u) = id_to_index.get(&c.id) {
            add_edge(&mut graph, u, t, c.demand, 0.0, false);
        }
    }
    // Add routes (bidirectional are provided as separate entries).
    // Use a large capacity (use total_supply as an upper bound).
    let large_cap = total_supply;
    for r in routes {
        if let (Some(&u), Some(&v)) = (id_to_index.get(&r.from), id_to_index.get(&r.to)) {
            add_edge(&mut graph, u, v, large_cap, r.cost, true);
        }
    }

    // Run min cost flow on the constructed graph.
    let (flow, cost) = match min_cost_flow(s, t, total_demand, &mut graph) {
        Some(res) => res,
        None => return Err("Could not satisfy all customer demands.".to_string()),
    };
    if flow < total_demand {
        return Err("Could not satisfy all customer demands.".to_string());
    }

    // Extract flows on original route edges.
    let mut optimal_flow = Vec::new();
    for u in 0..n {
        for edge in &graph[u] {
            if edge.orig {
                // Calculate flow used on this edge.
                let used = edge.initial_cap.saturating_sub(edge.cap);
                if used > 0 {
                    let from_id = node_ids[u];
                    let to_id = node_ids[edge.to];
                    optimal_flow.push((from_id, to_id, used));
                }
            }
        }
    }

    // Compute resilience score by simulating disruptions.
    let mut total_ratio = 0.0;
    let mut rng = SimpleRng::new(123456789);
    for _ in 0..simulations {
        // Build modified graph for simulation.
        let mut sim_graph = vec![vec![]; total_nodes];
        // Super source to warehouses.
        for w in warehouses {
            if let Some(&u) = id_to_index.get(&w.id) {
                add_edge(&mut sim_graph, s, u, w.capacity, 0.0, false);
            }
        }
        // Customers to super sink.
        for c in customers {
            if let Some(&u) = id_to_index.get(&c.id) {
                add_edge(&mut sim_graph, u, t, c.demand, 0.0, false);
            }
        }
        // Add routes with disruptions.
        for r in routes {
            if let (Some(&u), Some(&v)) = (id_to_index.get(&r.from), id_to_index.get(&r.to)) {
                // Simulate disruption: if random value is less than disruption_prob, skip this edge.
                if rng.next_f64() < disruption_prob {
                    continue;
                }
                add_edge(&mut sim_graph, u, v, large_cap, r.cost, false);
            }
        }
        let (sim_flow, _) = match min_cost_flow(s, t, total_demand, &mut sim_graph) {
            Some(res) => res,
            None => (0, 0.0),
        };
        let ratio = sim_flow as f64 / total_demand as f64;
        total_ratio += ratio;
    }
    let resilience_score = total_ratio / simulations as f64;

    Ok((optimal_flow, cost, resilience_score))
}

// Implementation of Min Cost Flow algorithm using Dijkstra with potentials.
fn min_cost_flow(s: usize, t: usize, mut f: u32, graph: &mut Vec<Vec<Edge>>) -> Option<(u32, f64)> {
    let n = graph.len();
    let mut prev_v = vec![0usize; n];
    let mut prev_e = vec![0usize; n];
    let mut dist = vec![0.0; n];
    let mut potential = vec![0.0; n];
    let mut flow = 0;
    let mut cost = 0.0;

    while f > 0 {
        // Dijkstra from s.
        for i in 0..n {
            dist[i] = INF;
        }
        let mut heap = BinaryHeap::new();
        dist[s] = 0.0;
        heap.push(State { cost: 0.0, position: s });
        while let Some(State { cost: d, position: v }) = heap.pop() {
            if dist[v] < d {
                continue;
            }
            for (i, edge) in graph[v].iter().enumerate() {
                if edge.cap > 0 {
                    let next_cost = d + edge.cost + potential[v] - potential[edge.to];
                    if dist[edge.to] > next_cost {
                        dist[edge.to] = next_cost;
                        prev_v[edge.to] = v;
                        prev_e[edge.to] = i;
                        heap.push(State { cost: next_cost, position: edge.to });
                    }
                }
            }
        }
        if dist[t] == INF {
            return None;
        }
        for v in 0..n {
            if dist[v] < INF {
                potential[v] += dist[v];
            }
        }
        let mut add_flow = f;
        let mut v = t;
        while v != s {
            let pv = prev_v[v];
            let pe = prev_e[v];
            add_flow = add_flow.min(graph[pv][pe].cap);
            v = pv;
        }
        f -= add_flow;
        flow += add_flow;
        cost += add_flow as f64 * potential[t];
        let mut v = t;
        while v != s {
            let pv = prev_v[v];
            let pe = prev_e[v];
            graph[pv][pe].cap -= add_flow;
            let rev = graph[pv][pe].rev;
            graph[v][rev].cap += add_flow;
            v = pv;
        }
    }
    Some((flow, cost))
}

// A simple xorshift RNG implementation.
struct SimpleRng {
    state: u64,
}

impl SimpleRng {
    fn new(seed: u64) -> Self {
        SimpleRng { state: seed }
    }

    fn next_u32(&mut self) -> u32 {
        // Xorshift32 algorithm variant.
        let mut x = self.state as u32;
        x ^= x << 13;
        x ^= x >> 17;
        x ^= x << 5;
        self.state = x as u64;
        x
    }

    fn next_f64(&mut self) -> f64 {
        let x = self.next_u32();
        (x as f64) / (u32::MAX as f64 + 1.0)
    }
}