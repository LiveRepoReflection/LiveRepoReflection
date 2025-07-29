use std::thread;
use std::time::Duration;
use saga_coordinator::{Coordinator, OrderRequest, OrderResponse, CoordinatorError};

#[test]
fn test_successful_order() {
    let mut coordinator = Coordinator::new();
    let request = OrderRequest {
        order_id: "order123".to_string(),
        user_id: "user456".to_string(),
        items: vec![
            ("item1".to_string(), 2),
            ("item2".to_string(), 3)
        ],
        payment_info: "valid_payment".to_string(),
        ttl: 300, // TTL in seconds
    };
    
    let response = coordinator.process_order(request);
    
    match response {
        Ok(order_response) => {
            assert_eq!(order_response.order_id, "order123");
            assert_eq!(order_response.status, "SUCCESS");
            assert!(order_response.error_message.is_none());
        },
        Err(e) => panic!("Expected successful order processing, got error: {:?}", e),
    }
}

#[test]
fn test_failure_in_inventory() {
    let mut coordinator = Coordinator::new();
    // Use a special item id "fail_inventory" to simulate an inventory failure.
    let request = OrderRequest {
        order_id: "order_fail_inventory".to_string(),
        user_id: "user789".to_string(),
        items: vec![
            ("fail_inventory".to_string(), 1)
        ],
        payment_info: "valid_payment".to_string(),
        ttl: 300,
    };
    
    let response = coordinator.process_order(request);
    
    match response {
        Ok(order_response) => {
            // Even if an order fails, the response should indicate the failure status.
            assert_eq!(order_response.status, "FAILED");
            assert!(order_response.error_message.is_some());
        },
        Err(e) => {
            // The error returned should be related to inventory failure.
            match e {
                CoordinatorError::InventoryFailure(_) => {},
                _ => panic!("Expected InventoryFailure error, got: {:?}", e),
            }
        },
    }
}

#[test]
fn test_ttl_expiry() {
    let mut coordinator = Coordinator::new();
    // Use a special item id "slow_item" to simulate a slow processing step.
    let request = OrderRequest {
        order_id: "order_ttl_expiry".to_string(),
        user_id: "user_ttl".to_string(),
        items: vec![
            ("slow_item".to_string(), 1)
        ],
        payment_info: "valid_payment".to_string(),
        ttl: 1, // Very short TTL to trigger expiry.
    };

    // Simulate a delay before processing to trigger TTL expiry.
    thread::sleep(Duration::from_secs(2));
    
    let response = coordinator.process_order(request);
    
    match response {
        Ok(order_response) => {
            assert_eq!(order_response.status, "FAILED");
            assert!(order_response.error_message.is_some());
        },
        Err(e) => match e {
            CoordinatorError::Timeout => {},
            _ => panic!("Expected Timeout error, got: {:?}", e),
        },
    }
}

#[test]
fn test_concurrent_sagas() {
    let mut handles = vec![];

    for i in 0..10 {
        let order_id = format!("order_concurrent_{}", i);
        let request = OrderRequest {
            order_id: order_id.clone(),
            user_id: format!("user_{}", i),
            items: vec![
                ("item1".to_string(), 1),
                ("item2".to_string(), 2)
            ],
            payment_info: "valid_payment".to_string(),
            ttl: 300,
        };

        handles.push(thread::spawn(move || {
            let mut coordinator = Coordinator::new();
            coordinator.process_order(request)
        }));
    }

    for handle in handles {
        let response = handle.join().unwrap();
        match response {
            Ok(order_response) => {
                assert_eq!(order_response.status, "SUCCESS");
            },
            Err(e) => panic!("Concurrent saga failed with error: {:?}", e),
        }
    }
}

#[test]
fn test_compensation_mechanism() {
    let mut coordinator = Coordinator::new();
    // Use a special payment_info "invalid_payment" to simulate a payment failure.
    let request = OrderRequest {
        order_id: "order_compensation".to_string(),
        user_id: "user_comp".to_string(),
        items: vec![
            ("item1".to_string(), 1)
        ],
        payment_info: "invalid_payment".to_string(),
        ttl: 300,
    };
    
    let response = coordinator.process_order(request);
    
    match response {
        Ok(order_response) => {
            // The order should fail and all previous steps must have been compensated.
            assert_eq!(order_response.status, "FAILED");
            assert!(order_response.error_message.is_some());
        },
        Err(e) => match e {
            CoordinatorError::PaymentFailure(_) => {},
            _ => panic!("Expected PaymentFailure error, got: {:?}", e),
        },
    }
}