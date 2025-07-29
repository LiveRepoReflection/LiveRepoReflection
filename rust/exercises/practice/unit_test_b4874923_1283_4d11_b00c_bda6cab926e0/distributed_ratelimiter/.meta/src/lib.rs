use std::collections::HashMap;
use std::hash::{Hash, Hasher};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

pub struct Config {
    pub capacity: usize,
    pub refill_rate: f64, // tokens per second
}

pub struct RateLimiter {
    config: Config,
    inner: Mutex<LimiterState>,
}

struct LimiterState {
    current_tokens: f64,
    last_refill: Instant,
}

impl RateLimiter {
    pub fn new(_client_id: String, config: Config) -> Self {
        let now = Instant::now();
        RateLimiter {
            config,
            inner: Mutex::new(LimiterState {
                current_tokens: _client_id.len() as f64, // initial value placeholder, will be overwritten
                last_refill: now,
            }),
        }
    }

    pub fn allow_request(&self) -> bool {
        let mut state = self.inner.lock().unwrap();
        let now = Instant::now();
        let elapsed = now.duration_since(state.last_refill);
        let refill_tokens = elapsed.as_secs_f64() * self.config.refill_rate;
        state.current_tokens = (state.current_tokens + refill_tokens).min(self.config.capacity as f64);
        state.last_refill = now;
        if state.current_tokens >= 1.0 {
            state.current_tokens -= 1.0;
            true
        } else {
            false
        }
    }
}

impl RateLimiter {
    // This method is used to initialize the rate limiter with full tokens.
    fn init_state(&self) {
        let mut state = self.inner.lock().unwrap();
        state.current_tokens = self.config.capacity as f64;
        state.last_refill = Instant::now();
    }
}

pub struct Node {
    online: Mutex<bool>,
    clients: Mutex<HashMap<String, Arc<RateLimiter>>>,
    config: Config,
}

impl Node {
    pub fn new(config: Config) -> Self {
        Node {
            online: Mutex::new(true),
            clients: Mutex::new(HashMap::new()),
            config,
        }
    }

    pub fn set_online(&self, flag: bool) {
        let mut online = self.online.lock().unwrap();
        *online = flag;
    }

    pub fn is_online(&self) -> bool {
        *self.online.lock().unwrap()
    }

    pub fn get_or_create_limiter(&self, client: &str) -> Arc<RateLimiter> {
        let mut clients = self.clients.lock().unwrap();
        if let Some(limiter) = clients.get(client) {
            return Arc::clone(limiter);
        }
        let limiter = Arc::new(RateLimiter::new(client.to_string(), Config {
            capacity: self.config.capacity,
            refill_rate: self.config.refill_rate,
        }));
        // Ensure bucket is full on creation.
        limiter.init_state();
        clients.insert(client.to_string(), Arc::clone(&limiter));
        limiter
    }
}

pub struct Cluster {
    nodes: Vec<Arc<Node>>,
}

impl Cluster {
    pub fn new(num_nodes: usize, config: Config) -> Self {
        let mut nodes = Vec::with_capacity(num_nodes);
        for _ in 0..num_nodes {
            nodes.push(Arc::new(Node::new(Config {
                capacity: config.capacity,
                refill_rate: config.refill_rate,
            })));
        }
        Cluster { nodes }
    }

    pub fn route_request(&self, client: &str) -> bool {
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        client.hash(&mut hasher);
        let mut idx = (hasher.finish() as usize) % self.nodes.len();
        let start_idx = idx;
        loop {
            let node = &self.nodes[idx];
            if node.is_online() {
                let limiter = node.get_or_create_limiter(client);
                return limiter.allow_request();
            }
            idx = (idx + 1) % self.nodes.len();
            if idx == start_idx {
                // All nodes are offline.
                return false;
            }
        }
    }

    pub fn kill_node(&self, node_index: usize) {
        if let Some(node) = self.nodes.get(node_index) {
            node.set_online(false);
        }
    }

    pub fn recover_node(&self, node_index: usize) {
        if let Some(node) = self.nodes.get(node_index) {
            node.set_online(true);
        }
    }
}