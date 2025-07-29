use rate_limiter::{RateLimiter, RateLimitConfig};
use std::sync::Arc;
use std::time::{Duration, Instant};
use tokio::sync::Mutex;

#[tokio::test]
async fn test_single_user_rate_limiting() {
    let config = RateLimitConfig {
        user_id: "user1".to_string(),
        endpoint: "/api".to_string(),
        max_requests: 5,
        time_window: Duration::from_secs(1),
    };
    
    let limiter = Arc::new(Mutex::new(RateLimiter::new()));
    limiter.lock().await.add_config(config.clone());

    // First 5 requests should pass
    for _ in 0..5 {
        assert!(limiter.lock().await.check_limit(&config.user_id, &config.endpoint).await);
    }

    // 6th request should fail
    assert!(!limiter.lock().await.check_limit(&config.user_id, &config.endpoint).await);

    // After window expires, should allow again
    tokio::time::sleep(Duration::from_secs(1)).await;
    assert!(limiter.lock().await.check_limit(&config.user_id, &config.endpoint).await);
}

#[tokio::test]
async fn test_multiple_users_different_limits() {
    let config1 = RateLimitConfig {
        user_id: "user1".to_string(),
        endpoint: "/api".to_string(),
        max_requests: 3,
        time_window: Duration::from_secs(1),
    };
    
    let config2 = RateLimitConfig {
        user_id: "user2".to_string(),
        endpoint: "/api".to_string(),
        max_requests: 5,
        time_window: Duration::from_secs(1),
    };

    let limiter = Arc::new(Mutex::new(RateLimiter::new()));
    limiter.lock().await.add_config(config1.clone());
    limiter.lock().await.add_config(config2.clone());

    // User1 hits limit at 3
    for _ in 0..3 {
        assert!(limiter.lock().await.check_limit(&config1.user_id, &config1.endpoint).await);
    }
    assert!(!limiter.lock().await.check_limit(&config1.user_id, &config1.endpoint).await);

    // User2 still has 2 more allowed
    for _ in 0..3 {
        assert!(limiter.lock().await.check_limit(&config2.user_id, &config2.endpoint).await);
    }
    assert!(limiter.lock().await.check_limit(&config2.user_id, &config2.endpoint).await);
}

#[tokio::test]
async fn test_different_endpoints() {
    let config1 = RateLimitConfig {
        user_id: "user1".to_string(),
        endpoint: "/api1".to_string(),
        max_requests: 2,
        time_window: Duration::from_secs(1),
    };
    
    let config2 = RateLimitConfig {
        user_id: "user1".to_string(),
        endpoint: "/api2".to_string(),
        max_requests: 4,
        time_window: Duration::from_secs(1),
    };

    let limiter = Arc::new(Mutex::new(RateLimiter::new()));
    limiter.lock().await.add_config(config1.clone());
    limiter.lock().await.add_config(config2.clone());

    // Hit limit on api1
    for _ in 0..2 {
        assert!(limiter.lock().await.check_limit(&config1.user_id, &config1.endpoint).await);
    }
    assert!(!limiter.lock().await.check_limit(&config1.user_id, &config1.endpoint).await);

    // Still can access api2
    for _ in 0..2 {
        assert!(limiter.lock().await.check_limit(&config2.user_id, &config2.endpoint).await);
    }
}

#[tokio::test]
async fn test_config_update() {
    let mut config = RateLimitConfig {
        user_id: "user1".to_string(),
        endpoint: "/api".to_string(),
        max_requests: 2,
        time_window: Duration::from_secs(1),
    };

    let limiter = Arc::new(Mutex::new(RateLimiter::new()));
    limiter.lock().await.add_config(config.clone());

    // Hit initial limit
    for _ in 0..2 {
        assert!(limiter.lock().await.check_limit(&config.user_id, &config.endpoint).await);
    }
    assert!(!limiter.lock().await.check_limit(&config.user_id, &config.endpoint).await);

    // Update config
    config.max_requests = 4;
    limiter.lock().await.update_config(config.clone());

    // Should now allow more requests
    for _ in 0..2 {
        assert!(limiter.lock().await.check_limit(&config.user_id, &config.endpoint).await);
    }
}

#[tokio::test]
async fn test_concurrent_access() {
    let config = RateLimitConfig {
        user_id: "user1".to_string(),
        endpoint: "/api".to_string(),
        max_requests: 100,
        time_window: Duration::from_secs(1),
    };

    let limiter = Arc::new(Mutex::new(RateLimiter::new()));
    limiter.lock().await.add_config(config.clone());

    let mut handles = vec![];
    for _ in 0..10 {
        let limiter = limiter.clone();
        let config = config.clone();
        handles.push(tokio::spawn(async move {
            for _ in 0..10 {
                limiter.lock().await.check_limit(&config.user_id, &config.endpoint).await;
            }
        }));
    }

    for handle in handles {
        handle.await.unwrap();
    }

    // Should have exactly 100 requests counted
    assert!(!limiter.lock().await.check_limit(&config.user_id, &config.endpoint).await);
}

#[tokio::test]
async fn test_time_window_reset() {
    let config = RateLimitConfig {
        user_id: "user1".to_string(),
        endpoint: "/api".to_string(),
        max_requests: 1,
        time_window: Duration::from_millis(100),
    };

    let limiter = Arc::new(Mutex::new(RateLimiter::new()));
    limiter.lock().await.add_config(config.clone());

    // First request allowed
    assert!(limiter.lock().await.check_limit(&config.user_id, &config.endpoint).await);
    
    // Second request blocked
    assert!(!limiter.lock().await.check_limit(&config.user_id, &config.endpoint).await);
    
    // Wait for window to reset
    tokio::time::sleep(Duration::from_millis(150)).await;
    
    // Should be allowed again
    assert!(limiter.lock().await.check_limit(&config.user_id, &config.endpoint).await);
}