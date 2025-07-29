use std::sync::{Arc, Barrier};
use std::thread;

use saga_orchestrator::{orchestrate_saga, SagaRequest, SagaStatus};

#[test]
fn test_successful_saga() {
    // A saga with all steps succeeding should complete successfully.
    let request = SagaRequest {
        order_id: 1,
        payment_success: true,
        inventory_success: true,
        shipping_success: true,
    };
    let result = orchestrate_saga(request);
    assert_eq!(result, SagaStatus::Completed);
}

#[test]
fn test_payment_failure_triggers_compensation() {
    // Payment failure should trigger rollback in all services.
    let request = SagaRequest {
        order_id: 2,
        payment_success: false,
        inventory_success: true,
        shipping_success: true,
    };
    let result = orchestrate_saga(request);
    assert_eq!(result, SagaStatus::Compensated);
}

#[test]
fn test_inventory_failure_triggers_compensation() {
    // Inventory failure should trigger compensation actions.
    let request = SagaRequest {
        order_id: 3,
        payment_success: true,
        inventory_success: false,
        shipping_success: true,
    };
    let result = orchestrate_saga(request);
    assert_eq!(result, SagaStatus::Compensated);
}

#[test]
fn test_shipping_failure_triggers_compensation() {
    // Shipping failure should trigger compensation actions.
    let request = SagaRequest {
        order_id: 4,
        payment_success: true,
        inventory_success: true,
        shipping_success: false,
    };
    let result = orchestrate_saga(request);
    assert_eq!(result, SagaStatus::Compensated);
}

#[test]
fn test_idempotency_of_saga() {
    // Triggering the same saga multiple times should produce the same result without adverse effects.
    let request = SagaRequest {
        order_id: 5,
        payment_success: true,
        inventory_success: true,
        shipping_success: true,
    };

    let first_attempt = orchestrate_saga(request.clone());
    let second_attempt = orchestrate_saga(request);
    assert_eq!(first_attempt, SagaStatus::Completed);
    assert_eq!(second_attempt, SagaStatus::Completed);
}

#[test]
fn test_concurrent_sagas() {
    // Simulate multiple sagas running concurrently.
    // We use a barrier to start all threads at roughly the same time.
    let num_threads = 10;
    let barrier = Arc::new(Barrier::new(num_threads));
    let mut handles = Vec::with_capacity(num_threads);

    for i in 0..num_threads {
        let cbarrier = barrier.clone();
        let order_id = 100 + i as u64;
        handles.push(thread::spawn(move || {
            // Wait for all threads.
            cbarrier.wait();
            // Alternate success and failure for inventory step.
            let inventory_success = i % 2 == 0;
            let request = SagaRequest {
                order_id,
                payment_success: true,
                inventory_success,
                shipping_success: true,
            };
            let result = orchestrate_saga(request);
            if inventory_success {
                assert_eq!(result, SagaStatus::Completed);
            } else {
                assert_eq!(result, SagaStatus::Compensated);
            }
        }));
    }

    for handle in handles {
        handle.join().expect("Thread panicked");
    }
}