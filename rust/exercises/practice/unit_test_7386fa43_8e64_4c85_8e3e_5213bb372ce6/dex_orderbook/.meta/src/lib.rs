use std::collections::{BTreeMap, BTreeSet, HashMap};

#[derive(Debug, Clone)]
pub struct Order {
    pub order_id: String,
    pub price: u32,
    pub quantity: u32,
    pub order_type: String,
    pub timestamp: u64,
}

pub struct OrderBook {
    orders: HashMap<String, Order>,
    // Map from price to (buy_quantity, sell_quantity)
    quantity_map: BTreeMap<u32, (u32, u32)>,
    // For recent orders: store (timestamp, order_id)
    recent_buys: BTreeSet<(u64, String)>,
    recent_sells: BTreeSet<(u64, String)>,
}

impl OrderBook {
    pub fn new() -> Self {
        OrderBook {
            orders: HashMap::new(),
            quantity_map: BTreeMap::new(),
            recent_buys: BTreeSet::new(),
            recent_sells: BTreeSet::new(),
        }
    }

    pub fn add_order(&mut self, order_id: String, price: u32, quantity: u32, order_type: String, timestamp: u64) -> Result<(), String> {
        if self.orders.contains_key(&order_id) {
            return Err("Order ID already exists".to_string());
        }
        if order_type != "buy" && order_type != "sell" {
            return Err("Invalid order type".to_string());
        }
        let order = Order {
            order_id: order_id.clone(),
            price,
            quantity,
            order_type: order_type.clone(),
            timestamp,
        };
        self.orders.insert(order_id.clone(), order);

        // Update aggregated quantity information
        self.quantity_map
            .entry(price)
            .and_modify(|e| {
                if order_type == "buy" {
                    e.0 = e.0.saturating_add(quantity);
                } else {
                    e.1 = e.1.saturating_add(quantity);
                }
            })
            .or_insert(if order_type == "buy" {
                (quantity, 0)
            } else {
                (0, quantity)
            });

        // Insert in recency data structures
        if order_type == "buy" {
            self.recent_buys.insert((timestamp, order_id));
        } else {
            self.recent_sells.insert((timestamp, order_id));
        }
        Ok(())
    }

    pub fn cancel_order(&mut self, order_id: String) -> Result<(), String> {
        let order = self.orders.remove(&order_id);
        if let Some(order) = order {
            let entry = self.quantity_map.get_mut(&order.price);
            if let Some((buy_qty, sell_qty)) = entry {
                if order.order_type == "buy" {
                    if *buy_qty < order.quantity {
                        *buy_qty = 0;
                    } else {
                        *buy_qty -= order.quantity;
                    }
                } else {
                    if *sell_qty < order.quantity {
                        *sell_qty = 0;
                    } else {
                        *sell_qty -= order.quantity;
                    }
                }
                // Remove price level if both quantities become zero
                if *buy_qty == 0 && *sell_qty == 0 {
                    self.quantity_map.remove(&order.price);
                }
            }
            // Remove from recency data structures
            if order.order_type == "buy" {
                self.recent_buys.remove(&(order.timestamp, order_id));
            } else {
                self.recent_sells.remove(&(order.timestamp, order_id));
            }
            Ok(())
        } else {
            Err("Order ID does not exist".to_string())
        }
    }

    pub fn get_quantity_at_price(&self, price: u32) -> Result<(u32, u32), String> {
        if let Some(&(buy_qty, sell_qty)) = self.quantity_map.get(&price) {
            Ok((buy_qty, sell_qty))
        } else {
            Err("No orders at the given price level".to_string())
        }
    }

    pub fn get_recent_orders(&self, n: usize) -> Result<(Vec<Order>, Vec<Order>), String> {
        let mut recent_buys: Vec<Order> = Vec::new();
        let mut recent_sells: Vec<Order> = Vec::new();

        // Iterate over recent_buys in descending order (i.e., newest first)
        for &(timestamp, ref order_id) in self.recent_buys.iter().rev() {
            if recent_buys.len() >= n {
                break;
            }
            if let Some(order) = self.orders.get(order_id) {
                recent_buys.push(order.clone());
            }
        }

        for &(timestamp, ref order_id) in self.recent_sells.iter().rev() {
            if recent_sells.len() >= n {
                break;
            }
            if let Some(order) = self.orders.get(order_id) {
                recent_sells.push(order.clone());
            }
        }

        Ok((recent_buys, recent_sells))
    }

    pub fn get_weighted_average_price(&self, min_price: u32, max_price: u32) -> Result<(f64, f64), String> {
        let mut buy_total_weight: u64 = 0;
        let mut buy_total_qty: u64 = 0;
        let mut sell_total_weight: u64 = 0;
        let mut sell_total_qty: u64 = 0;

        for (&price, &(buy_qty, sell_qty)) in self.quantity_map.range(min_price..=max_price) {
            buy_total_weight += (price as u64) * (buy_qty as u64);
            buy_total_qty += buy_qty as u64;
            sell_total_weight += (price as u64) * (sell_qty as u64);
            sell_total_qty += sell_qty as u64;
        }

        let buy_wap = if buy_total_qty > 0 {
            buy_total_weight as f64 / buy_total_qty as f64
        } else {
            0.0
        };
        let sell_wap = if sell_total_qty > 0 {
            sell_total_weight as f64 / sell_total_qty as f64
        } else {
            0.0
        };

        Ok((buy_wap, sell_wap))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add_and_query_quantity() {
        let mut ob = OrderBook::new();
        let res1 = ob.add_order("order1".to_string(), 100, 10, "buy".to_string(), 1);
        assert!(res1.is_ok());
        let res2 = ob.add_order("order2".to_string(), 100, 5, "sell".to_string(), 2);
        assert!(res2.is_ok());

        let qty_result = ob.get_quantity_at_price(100);
        assert!(qty_result.is_ok());
        let (buy_qty, sell_qty) = qty_result.unwrap();
        assert_eq!(buy_qty, 10);
        assert_eq!(sell_qty, 5);
    }

    #[test]
    fn test_cancel_order() {
        let mut ob = OrderBook::new();
        assert!(ob.add_order("order1".to_string(), 101, 10, "buy".to_string(), 1).is_ok());
        assert!(ob.add_order("order2".to_string(), 101, 15, "buy".to_string(), 2).is_ok());

        let cancel_res = ob.cancel_order("order1".to_string());
        assert!(cancel_res.is_ok());

        let qty_result = ob.get_quantity_at_price(101);
        assert!(qty_result.is_ok());
        let (buy_qty, sell_qty) = qty_result.unwrap();
        assert_eq!(buy_qty, 15);
        assert_eq!(sell_qty, 0);
    }

    #[test]
    fn test_get_recent_orders() {
        let mut ob = OrderBook::new();
        assert!(ob.add_order("order1".to_string(), 102, 10, "buy".to_string(), 1).is_ok());
        assert!(ob.add_order("order2".to_string(), 103, 20, "sell".to_string(), 2).is_ok());
        assert!(ob.add_order("order3".to_string(), 104, 30, "buy".to_string(), 3).is_ok());
        assert!(ob.add_order("order4".to_string(), 105, 40, "sell".to_string(), 4).is_ok());
        assert!(ob.add_order("order5".to_string(), 106, 50, "buy".to_string(), 5).is_ok());
        assert!(ob.add_order("order6".to_string(), 107, 60, "sell".to_string(), 6).is_ok());

        let recent_result = ob.get_recent_orders(2);
        assert!(recent_result.is_ok());
        let (recent_buys, recent_sells) = recent_result.unwrap();

        assert_eq!(recent_buys.len(), 2);
        assert_eq!(recent_buys[0].order_id, "order5");
        assert_eq!(recent_buys[1].order_id, "order3");

        assert_eq!(recent_sells.len(), 2);
        assert_eq!(recent_sells[0].order_id, "order6");
        assert_eq!(recent_sells[1].order_id, "order4");
    }

    #[test]
    fn test_get_weighted_average_price() {
        let mut ob = OrderBook::new();
        assert!(ob.add_order("order1".to_string(), 100, 10, "buy".to_string(), 1).is_ok());
        assert!(ob.add_order("order2".to_string(), 105, 20, "buy".to_string(), 2).is_ok());

        assert!(ob.add_order("order3".to_string(), 100, 5, "sell".to_string(), 3).is_ok());
        assert!(ob.add_order("order4".to_string(), 105, 15, "sell".to_string(), 4).is_ok());

        let wap_result = ob.get_weighted_average_price(100, 105);
        assert!(wap_result.is_ok());
        let (buy_wap, sell_wap) = wap_result.unwrap();

        let expected_buy = (100 * 10 + 105 * 20) as f64 / 30.0;
        let expected_sell = (100 * 5 + 105 * 15) as f64 / 20.0;

        assert!((buy_wap - expected_buy).abs() < 1e-5);
        assert!((sell_wap - expected_sell).abs() < 1e-5);
    }

    #[test]
    fn test_no_orders_in_range() {
        let mut ob = OrderBook::new();
        let wap_result = ob.get_weighted_average_price(50, 60);
        assert!(wap_result.is_ok());
        let (buy_wap, sell_wap) = wap_result.unwrap();
        assert_eq!(buy_wap, 0.0);
        assert_eq!(sell_wap, 0.0);
    }

    #[test]
    fn test_cancel_nonexistent_order() {
        let mut ob = OrderBook::new();
        let result = ob.cancel_order("nonexistent".to_string());
        assert!(result.is_err());
    }

    #[test]
    fn test_duplicate_order_id() {
        let mut ob = OrderBook::new();
        assert!(ob.add_order("order1".to_string(), 110, 10, "buy".to_string(), 1).is_ok());
        let duplicate = ob.add_order("order1".to_string(), 110, 15, "sell".to_string(), 2);
        assert!(duplicate.is_err());
    }

    #[test]
    fn test_get_recent_orders_empty() {
        let mut ob = OrderBook::new();
        let recent_result = ob.get_recent_orders(5);
        assert!(recent_result.is_ok());
        let (recent_buys, recent_sells) = recent_result.unwrap();
        assert!(recent_buys.is_empty());
        assert!(recent_sells.is_empty());
    }

    #[test]
    fn test_get_quantity_no_orders() {
        let mut ob = OrderBook::new();
        let result = ob.get_quantity_at_price(999);
        assert!(result.is_err());
    }
}