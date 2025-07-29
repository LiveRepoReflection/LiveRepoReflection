use std::thread;
use std::time::Duration;
use distributed_saga::{Order, process_order, SagaError};

#[test]
fn test_successful_transaction() {
    let order = Order {
        order_id: 1,
        customer_id: 10,
        items: vec![(101, 2), (102, 1)],
        payment_info: "valid_payment".to_string(),
    };
    match process_order(order) {
        Ok(result) => {
            assert_eq!(result, "Order processed successfully");
        },
        Err(err) => panic!("Expected success but got error: {:?}", err),
    }
}

#[test]
fn test_inventory_failure() {
    let order = Order {
        order_id: 2,
        customer_id: 20,
        // Use an item id that the mocked InventoryService will treat as unavailable.
        items: vec![(999, 1)],
        payment_info: "valid_payment".to_string(),
    };
    match process_order(order) {
        Ok(_) => panic!("Expected failure due to inventory error, but transaction succeeded"),
        Err(err) => {
            match err {
                SagaError::InventoryError(msg) => {
                    assert!(msg.contains("Inventory"));
                },
                _ => panic!("Expected InventoryError, got different error: {:?}", err),
            }
        },
    }
}

#[test]
fn test_payment_failure() {
    let order = Order {
        order_id: 3,
        customer_id: 30,
        items: vec![(101, 1)],
        // Use payment info that triggers a failure in the PaymentService.
        payment_info: "fail_payment".to_string(),
    };
    match process_order(order) {
        Ok(_) => panic!("Expected failure due to payment error, but transaction succeeded"),
        Err(err) => {
            match err {
                SagaError::PaymentError(msg) => {
                    assert!(msg.contains("Payment"));
                },
                _ => panic!("Expected PaymentError, got different error: {:?}", err),
            }
        },
    }
}

#[test]
fn test_shipping_failure() {
    let order = Order {
        order_id: 4,
        customer_id: 40,
        items: vec![(101, 1)],
        payment_info: "valid_payment".to_string(),
    };
    // Suppose that for order_id == 4, the ShippingService simulates a failure.
    match process_order(order) {
        Ok(_) => panic!("Expected failure due to shipping error, but transaction succeeded"),
        Err(err) => {
            match err {
                SagaError::ShippingError(msg) => {
                    assert!(msg.contains("Shipping"));
                },
                _ => panic!("Expected ShippingError, got different error: {:?}", err),
            }
        },
    }
}

#[test]
fn test_notification_failure() {
    let order = Order {
        order_id: 5,
        customer_id: 50,
        items: vec![(101, 1)],
        payment_info: "valid_payment".to_string(),
    };
    // Assume that for order_id == 5, the NotificationService triggers a failure.
    match process_order(order) {
        Ok(_) => panic!("Expected failure due to notification error, but transaction succeeded"),
        Err(err) => {
            match err {
                SagaError::NotificationError(msg) => {
                    assert!(msg.contains("Notification"));
                },
                _ => panic!("Expected NotificationError, got different error: {:?}", err),
            }
        },
    }
}

#[test]
fn test_concurrent_transactions() {
    let orders: Vec<Order> = (6..=10)
        .map(|i| Order {
            order_id: i,
            customer_id: i * 10,
            items: vec![(101, 1), (102, 2)],
            payment_info: "valid_payment".to_string(),
        })
        .collect();

    let mut handles = vec![];

    for order in orders {
        handles.push(thread::spawn(move || {
            // Introduce a slight delay to simulate asynchronous behavior.
            thread::sleep(Duration::from_millis(10));
            process_order(order)
        }));
    }

    for handle in handles {
        match handle.join() {
            Ok(result) => {
                match result {
                    Ok(msg) => assert_eq!(msg, "Order processed successfully"),
                    Err(err) => panic!("Expected successful transaction in concurrent order, got error: {:?}", err),
                }
            },
            Err(_) => panic!("Thread panicked during execution"),
        }
    }
}

#[test]
fn test_retry_mechanism() {
    let order = Order {
        order_id: 11,
        customer_id: 110,
        items: vec![(101, 1)],
        // Use payment info that simulates a transient failure which should be recovered via retries.
        payment_info: "transient_failure_payment".to_string(),
    };

    // The process_order function is expected to internally retry on transient errors.
    match process_order(order) {
        Ok(msg) => assert_eq!(msg, "Order processed successfully"),
        Err(err) => panic!("Expected success after retries, but got error: {:?}", err),
    }
}