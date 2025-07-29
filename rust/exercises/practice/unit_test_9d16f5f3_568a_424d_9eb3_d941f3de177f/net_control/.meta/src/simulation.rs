use std::collections::HashMap;

use crate::network::Network;

pub struct Traffic {
    pub src: String,
    pub dst: String,
    pub rate: u64,
}

impl Traffic {
    pub fn new(src: &str, dst: &str, rate: u64) -> Self {
        Traffic {
            src: src.to_string(),
            dst: dst.to_string(),
            rate,
        }
    }
}

pub struct Simulation {
    pub network: Network,
    pub traffics: Vec<Traffic>,
    pub time_steps: u64,
}

pub struct SimulationResult {
    pub delivered: Vec<(String, String, u64)>,
    pub avg_latency: Vec<(String, String, f64)>,
    pub max_utilization: f64,
    pub total_dropped: u64,
}

impl Simulation {
    pub fn new(network: Network, traffics: Vec<Traffic>, time_steps: u64) -> Self {
        Simulation {
            network,
            traffics,
            time_steps,
        }
    }

    pub fn run(&mut self) -> SimulationResult {
        // Aggregated results per traffic flow, keyed by (src,dst)
        let mut delivered_flow: HashMap<(String, String), u64> = HashMap::new();
        let mut latency_flow: HashMap<(String, String), f64> = HashMap::new();
        let mut total_dropped = 0u64;
        let mut global_max_utilization = 0.0;

        // Run simulation for each time step
        for _ in 0..self.time_steps {
            // For each time step, we will accumulate the load on each link.
            let mut link_load: HashMap<usize, u64> = HashMap::new();
            // Map from traffic index to its chosen path (vec of link indices)
            let mut flow_paths: HashMap<usize, Vec<usize>> = HashMap::new();

            // Determine the path for each traffic flow and accumulate intended load.
            for (i, flow) in self.traffics.iter().enumerate() {
                if let Some(path) = self.network.find_path(&flow.src, &flow.dst) {
                    flow_paths.insert(i, path.clone());
                    // For each link in the path, add this flow's rate.
                    for li in path {
                        let entry = link_load.entry(li).or_insert(0);
                        *entry += flow.rate;
                    }
                }
            }

            // Update global max utilization
            for (li, &load) in link_load.iter() {
                let capacity = self.network.links[*li].capacity;
                let utilization = load as f64 / capacity as f64;
                if utilization > global_max_utilization {
                    global_max_utilization = utilization;
                }
            }

            // For each traffic flow, simulate packet transmission across its path.
            for (i, flow) in self.traffics.iter().enumerate() {
                let key = (flow.src.clone(), flow.dst.clone());
                if let Some(path) = flow_paths.get(&i) {
                    let mut packets = flow.rate;
                    let mut path_latency = 0.0;
                    // Process each link in the path sequentially.
                    for li in path {
                        let capacity = self.network.links[*li].capacity;
                        let load = *link_load.get(li).unwrap_or(&0);
                        let fraction = if load > capacity {
                            capacity as f64 / load as f64
                        } else {
                            1.0
                        };
                        let delivered_here = (packets as f64 * fraction).floor() as u64;
                        let dropped_here = packets.saturating_sub(delivered_here);
                        total_dropped += dropped_here;
                        // Calculate latency for this link: base latency is 1.0,
                        // if congested, add a penalty proportional to overload.
                        let link_latency = if load > capacity {
                            1.0 + (load as f64 / capacity as f64 - 1.0)
                        } else {
                            1.0
                        };
                        path_latency += link_latency;
                        packets = delivered_here;
                    }
                    // Update delivered packets and latency aggregates.
                    let entry_delivered = delivered_flow.entry(key.clone()).or_insert(0);
                    *entry_delivered += packets;
                    // Sum latency for delivered packets in this time step.
                    let entry_latency = latency_flow.entry(key).or_insert(0.0);
                    // Only add latency if some packets were delivered.
                    if packets > 0 {
                        *entry_latency += path_latency;
                    }
                }
            }
        }

        // Prepare results: average latency per flow is computed as total latency divided by total delivered packets.
        let mut delivered_vec = Vec::new();
        let mut avg_latency_vec = Vec::new();
        for ((src, dst), delivered) in delivered_flow {
            let latency = latency_flow.get(&(src.clone(), dst.clone())).unwrap_or(&0.0);
            let avg = if delivered > 0 {
                *latency / delivered as f64
            } else {
                0.0
            };
            delivered_vec.push((src.clone(), dst.clone(), delivered));
            avg_latency_vec.push((src, dst, avg));
        }

        SimulationResult {
            delivered: delivered_vec,
            avg_latency: avg_latency_vec,
            max_utilization: global_max_utilization,
            total_dropped,
        }
    }
}