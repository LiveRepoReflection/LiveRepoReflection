use std::cmp::min;
use std::collections::VecDeque;

#[derive(Clone, Debug)]
pub struct Warehouse {
    pub id: i32,
    pub supply: i32,
}

#[derive(Clone, Debug)]
pub struct DistributionCenter {
    pub id: i32,
    pub demand: i32,
    pub time_window: (i32, i32), // (start_time, end_time)
}

#[derive(Clone, Debug)]
pub struct Edge {
    pub from: i32,
    pub to: i32,
    pub capacity: i32,
    pub cost: i32,
    pub delay: i32,
}

#[derive(Clone, Debug)]
pub struct Problem {
    pub warehouses: Vec<Warehouse>,
    pub distribution_centers: Vec<DistributionCenter>,
    pub edges: Vec<Edge>,
    pub truck_limit: i32,
}

#[derive(Debug, PartialEq, Eq)]
pub struct FlowEdge {
    pub from: i32,
    pub to: i32,
    pub flow: i32,
}

#[derive(Debug, PartialEq, Eq)]
pub struct FlowResult {
    pub flows: Vec<FlowEdge>,
    pub total_cost: i32,
}

// Struct for internal use in min cost flow.
#[derive(Clone, Debug)]
struct MCEdge {
    to: usize,
    cap: i32,
    cost: i32,
    rev: usize,
    // Only true for edges that originate from the original problem definition.
    is_original: bool,
    // The original endpoints for this edge (if is_original is true)
    orig_from: i32,
    orig_to: i32,
    initial_cap: i32,
}

pub fn optimize_routes(problem: Problem) -> Result<FlowResult, String> {
    // Build the set of nodes: use the maximum id among warehouses and distribution centers and edges.
    // We'll assume node ids are non-negative.
    let mut max_id = -1;
    for w in &problem.warehouses {
        if w.id > max_id {
            max_id = w.id;
        }
    }
    for d in &problem.distribution_centers {
        if d.id > max_id {
            max_id = d.id;
        }
    }
    for e in &problem.edges {
        if e.from > max_id {
            max_id = e.from;
        }
        if e.to > max_id {
            max_id = e.to;
        }
    }
    // Create node count for original graph nodes.
    let num_nodes = (max_id + 1) as usize;

    // Before constructing min cost flow graph, check time window feasibility.
    // For each distribution center, calculate minimal delay from any warehouse.
    // We build a graph (adjacency list) for delays.
    let mut delay_graph: Vec<Vec<(usize, i32)>> = vec![Vec::new(); num_nodes];
    for e in &problem.edges {
        let u = e.from as usize;
        let v = e.to as usize;
        delay_graph[u].push((v, e.delay));
    }
    // For each distribution center, perform multi-source shortest path from all warehouses.
    for dc in &problem.distribution_centers {
        let dest = dc.id as usize;
        // Initialize distances as infinity.
        let mut dist = vec![i32::MAX; num_nodes];
        let mut dq = VecDeque::new();
        // Push all warehouses as sources with distance 0.
        for w in &problem.warehouses {
            let src = w.id as usize;
            if dist[src] > 0 {
                dist[src] = 0;
                dq.push_back(src);
            }
        }
        while let Some(u) = dq.pop_front() {
            for &(v, dly) in &delay_graph[u] {
                if dist[u] != i32::MAX && dist[u] + dly < dist[v] {
                    dist[v] = dist[u] + dly;
                    dq.push_back(v);
                }
            }
        }
        // Check if delivery can be within the time window upper bound.
        if dist[dest] == i32::MAX || dist[dest] > dc.time_window.1 {
            return Err("Time window infeasible for distribution center".to_string());
        }
    }

    // Calculate total demand.
    let total_demand: i32 = problem.distribution_centers.iter().map(|d| d.demand).sum();
    // Check if truck limit is sufficient.
    if total_demand > problem.truck_limit {
        return Err("Truck limit insufficient to meet total demand".to_string());
    }

    // We build a new graph for min cost flow.
    // Create new nodes:
    // Let aggregator Q be index: num_nodes
    // Let super source S be index: num_nodes + 1
    // Let super sink T be index: num_nodes + 2
    let q = num_nodes;
    let s = num_nodes + 1;
    let t = num_nodes + 2;
    let total_nodes = num_nodes + 3;

    let mut graph: Vec<Vec<MCEdge>> = vec![Vec::new(); total_nodes];

    // Helper function to add edge.
    fn add_edge(
        graph: &mut Vec<Vec<MCEdge>>,
        from: usize,
        to: usize,
        cap: i32,
        cost: i32,
        is_original: bool,
        orig_from: i32,
        orig_to: i32,
    ) {
        let from_len = graph[from].len();
        let to_len = graph[to].len();
        graph[from].push(MCEdge {
            to,
            cap,
            cost,
            rev: to_len,
            is_original,
            orig_from,
            orig_to,
            initial_cap: cap,
        });
        graph[to].push(MCEdge {
            to: from,
            cap: 0,
            cost: -cost,
            rev: from_len,
            is_original: false,
            orig_from: 0,
            orig_to: 0,
            initial_cap: 0,
        });
    }

    // Add edge from super source S -> aggregator Q with capacity = truck_limit.
    add_edge(&mut graph, s, q, problem.truck_limit, 0, false, 0, 0);
    // For each warehouse, add edge from aggregator Q -> warehouse with capacity = supply.
    for w in &problem.warehouses {
        let node = w.id as usize;
        add_edge(&mut graph, q, node, w.supply, 0, false, 0, 0);
    }
    // Add original graph edges.
    // For each edge in problem.edges, add edge from e.from to e.to with capacity and cost as given.
    for e in &problem.edges {
        let u = e.from as usize;
        let v = e.to as usize;
        add_edge(&mut graph, u, v, e.capacity, e.cost, true, e.from, e.to);
    }
    // For each distribution center, add edge from distribution center -> super sink T with capacity = demand.
    for d in &problem.distribution_centers {
        let node = d.id as usize;
        add_edge(&mut graph, node, t, d.demand, 0, false, 0, 0);
    }

    // Implement min cost flow algorithm.
    let mut flow = 0;
    let mut cost = 0;
    let flow_limit = total_demand; // Must push total demand.
    let mut potential = vec![0; total_nodes]; 
    let mut dist = vec![0; total_nodes];
    let mut prev_v = vec![0; total_nodes];
    let mut prev_e = vec![0; total_nodes];

    while flow < flow_limit {
        // Use Bellman-Ford to find shortest path from s to t.
        const INF: i32 = 1 << 28;
        dist = vec![INF; total_nodes];
        dist[s] = 0;
        let mut update = true;
        while update {
            update = false;
            for v in 0..total_nodes {
                if dist[v] == INF {
                    continue;
                }
                for (i, e) in graph[v].iter().enumerate() {
                    if e.cap > 0 && dist[e.to] > dist[v] + e.cost {
                        dist[e.to] = dist[v] + e.cost;
                        prev_v[e.to] = v;
                        prev_e[e.to] = i;
                        update = true;
                    }
                }
            }
        }
        if dist[t] == INF {
            return Err("Infeasible flow: cannot satisfy all demands".to_string());
        }
        // Determine the possible amount to push.
        let mut add_flow = flow_limit - flow;
        let mut v = t;
        while v != s {
            let pv = prev_v[v];
            let pe = prev_e[v];
            if add_flow > graph[pv][pe].cap {
                add_flow = graph[pv][pe].cap;
            }
            v = pv;
        }
        flow += add_flow;
        cost += add_flow * dist[t];
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

    // Now, reconstruct the flows on the original edges.
    let mut flows_out: Vec<FlowEdge> = Vec::new();
    for u in 0..total_nodes {
        for e in &graph[u] {
            if e.is_original {
                // Flow is initial_cap - remaining capacity.
                let sent = e.initial_cap - e.cap;
                if sent > 0 {
                    flows_out.push(FlowEdge {
                        from: e.orig_from,
                        to: e.orig_to,
                        flow: sent,
                    });
                }
            }
        }
    }

    Ok(FlowResult {
        flows: flows_out,
        total_cost: cost,
    })
}