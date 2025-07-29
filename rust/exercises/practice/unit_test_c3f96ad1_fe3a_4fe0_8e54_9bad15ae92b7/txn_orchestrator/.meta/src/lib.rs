pub struct InventoryService {
    failure_rate: f64,
}

impl InventoryService {
    pub fn new(f: f64) -> Self {
        InventoryService { failure_rate: f }
    }

    pub fn reserve(&self, item_id: u32, quantity: u32) -> Result<(), String> {
        if self.failure_rate >= 1.0 {
            Err(format!("Inventory failure on reserve for item {}", item_id))
        } else {
            Ok(())
        }
    }

    pub fn rollback_reserve(&self, item_id: u32, _quantity: u32) -> Result<(), String> {
        if self.failure_rate >= 1.0 {
            Err(format!("Inventory rollback failure for item {}", item_id))
        } else {
            Ok(())
        }
    }
}

pub struct PaymentService {
    failure_rate: f64,
}

impl PaymentService {
    pub fn new(f: f64) -> Self {
        PaymentService { failure_rate: f }
    }

    pub fn charge(&self, user_id: u32, amount: u32) -> Result<(), String> {
        if self.failure_rate >= 1.0 {
            Err(format!("Payment failure on charge for user {}", user_id))
        } else {
            Ok(())
        }
    }

    pub fn refund(&self, user_id: u32, amount: u32) -> Result<(), String> {
        if self.failure_rate >= 1.0 {
            Err(format!("Payment refund failure for user {}", user_id))
        } else {
            Ok(())
        }
    }
}

pub struct OrderService {
    failure_rate: f64,
    order_count: u32,
}

impl OrderService {
    pub fn new(f: f64) -> Self {
        OrderService { failure_rate: f, order_count: 0 }
    }

    pub fn create_order(&mut self, user_id: u32, items: &[(u32, u32)]) -> Result<u32, String> {
        if self.failure_rate >= 1.0 {
            Err(format!("Order creation failure for user {}", user_id))
        } else {
            self.order_count += 1;
            Ok(self.order_count)
        }
    }

    pub fn cancel_order(&self, order_id: u32) -> Result<(), String> {
        if self.failure_rate >= 1.0 {
            Err(format!("Order cancellation failure for order {}", order_id))
        } else {
            Ok(())
        }
    }
}

pub struct TransactionOrchestrator {
    inventory: InventoryService,
    payment: PaymentService,
    order: OrderService,
}

impl TransactionOrchestrator {
    pub fn new(inventory: InventoryService, payment: PaymentService, order: OrderService) -> Self {
        TransactionOrchestrator {
            inventory,
            payment,
            order,
        }
    }

    pub fn execute_transaction(&mut self, user_id: u32, items: Vec<(u32, u32)>, amount: u32) -> Result<u32, String> {
        let mut reserved_items: Vec<(u32, u32)> = Vec::new();

        for (item_id, qty) in &items {
            match self.inventory.reserve(*item_id, *qty) {
                Ok(()) => reserved_items.push((*item_id, *qty)),
                Err(e) => {
                    for (r_item, r_qty) in reserved_items.iter().rev() {
                        if let Err(roll_err) = self.inventory.rollback_reserve(*r_item, *r_qty) {
                            println!("Rollback error: {}", roll_err);
                        }
                    }
                    return Err(format!("Inventory error: {}", e));
                }
            }
        }

        if let Err(e) = self.payment.charge(user_id, amount) {
            for (r_item, r_qty) in reserved_items.iter().rev() {
                if let Err(roll_err) = self.inventory.rollback_reserve(*r_item, *r_qty) {
                    println!("Rollback error: {}", roll_err);
                }
            }
            return Err(format!("Payment error: {}", e));
        }

        let order_id = match self.order.create_order(user_id, &items) {
            Ok(id) => id,
            Err(e) => {
                if let Err(refund_err) = self.payment.refund(user_id, amount) {
                    println!("Refund error: {}", refund_err);
                }
                for (r_item, r_qty) in reserved_items.iter().rev() {
                    if let Err(roll_err) = self.inventory.rollback_reserve(*r_item, *r_qty) {
                        println!("Rollback error: {}", roll_err);
                    }
                }
                return Err(format!("Order error: {}", e));
            }
        };

        Ok(order_id)
    }
}