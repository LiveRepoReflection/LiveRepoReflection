use std::cmp::Ordering;
use std::fs::File;
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug, Clone, PartialEq)]
pub enum OrderType {
    Buy,
    Sell,
}

impl OrderType {
    fn from_str(s: &str) -> Option<OrderType> {
        match s {
            "Buy" => Some(OrderType::Buy),
            "Sell" => Some(OrderType::Sell),
            _ => None,
        }
    }

    fn as_str(&self) -> &str {
        match self {
            OrderType::Buy => "Buy",
            OrderType::Sell => "Sell",
        }
    }
}

#[derive(Debug, Clone)]
pub struct Order {
    pub order_id: String,
    pub timestamp: u64,
    pub order_type: OrderType,
    pub price: u32,
    pub quantity: u64,
    pub user_id: String,
    pub signature: String,
}

impl Order {
    fn serialize(&self) -> String {
        // Format: order|order_id|timestamp|order_type|price|quantity|user_id|signature
        format!(
            "order|{}|{}|{}|{}|{}|{}|{}",
            self.order_id,
            self.timestamp,
            self.order_type.as_str(),
            self.price,
            self.quantity,
            self.user_id,
            self.signature
        )
    }

    fn deserialize(s: &str) -> Option<Order> {
        let parts: Vec<&str> = s.split('|').collect();
        if parts.len() != 8 {
            return None;
        }
        if parts[0] != "order" {
            return None;
        }
        let order_type = OrderType::from_str(parts[3])?;
        let timestamp = parts[2].parse::<u64>().ok()?;
        let price = parts[4].parse::<u32>().ok()?;
        let quantity = parts[5].parse::<u64>().ok()?;
        Some(Order {
            order_id: parts[1].to_string(),
            timestamp,
            order_type,
            price,
            quantity,
            user_id: parts[6].to_string(),
            signature: parts[7].to_string(),
        })
    }
}

#[derive(Debug, Clone)]
pub struct Trade {
    pub buy_order_id: String,
    pub sell_order_id: String,
    pub price: u32,
    pub quantity: u64,
    pub timestamp: u64,
}

impl Trade {
    fn serialize(&self) -> String {
        // Format: trade|buy_order_id|sell_order_id|price|quantity|timestamp
        format!(
            "trade|{}|{}|{}|{}|{}",
            self.buy_order_id, self.sell_order_id, self.price, self.quantity, self.timestamp
        )
    }

    fn deserialize(s: &str) -> Option<Trade> {
        let parts: Vec<&str> = s.split('|').collect();
        if parts.len() != 6 {
            return None;
        }
        if parts[0] != "trade" {
            return None;
        }
        let price = parts[3].parse::<u32>().ok()?;
        let quantity = parts[4].parse::<u64>().ok()?;
        let timestamp = parts[5].parse::<u64>().ok()?;
        Some(Trade {
            buy_order_id: parts[1].to_string(),
            sell_order_id: parts[2].to_string(),
            price,
            quantity,
            timestamp,
        })
    }
}

pub struct DexEngine {
    buy_orders: Vec<Order>,
    sell_orders: Vec<Order>,
    trades: Vec<Trade>,
}

impl DexEngine {
    pub fn new() -> DexEngine {
        DexEngine {
            buy_orders: Vec::new(),
            sell_orders: Vec::new(),
            trades: Vec::new(),
        }
    }

    fn sort_orders(&mut self) {
        // For buys: sort descending by price, then ascending by timestamp (FIFO)
        self.buy_orders.sort_by(|a, b| {
            b.price
                .cmp(&a.price)
                .then_with(|| a.timestamp.cmp(&b.timestamp))
        });

        // For sells: sort ascending by price, then ascending by timestamp (FIFO)
        self.sell_orders.sort_by(|a, b| {
            a.price
                .cmp(&b.price)
                .then_with(|| a.timestamp.cmp(&b.timestamp))
        });
    }

    pub fn submit_order(&mut self, order: Order) {
        match order.order_type {
            OrderType::Buy => {
                self.buy_orders.push(order);
            }
            OrderType::Sell => {
                self.sell_orders.push(order);
            }
        }
        self.sort_orders();
    }

    pub fn match_orders(&mut self) {
        loop {
            self.sort_orders();
            if self.buy_orders.is_empty() || self.sell_orders.is_empty() {
                break;
            }
            let best_buy = &self.buy_orders[0];
            let best_sell = &self.sell_orders[0];
            if best_buy.price >= best_sell.price {
                let trade_qty = std::cmp::min(best_buy.quantity, best_sell.quantity);
                let trade_price = best_sell.price; // Trade at sell order price
                let trade_timestamp = SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .expect("Time went backwards")
                    .as_nanos() as u64;
                let trade = Trade {
                    buy_order_id: best_buy.order_id.clone(),
                    sell_order_id: best_sell.order_id.clone(),
                    price: trade_price,
                    quantity: trade_qty,
                    timestamp: trade_timestamp,
                };
                self.trades.push(trade);

                // Update quantities
                if let Some(buy_order) = self.buy_orders.get_mut(0) {
                    if buy_order.quantity > trade_qty {
                        buy_order.quantity -= trade_qty;
                    } else {
                        // Fully filled
                        self.buy_orders.remove(0);
                    }
                }
                if let Some(sell_order) = self.sell_orders.get_mut(0) {
                    if sell_order.quantity > trade_qty {
                        sell_order.quantity -= trade_qty;
                    } else {
                        // Fully filled
                        self.sell_orders.remove(0);
                    }
                }
            } else {
                break;
            }
        }
    }

    pub fn get_trades(&self) -> Vec<Trade> {
        self.trades.clone()
    }

    pub fn get_orders(&self, order_type: OrderType) -> Vec<Order> {
        match order_type {
            OrderType::Buy => self.buy_orders.clone(),
            OrderType::Sell => self.sell_orders.clone(),
        }
    }

    pub fn cancel_order(&mut self, order_id: &str) -> bool {
        let mut found = false;
        self.buy_orders.retain(|order| {
            if order.order_id == order_id {
                found = true;
                false
            } else {
                true
            }
        });
        if found {
            return true;
        }
        self.sell_orders.retain(|order| {
            if order.order_id == order_id {
                found = true;
                false
            } else {
                true
            }
        });
        found
    }

    pub fn persist(&self, filename: &str) -> Result<(), std::io::Error> {
        let file = File::create(filename)?;
        let mut writer = BufWriter::new(file);
        // Write trades section
        writeln!(writer, "TRADES {}", self.trades.len())?;
        for trade in &self.trades {
            writeln!(writer, "{}", trade.serialize())?;
        }
        // Write buy orders section
        writeln!(writer, "BUY_ORDERS {}", self.buy_orders.len())?;
        for order in &self.buy_orders {
            writeln!(writer, "{}", order.serialize())?;
        }
        // Write sell orders section
        writeln!(writer, "SELL_ORDERS {}", self.sell_orders.len())?;
        for order in &self.sell_orders {
            writeln!(writer, "{}", order.serialize())?;
        }
        writer.flush()?;
        Ok(())
    }

    pub fn load(filename: &str) -> Result<DexEngine, std::io::Error> {
        let file = File::open(filename)?;
        let reader = BufReader::new(file);
        let mut engine = DexEngine::new();
        let mut lines = reader.lines();
        // Read TRADES line
        let trades_line = match lines.next() {
            Some(line) => line?,
            None => return Ok(engine),
        };
        let trades_count = {
            let parts: Vec<&str> = trades_line.trim().split_whitespace().collect();
            if parts.len() != 2 || parts[0] != "TRADES" {
                0usize
            } else {
                parts[1].parse::<usize>().unwrap_or(0)
            }
        };
        for _ in 0..trades_count {
            if let Some(line) = lines.next() {
                let line = line?;
                if let Some(trade) = Trade::deserialize(&line) {
                    engine.trades.push(trade);
                }
            }
        }
        // Read BUY_ORDERS line
        let buy_line = match lines.next() {
            Some(line) => line?,
            None => return Ok(engine),
        };
        let buy_count = {
            let parts: Vec<&str> = buy_line.trim().split_whitespace().collect();
            if parts.len() != 2 || parts[0] != "BUY_ORDERS" {
                0usize
            } else {
                parts[1].parse::<usize>().unwrap_or(0)
            }
        };
        for _ in 0..buy_count {
            if let Some(line) = lines.next() {
                let line = line?;
                if let Some(order) = Order::deserialize(&line) {
                    engine.buy_orders.push(order);
                }
            }
        }
        // Read SELL_ORDERS line
        let sell_line = match lines.next() {
            Some(line) => line?,
            None => return Ok(engine),
        };
        let sell_count = {
            let parts: Vec<&str> = sell_line.trim().split_whitespace().collect();
            if parts.len() != 2 || parts[0] != "SELL_ORDERS" {
                0usize
            } else {
                parts[1].parse::<usize>().unwrap_or(0)
            }
        };
        for _ in 0..sell_count {
            if let Some(line) = lines.next() {
                let line = line?;
                if let Some(order) = Order::deserialize(&line) {
                    engine.sell_orders.push(order);
                }
            }
        }
        engine.sort_orders();
        Ok(engine)
    }
}