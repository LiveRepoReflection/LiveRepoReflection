use std::collections::{BinaryHeap, HashMap};
use std::cmp::Ordering;
use std::u32;

#[derive(Clone)]
struct Edge {
    target: usize,
    bandwidth: u32,
}

pub struct Graph {
    // Adjacency list: node -> Vec<Edge>
    adj: HashMap<usize, Vec<Edge>>,
}

impl Graph {
    pub fn new() -> Self {
        Graph {
            adj: HashMap::new(),
        }
    }

    pub fn add_connection(&mut self, u: usize, v: usize, bandwidth: u32) {
        self.adj.entry(u).or_insert(Vec::new()).push(Edge { target: v, bandwidth });
        self.adj.entry(v).or_insert(Vec::new()).push(Edge { target: u, bandwidth });
    }

    pub fn remove_connection(&mut self, u: usize, v: usize) {
        if let Some(neighbors) = self.adj.get_mut(&u) {
            neighbors.retain(|edge| edge.target != v);
        }
        if let Some(neighbors) = self.adj.get_mut(&v) {
            neighbors.retain(|edge| edge.target != u);
        }
    }

    // Routing using modified Dijkstra to maximize the minimal bandwidth (bottleneck)
    // and in case of ties, pick the path with fewer hops.
    pub fn route(&self, source: usize, destination: usize) -> Option<(Vec<usize>, u32, usize)> {
        // best[node] = (best_bottleneck, hops)
        let mut best: HashMap<usize, (u32, usize)> = HashMap::new();
        let mut heap = BinaryHeap::new();

        // Start with source node. Bottleneck is infinity (represented by u32::MAX)
        best.insert(source, (u32::MAX, 0));
        heap.push(State {
            node: source,
            bottleneck: u32::MAX,
            hops: 0,
            path: vec![source],
        });

        while let Some(current) = heap.pop() {
            // If we reached the destination, return the path and bottleneck
            if current.node == destination {
                return Some((current.path, current.bottleneck, current.hops));
            }
            // If current state is not as good as recorded, skip
            if let Some(&(best_bot, best_hops)) = best.get(&current.node) {
                if current.bottleneck < best_bot || (current.bottleneck == best_bot && current.hops > best_hops) {
                    continue;
                }
            }
            if let Some(neighbors) = self.adj.get(&current.node) {
                for edge in neighbors {
                    let new_bottleneck = current.bottleneck.min(edge.bandwidth);
                    let new_hops = current.hops + 1;
                    // Check if we found a better route to edge.target
                    let update = match best.get(&edge.target) {
                        None => true,
                        Some(&(existing_bot, existing_hops)) => {
                            new_bottleneck > existing_bot || (new_bottleneck == existing_bot && new_hops < existing_hops)
                        }
                    };
                    if update {
                        let mut new_path = current.path.clone();
                        new_path.push(edge.target);
                        best.insert(edge.target, (new_bottleneck, new_hops));
                        heap.push(State {
                            node: edge.target,
                            bottleneck: new_bottleneck,
                            hops: new_hops,
                            path: new_path,
                        });
                    }
                }
            }
        }
        None
    }
}

#[derive(Clone)]
struct State {
    node: usize,
    bottleneck: u32,
    hops: usize,
    path: Vec<usize>,
}

// Custom ordering for BinaryHeap: higher bottleneck first, if tie then fewer hops.
impl Eq for State {}

impl PartialEq for State {
    fn eq(&self, other: &Self) -> bool {
        self.bottleneck == other.bottleneck && self.hops == other.hops
    }
}

impl Ord for State {
    fn cmp(&self, other: &Self) -> Ordering {
        // First compare by bottleneck (higher is better)
        match self.bottleneck.cmp(&other.bottleneck) {
            Ordering::Equal => {
                // Then by hops (fewer is better)
                other.hops.cmp(&self.hops)
            },
            other_order => other_order,
        }
    }
}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

// Parses a command string and returns a Command enum.
enum Command {
    Connect { u: usize, v: usize, bandwidth: u32 },
    Remove { u: usize, v: usize },
    Transmit { source: usize, destination: usize, packet_size: u32 },
}

fn parse_command(line: &str) -> Option<Command> {
    let tokens: Vec<&str> = line.split_whitespace().collect();
    if tokens.is_empty() {
        return None;
    }
    match tokens[0] {
        "connect" => {
            if tokens.len() != 4 {
                return None;
            }
            let u = tokens[1].parse().ok()?;
            let v = tokens[2].parse().ok()?;
            let bandwidth = tokens[3].parse().ok()?;
            Some(Command::Connect { u, v, bandwidth })
        },
        "remove" => {
            if tokens.len() != 3 {
                return None;
            }
            let u = tokens[1].parse().ok()?;
            let v = tokens[2].parse().ok()?;
            Some(Command::Remove { u, v })
        },
        "transmit" => {
            if tokens.len() != 4 {
                return None;
            }
            let source = tokens[1].parse().ok()?;
            let destination = tokens[2].parse().ok()?;
            let packet_size = tokens[3].parse().ok()?;
            Some(Command::Transmit { source, destination, packet_size })
        },
        _ => None,
    }
}

// The simulate function processes an iterator of command strings, updating the
// network graph and processing transmissions. It returns a vector of output strings
// for each transmit command.
pub fn simulate<I: Iterator<Item = String>>(commands: I) -> Vec<String> {
    let mut outputs = Vec::new();
    let mut graph = Graph::new();
    
    for line in commands {
        if let Some(command) = parse_command(&line) {
            match command {
                Command::Connect { u, v, bandwidth } => {
                    graph.add_connection(u, v, bandwidth);
                },
                Command::Remove { u, v } => {
                    graph.remove_connection(u, v);
                },
                Command::Transmit { source, destination, packet_size } => {
                    if let Some((path, effective_bandwidth, _hops)) = graph.route(source, destination) {
                        // Calculate transmission time as packet_size / effective_bandwidth.
                        // Even if packet_size > effective_bandwidth, the simulator splits the packet.
                        let transmission_time = (packet_size as f64) / (effective_bandwidth as f64);
                        // Build output string: "success <path> <transmission_time formatted to two decimals>"
                        let mut output = String::from("success");
                        for node in path {
                            output.push(' ');
                            output.push_str(&node.to_string());
                        }
                        output.push(' ');
                        output.push_str(&format!("{:.2}", transmission_time));
                        outputs.push(output);
                    } else {
                        outputs.push(String::from("failure no path"));
                    }
                },
            }
        }
    }
    
    outputs
}