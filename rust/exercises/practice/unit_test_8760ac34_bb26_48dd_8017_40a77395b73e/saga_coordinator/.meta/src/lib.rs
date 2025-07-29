use std::thread;
use std::time::{Duration, Instant};

/// Represents an order request in the system.
pub struct OrderRequest {
    pub order_id: String,
    pub user_id: String,
    pub items: Vec<(String, u32)>,
    pub payment_info: String,
    pub ttl: u64, // time-to-live in seconds
}

/// Represents an order response returned by the coordinator.
pub struct OrderResponse {
    pub order_id: String,
    pub status: String,
    pub error_message: Option<String>,
}

/// Represents possible errors returned by the Coordinator
#[derive(Debug)]
pub enum CoordinatorError {
    Timeout,
    OrderFailure(String),
    InventoryFailure(String),
    PaymentFailure(String),
    ShippingFailure(String),
}

/// Coordinator orchestrates the saga across microservices.
pub struct Coordinator {}

impl Coordinator {
    /// Constructs a new Coordinator.
    pub fn new() -> Self {
        Coordinator {}
    }

    /// Processes the order request through a series of steps.
    /// Implements the saga pattern with compensations.
    pub fn process_order(&mut self, req: OrderRequest) -> Result<OrderResponse, CoordinatorError> {
        let start = Instant::now();
        
        // Step 1: Order Service
        if check_timeout(start, req.ttl) {
            return Err(CoordinatorError::Timeout);
        }
        let order_result = order_service(&req);
        if order_result.is_err() {
            return Err(CoordinatorError::OrderFailure("Order service error".to_string()));
        }
        
        // Step 2: Inventory Service
        if check_timeout(start, req.ttl) {
            let _ = order_compensate(&req);
            return Err(CoordinatorError::Timeout);
        }
        let inv_result = inventory_service(&req);
        if let Err(msg) = inv_result {
            let _ = order_compensate(&req);
            return Err(CoordinatorError::InventoryFailure(msg));
        }
        
        // Step 3: Payment Service
        if check_timeout(start, req.ttl) {
            let _ = inventory_compensate(&req);
            let _ = order_compensate(&req);
            return Err(CoordinatorError::Timeout);
        }
        let pay_result = payment_service(&req);
        if let Err(msg) = pay_result {
            let _ = inventory_compensate(&req);
            let _ = order_compensate(&req);
            return Err(CoordinatorError::PaymentFailure(msg));
        }
        
        // Step 4: Shipping Service
        if check_timeout(start, req.ttl) {
            let _ = payment_compensate(&req);
            let _ = inventory_compensate(&req);
            let _ = order_compensate(&req);
            return Err(CoordinatorError::Timeout);
        }
        let ship_result = shipping_service(&req);
        if let Err(msg) = ship_result {
            let _ = payment_compensate(&req);
            let _ = inventory_compensate(&req);
            let _ = order_compensate(&req);
            return Err(CoordinatorError::ShippingFailure(msg));
        }
        
        if check_timeout(start, req.ttl) {
            let _ = shipping_compensate(&req);
            let _ = payment_compensate(&req);
            let _ = inventory_compensate(&req);
            let _ = order_compensate(&req);
            return Err(CoordinatorError::Timeout);
        }
        
        Ok(OrderResponse {
            order_id: req.order_id,
            status: "SUCCESS".to_string(),
            error_message: None,
        })
    }
}

/// Checks if the elapsed time since `start` exceeds the TTL.
fn check_timeout(start: Instant, ttl: u64) -> bool {
    start.elapsed() > Duration::from_secs(ttl)
}

/// Simulates the Order Service. Always succeeds for this simulation.
fn order_service(_req: &OrderRequest) -> Result<(), String> {
    Ok(())
}

/// Simulates the Inventory Service.
/// If any item has an id "fail_inventory", it triggers a failure.
/// If any item is "slow_item", it simulates a slow processing (sleep for 2 seconds).
fn inventory_service(req: &OrderRequest) -> Result<(), String> {
    for (item, _) in &req.items {
        if item == "fail_inventory" {
            return Err("Inventory service failed".to_string());
        }
        if item == "slow_item" {
            thread::sleep(Duration::from_secs(2));
        }
    }
    Ok(())
}

/// Simulates the Payment Service.
/// Returns an error if payment_info equals "invalid_payment".
fn payment_service(req: &OrderRequest) -> Result<(), String> {
    if req.payment_info == "invalid_payment" {
        return Err("Payment service failed".to_string());
    }
    Ok(())
}

/// Simulates the Shipping Service. Always succeeds for this simulation.
fn shipping_service(_req: &OrderRequest) -> Result<(), String> {
    Ok(())
}

/// Compensation for Order Service.
fn order_compensate(_req: &OrderRequest) -> Result<(), String> {
    Ok(())
}

/// Compensation for Inventory Service.
fn inventory_compensate(_req: &OrderRequest) -> Result<(), String> {
    Ok(())
}

/// Compensation for Payment Service.
fn payment_compensate(_req: &OrderRequest) -> Result<(), String> {
    Ok(())
}

/// Compensation for Shipping Service.
fn shipping_compensate(_req: &OrderRequest) -> Result<(), String> {
    Ok(())
}