use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq)]
pub enum OrderSide {
    Bid,
    Ask,
}

#[derive(Debug, Clone, PartialEq)]
pub struct Order {
    pub provider_id: String,
    pub price: i32,
    pub quantity: i32,
    pub side: OrderSide,
}

impl Order {
    pub fn new(provider_id: String, price: i32, quantity: i32, side: OrderSide) -> Self {
        Self {
            provider_id,
            price,
            quantity,
            side,
        }
    }
}

pub struct OrderAggregator {
    providers: HashMap<String, Vec<Order>>,
}

impl OrderAggregator {
    pub fn new() -> Self {
        Self {
            providers: HashMap::new(),
        }
    }

    pub fn update_provider(&mut self, provider_id: String, orders: Vec<Order>) {
        self.providers.insert(provider_id, orders);
    }

    pub fn remove_provider(&mut self, provider_id: &str) {
        self.providers.remove(provider_id);
    }

    pub fn get_top_of_book(&self) -> Result<(Option<i32>, Option<i32>), String> {
        let mut best_bid: Option<i32> = None;
        let mut best_ask: Option<i32> = None;

        for orders in self.providers.values() {
            for order in orders {
                match order.side {
                    OrderSide::Bid => {
                        if best_bid.map_or(true, |bid| order.price > bid) {
                            best_bid = Some(order.price);
                        }
                    }
                    OrderSide::Ask => {
                        if best_ask.map_or(true, |ask| order.price < ask) {
                            best_ask = Some(order.price);
                        }
                    }
                }
            }
        }
        Ok((best_bid, best_ask))
    }

    pub fn get_orders(&self, min_price: i32, max_price: i32, min_quantity: i32) -> Result<Vec<Order>, String> {
        let mut result = Vec::new();
        for orders in self.providers.values() {
            for order in orders {
                if order.price >= min_price && order.price <= max_price && order.quantity >= min_quantity {
                    result.push(order.clone());
                }
            }
        }
        Ok(result)
    }
}