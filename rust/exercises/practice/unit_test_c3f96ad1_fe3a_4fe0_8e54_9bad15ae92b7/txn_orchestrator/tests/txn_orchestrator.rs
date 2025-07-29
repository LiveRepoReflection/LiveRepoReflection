use txn_orchestrator::{TransactionOrchestrator, InventoryService, PaymentService, OrderService};

#[test]
fn test_successful_transaction() {
    let inventory = InventoryService::new(0.0);
    let payment = PaymentService::new(0.0);
    let order = OrderService::new(0.0);
    let mut orchestrator = TransactionOrchestrator::new(inventory, payment, order);

    let result = orchestrator.execute_transaction(1, vec![(10, 2), (20, 3)], 150);
    assert!(result.is_ok(), "Expected transaction to succeed");
    if let Ok(order_id) = result {
        assert!(order_id > 0, "Order ID should be a positive number");
    }
}

#[test]
fn test_inventory_failure() {
    // Set inventory failure probability to 100% to simulate failure.
    let inventory = InventoryService::new(1.0);
    let payment = PaymentService::new(0.0);
    let order = OrderService::new(0.0);
    let mut orchestrator = TransactionOrchestrator::new(inventory, payment, order);

    let result = orchestrator.execute_transaction(2, vec![(30, 1)], 100);
    assert!(result.is_err(), "Expected transaction to fail due to inventory failure");
    let err_msg = result.unwrap_err();
    assert!(err_msg.contains("Inventory"), "Error message should mention Inventory failure");
}

#[test]
fn test_payment_failure() {
    // Set payment failure probability to 100% to simulate failure.
    let inventory = InventoryService::new(0.0);
    let payment = PaymentService::new(1.0);
    let order = OrderService::new(0.0);
    let mut orchestrator = TransactionOrchestrator::new(inventory, payment, order);

    let result = orchestrator.execute_transaction(3, vec![(40, 3)], 120);
    assert!(result.is_err(), "Expected transaction to fail due to payment failure");
    let err_msg = result.unwrap_err();
    assert!(err_msg.contains("Payment"), "Error message should mention Payment failure");
}

#[test]
fn test_order_failure() {
    // Set order failure probability to 100% to simulate order creation failure.
    let inventory = InventoryService::new(0.0);
    let payment = PaymentService::new(0.0);
    let order = OrderService::new(1.0);
    let mut orchestrator = TransactionOrchestrator::new(inventory, payment, order);

    let result = orchestrator.execute_transaction(4, vec![(50, 5)], 250);
    assert!(result.is_err(), "Expected transaction to fail due to order creation failure");
    let err_msg = result.unwrap_err();
    assert!(err_msg.contains("Order"), "Error message should mention Order creation failure");
}