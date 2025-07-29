pub struct Link {
    pub from: usize,
    pub to: usize,
    pub capacity: u32,
}

pub struct TrafficDemand {
    pub source: usize,
    pub destination: usize,
    pub initial_rate: u32,
}

pub struct NetworkConfig {
    pub n: usize,                      // Number of nodes
    pub links: Vec<Link>,              // List of links
    pub traffic_demands: Vec<TrafficDemand>, // List of traffic demands
    pub time_units: u32,               // Number of time units to simulate
    pub alpha: f64,                    // Additive increase constant
    pub beta: f64,                     // Multiplicative decrease factor
}

/// Simulates the network congestion control algorithm
/// Returns the final sending rates for each traffic demand
pub fn simulate_network(config: &NetworkConfig) -> Vec<f64> {
    // Your implementation goes here
    // This is a stub to make the tests compile
    vec![0.0; config.traffic_demands.len()]
}