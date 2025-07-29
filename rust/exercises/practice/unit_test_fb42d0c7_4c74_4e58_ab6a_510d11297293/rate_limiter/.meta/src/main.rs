use rate_limiter::{RateLimiter, RateLimitConfig};
use std::sync::Arc;
use std::time::Duration;
use tokio::sync::Mutex;

#[tokio::main]
async fn main() {
    let limiter = Arc::new(Mutex::new(RateLimiter::new()));
    
    let config = RateLimitConfig {
        user_id: "api_user".to_string(),
        endpoint: "/data".to_string(),
        max_requests: 5,
        time_window: Duration::from_secs(60),
    };

    limiter.lock().await.add_config(config);

    println!("Rate limiter service started");
}