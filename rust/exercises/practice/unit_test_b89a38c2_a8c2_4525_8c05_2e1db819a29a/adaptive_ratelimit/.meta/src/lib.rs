use std::collections::HashMap;
use std::sync::Mutex;
use std::time::{Duration, Instant};

#[derive(Clone)]
pub struct RateLimitConfig {
    limits: HashMap<String, (u32, Duration)>,
}

impl RateLimitConfig {
    pub fn new() -> Self {
        RateLimitConfig {
            limits: HashMap::new(),
        }
    }

    pub fn set_client_limit(&mut self, client_id: &str, limit: u32, window: Duration) {
        self.limits.insert(client_id.to_string(), (limit, window));
    }

    pub fn get(&self, client_id: &str) -> Option<(u32, Duration)> {
        self.limits.get(client_id).cloned()
    }
}

impl Default for RateLimitConfig {
    fn default() -> Self {
        Self::new()
    }
}

#[derive(Clone)]
struct ClientState {
    count: u32,
    window_start: Instant,
}

pub struct RateLimiter {
    config: Mutex<RateLimitConfig>,
    client_states: Mutex<HashMap<String, ClientState>>,
    system_load: Mutex<f64>, // load value between 0.0 and 1.0
}

impl RateLimiter {
    pub fn new(config: RateLimitConfig) -> Self {
        RateLimiter {
            config: Mutex::new(config),
            client_states: Mutex::new(HashMap::new()),
            system_load: Mutex::new(0.0),
        }
    }

    pub fn allow_request(&self, client_id: &str) -> bool {
        let now = Instant::now();
        let (limit, window) = {
            let cfg = self.config.lock().unwrap();
            match cfg.get(client_id) {
                Some((lim, win)) => (lim, win),
                None => {
                    // if no configuration exists, deny the request by default
                    return false;
                }
            }
        };

        // Determine effective limit based on system load.
        // Under heavy load (>=0.8) reduce allowed limit to 60% of the configured one.
        let effective_limit = {
            let load = *self.system_load.lock().unwrap();
            if load >= 0.8 {
                let adjusted = (limit as f64 * 0.6).floor() as u32;
                if adjusted < 1 { 1 } else { adjusted }
            } else {
                limit
            }
        };

        let mut states = self.client_states.lock().unwrap();
        let state = states.entry(client_id.to_string()).or_insert(ClientState {
            count: 0,
            window_start: now,
        });

        if now.duration_since(state.window_start) >= window {
            state.count = 0;
            state.window_start = now;
        }

        if state.count < effective_limit {
            state.count += 1;
            true
        } else {
            false
        }
    }

    pub fn update_config(&self, client_id: &str, new_limit: u32, new_window: Duration) {
        {
            let mut cfg = self.config.lock().unwrap();
            cfg.set_client_limit(client_id, new_limit, new_window);
        }
        let mut states = self.client_states.lock().unwrap();
        states.insert(
            client_id.to_string(),
            ClientState {
                count: 0,
                window_start: Instant::now(),
            },
        );
    }

    pub fn simulate_system_load(&self, load: f64) {
        let mut current_load = self.system_load.lock().unwrap();
        *current_load = load;
    }

    pub fn recover_state(&self) -> RateLimiter {
        let cfg = {
            let cfg_lock = self.config.lock().unwrap();
            cfg_lock.clone()
        };
        let states = {
            let state_lock = self.client_states.lock().unwrap();
            state_lock.clone()
        };
        let load = *self.system_load.lock().unwrap();
        RateLimiter {
            config: Mutex::new(cfg),
            client_states: Mutex::new(states),
            system_load: Mutex::new(load),
        }
    }
}