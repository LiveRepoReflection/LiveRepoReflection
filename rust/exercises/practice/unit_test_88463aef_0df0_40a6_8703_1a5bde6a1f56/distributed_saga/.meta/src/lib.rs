use std::thread;
use std::time::Duration;

#[derive(Debug, Clone)]
pub struct Order {
    pub order_id: u32,
    pub customer_id: u32,
    pub items: Vec<(u32, u32)>,
    pub payment_info: String,
}

#[derive(Debug, PartialEq)]
pub enum SagaError {
    InventoryError(String),
    PaymentError(String),
    ShippingError(String),
    NotificationError(String),
}

fn reserve_inventory(order: &Order) -> Result<(), SagaError> {
    // Simulate processing time.
    thread::sleep(Duration::from_millis(50));
    // If any item id is 999, simulate inventory failure.
    for (item_id, _) in &order.items {
        if *item_id == 999 {
            return Err(SagaError::InventoryError("InventoryService failed to reserve item".to_string()));
        }
    }
    Ok(())
}

fn release_inventory(order: &Order) -> Result<(), SagaError> {
    // Simulate releasing inventory, assume it always succeeds.
    thread::sleep(Duration::from_millis(30));
    Ok(())
}

fn process_payment(order: &Order) -> Result<(), SagaError> {
    // Simulate processing time.
    thread::sleep(Duration::from_millis(50));
    if order.payment_info == "fail_payment" {
        return Err(SagaError::PaymentError("PaymentService failed to process payment".to_string()));
    }
    if order.payment_info == "transient_failure_payment" {
        let max_retries = 3;
        // Simulate transient failures. Fail on the first two attempts.
        for attempt in 0..max_retries {
            if attempt < 2 {
                thread::sleep(Duration::from_millis(50));
                continue;
            } else {
                return Ok(());
            }
        }
        return Err(SagaError::PaymentError("PaymentService transient failure".to_string()));
    }
    Ok(())
}

fn refund_payment(order: &Order) -> Result<(), SagaError> {
    // Simulate refunding payment, assume it always succeeds.
    thread::sleep(Duration::from_millis(30));
    Ok(())
}

fn schedule_shipping(order: &Order) -> Result<(), SagaError> {
    // Simulate scheduling shipping.
    thread::sleep(Duration::from_millis(50));
    // For order_id 4, simulate failure in ShippingService.
    if order.order_id == 4 {
        return Err(SagaError::ShippingError("ShippingService failed to schedule shipping".to_string()));
    }
    Ok(())
}

fn cancel_shipping(order: &Order) -> Result<(), SagaError> {
    // Simulate cancelling shipping, assume it always succeeds.
    thread::sleep(Duration::from_millis(30));
    Ok(())
}

fn send_notification(order: &Order) -> Result<(), SagaError> {
    // Simulate sending notification.
    thread::sleep(Duration::from_millis(50));
    // For order_id 5, simulate failure in NotificationService.
    if order.order_id == 5 {
        return Err(SagaError::NotificationError("NotificationService failed to send notification".to_string()));
    }
    Ok(())
}

pub fn process_order(order: Order) -> Result<String, SagaError> {
    // Vector to store compensation closures in the order of execution.
    // Each closure when called performs the compensation action.
    let mut compensations: Vec<Box<dyn Fn() -> ()>> = Vec::new();

    if let Err(e) = reserve_inventory(&order) {
        return Err(e);
    } else {
        // Register compensation for inventory reservation.
        let order_clone = order.clone();
        compensations.push(Box::new(move || {
            let _ = release_inventory(&order_clone);
        }));
    }

    if let Err(e) = process_payment(&order) {
        // Execute compensations in reverse order.
        for compensate in compensations.into_iter().rev() {
            compensate();
        }
        return Err(e);
    } else {
        // Register compensation for payment processing.
        let order_clone = order.clone();
        compensations.push(Box::new(move || {
            let _ = refund_payment(&order_clone);
        }));
    }

    if let Err(e) = schedule_shipping(&order) {
        for compensate in compensations.into_iter().rev() {
            compensate();
        }
        return Err(e);
    } else {
        // Register compensation for shipping scheduling.
        let order_clone = order.clone();
        compensations.push(Box::new(move || {
            let _ = cancel_shipping(&order_clone);
        }));
    }

    if let Err(e) = send_notification(&order) {
        for compensate in compensations.into_iter().rev() {
            compensate();
        }
        return Err(e);
    }

    Ok("Order processed successfully".to_string())
}