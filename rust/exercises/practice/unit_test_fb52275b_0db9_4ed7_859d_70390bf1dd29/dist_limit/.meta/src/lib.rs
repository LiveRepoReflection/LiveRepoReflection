use std::collections::HashMap;
use std::fs::{File, OpenOptions};
use std::io::{Read, Write};
use std::sync::Mutex;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

pub struct RateLimiter {
    inner: Mutex<RateLimiterInner>,
    persist_path: String,
}

struct RateLimiterInner {
    rates: HashMap<String, (u32, Duration)>,
    user_requests: HashMap<String, Vec<u128>>,
}

impl RateLimiter {
    pub fn new() -> RateLimiter {
        let persist_path = "dist_limit_state.db".to_string();
        let mut inner = RateLimiterInner {
            rates: HashMap::new(),
            user_requests: HashMap::new(),
        };
        if let Ok(saved_state) = RateLimiter::load_state_from_file(&persist_path) {
            inner.user_requests = saved_state;
        }
        RateLimiter {
            inner: Mutex::new(inner),
            persist_path,
        }
    }

    pub fn set_rate(&mut self, user: &str, limit: u32, window: Duration) {
        let mut inner = self.inner.lock().unwrap();
        inner.rates.insert(user.to_string(), (limit, window));
        inner.user_requests.entry(user.to_string()).or_insert_with(Vec::new);
    }

    pub fn allow(&self, user: &str) -> bool {
        let now_ms = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis();
        let mut inner = self.inner.lock().unwrap();
        let (limit, window) = match inner.rates.get(user) {
            Some(rate) => *rate,
            None => {
                // If no rate is set, allow the request.
                return true;
            }
        };
        let window_ms = window.as_millis();
        let entry = inner.user_requests.entry(user.to_string()).or_insert_with(Vec::new);
        entry.retain(|&timestamp| now_ms.saturating_sub(timestamp) < window_ms);
        if entry.len() < limit as usize {
            entry.push(now_ms);
            let _ = RateLimiter::persist_state_to_file(&self.persist_path, &inner.user_requests);
            true
        } else {
            false
        }
    }

    fn persist_state_to_file(
        path: &str,
        data: &HashMap<String, Vec<u128>>,
    ) -> std::io::Result<()> {
        let mut file = OpenOptions::new()
            .write(true)
            .create(true)
            .truncate(true)
            .open(path)?;
        for (user, timestamps) in data {
            let timestamp_strs: Vec<String> =
                timestamps.iter().map(|ts| ts.to_string()).collect();
            let line = format!("{};{}\n", user, timestamp_strs.join(","));
            file.write_all(line.as_bytes())?;
        }
        Ok(())
    }

    fn load_state_from_file(path: &str) -> std::io::Result<HashMap<String, Vec<u128>>> {
        let mut file = File::open(path)?;
        let mut contents = String::new();
        file.read_to_string(&mut contents)?;
        let mut data = HashMap::new();
        for line in contents.lines() {
            let parts: Vec<&str> = line.splitn(2, ';').collect();
            if parts.len() != 2 {
                continue;
            }
            let user = parts[0].to_string();
            let timestamps: Vec<u128> = if parts[1].trim().is_empty() {
                Vec::new()
            } else {
                parts[1]
                    .split(',')
                    .filter_map(|s| s.parse::<u128>().ok())
                    .collect()
            };
            data.insert(user, timestamps);
        }
        Ok(data)
    }
}