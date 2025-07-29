use std::cmp::Ordering;

#[derive(Clone, Debug, PartialEq)]
pub enum OrderType {
    Buy,
    Sell,
}

#[derive(Clone, Debug, PartialEq)]
pub struct Order {
    pub id: u64,
    pub order_type: OrderType,
    pub price: f64,
    pub quantity: u64,
}

#[derive(Clone, Debug, PartialEq)]
pub struct Trade {
    pub buy_order_id: u64,
    pub sell_order_id: u64,
    pub price: f64,
    pub quantity: u64,
}

#[derive(Clone, Debug)]
pub struct OrderBookState {
    pub buy_orders: Vec<Order>,
    pub sell_orders: Vec<Order>,
}

#[derive(Clone, Debug)]
pub struct OrderBook {
    pub buy_orders: Vec<Order>,
    pub sell_orders: Vec<Order>,
}

impl OrderBook {
    pub fn new() -> Self {
        OrderBook {
            buy_orders: Vec::new(),
            sell_orders: Vec::new(),
        }
    }

    pub fn add_order(&mut self, mut order: Order) -> Result<Vec<Trade>, String> {
        let mut trades = Vec::new();
        if order.order_type == OrderType::Buy {
            let mut i = 0;
            while order.quantity > 0 && i < self.sell_orders.len() {
                if order.price >= self.sell_orders[i].price {
                    let match_qty = std::cmp::min(order.quantity, self.sell_orders[i].quantity);
                    trades.push(Trade {
                        buy_order_id: order.id,
                        sell_order_id: self.sell_orders[i].id,
                        price: self.sell_orders[i].price,
                        quantity: match_qty,
                    });
                    order.quantity -= match_qty;
                    self.sell_orders[i].quantity -= match_qty;
                    if self.sell_orders[i].quantity == 0 {
                        self.sell_orders.remove(i);
                        continue;
                    }
                }
                i += 1;
            }
            if order.quantity > 0 {
                self.buy_orders.push(order);
                self.buy_orders.sort_by(|a, b| {
                    b.price
                        .partial_cmp(&a.price)
                        .unwrap_or(Ordering::Equal)
                        .then(a.id.cmp(&b.id))
                });
            }
        } else {
            let mut i = 0;
            while order.quantity > 0 && i < self.buy_orders.len() {
                if order.price <= self.buy_orders[i].price {
                    let match_qty = std::cmp::min(order.quantity, self.buy_orders[i].quantity);
                    trades.push(Trade {
                        buy_order_id: self.buy_orders[i].id,
                        sell_order_id: order.id,
                        price: self.buy_orders[i].price,
                        quantity: match_qty,
                    });
                    order.quantity -= match_qty;
                    self.buy_orders[i].quantity -= match_qty;
                    if self.buy_orders[i].quantity == 0 {
                        self.buy_orders.remove(i);
                        continue;
                    }
                }
                i += 1;
            }
            if order.quantity > 0 {
                self.sell_orders.push(order);
                self.sell_orders.sort_by(|a, b| {
                    a.price
                        .partial_cmp(&b.price)
                        .unwrap_or(Ordering::Equal)
                        .then(a.id.cmp(&b.id))
                });
            }
        }
        Ok(trades)
    }

    pub fn cancel_order(&mut self, order_id: u64) -> bool {
        if let Some(pos) = self.buy_orders.iter().position(|o| o.id == order_id) {
            self.buy_orders.remove(pos);
            return true;
        }
        if let Some(pos) = self.sell_orders.iter().position(|o| o.id == order_id) {
            self.sell_orders.remove(pos);
            return true;
        }
        false
    }

    pub fn get_state(&self) -> OrderBookState {
        OrderBookState {
            buy_orders: self.buy_orders.clone(),
            sell_orders: self.sell_orders.clone(),
        }
    }

    pub fn persist(&self) -> std::io::Result<()> {
        use std::fs::File;
        use std::io::Write;
        let mut file = File::create("orderbook_state.txt")?;
        writeln!(file, "BUY")?;
        for order in &self.buy_orders {
            writeln!(file, "{} {} {}", order.id, order.price, order.quantity)?;
        }
        writeln!(file, "SELL")?;
        for order in &self.sell_orders {
            writeln!(file, "{} {} {}", order.id, order.price, order.quantity)?;
        }
        Ok(())
    }

    pub fn recover() -> std::io::Result<Self> {
        use std::fs::File;
        use std::io::{BufReader, BufRead};
        let file = File::open("orderbook_state.txt")?;
        let reader = BufReader::new(file);
        let mut buy_orders = Vec::new();
        let mut sell_orders = Vec::new();
        let mut section = "";
        for line in reader.lines() {
            let line = line?;
            if line.trim().is_empty() {
                continue;
            }
            if line.trim() == "BUY" {
                section = "BUY";
                continue;
            }
            if line.trim() == "SELL" {
                section = "SELL";
                continue;
            }
            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() != 3 {
                continue;
            }
            let id: u64 = parts[0].parse().unwrap_or(0);
            let price: f64 = parts[1].parse().unwrap_or(0.0);
            let quantity: u64 = parts[2].parse().unwrap_or(0);
            let order = Order {
                id,
                order_type: if section == "BUY" {
                    OrderType::Buy
                } else {
                    OrderType::Sell
                },
                price,
                quantity,
            };
            if section == "BUY" {
                buy_orders.push(order);
            } else {
                sell_orders.push(order);
            }
        }
        buy_orders.sort_by(|a, b| {
            b.price
                .partial_cmp(&a.price)
                .unwrap_or(Ordering::Equal)
                .then(a.id.cmp(&b.id))
        });
        sell_orders.sort_by(|a, b| {
            a.price
                .partial_cmp(&b.price)
                .unwrap_or(Ordering::Equal)
                .then(a.id.cmp(&b.id))
        });
        Ok(OrderBook { buy_orders, sell_orders })
    }
}