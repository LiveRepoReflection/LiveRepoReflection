#[derive(Debug, Clone, Default)]
pub struct TrustNetwork {
    // Implementation will be provided by the solution
}

impl TrustNetwork {
    pub fn new() -> Self {
        TrustNetwork::default()
    }
    
    pub fn add_trust_assertion(&mut self, from: u32, to: u32, trust_score: Option<f64>) {
        // Implementation will be provided by the solution
    }
    
    pub fn highest_trust_path(&self, source: u32, destination: u32) -> f64 {
        // Implementation will be provided by the solution
        0.0
    }
}

// Thread-safe version for concurrent access
pub struct ConcurrentTrustNetwork {
    // Implementation will be provided by the solution
}

impl ConcurrentTrustNetwork {
    pub fn new() -> Self {
        // Implementation will be provided by the solution
        Self {}
    }
    
    pub fn add_trust_assertion(&self, from: u32, to: u32, trust_score: Option<f64>) {
        // Implementation will be provided by the solution
    }
    
    pub fn highest_trust_path(&self, source: u32, destination: u32) -> f64 {
        // Implementation will be provided by the solution
        0.0
    }
}