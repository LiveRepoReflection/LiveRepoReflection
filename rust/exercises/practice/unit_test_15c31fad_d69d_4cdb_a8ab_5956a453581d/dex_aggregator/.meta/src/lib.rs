use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq)]
pub enum Side {
    Bid,
    Ask,
}

#[derive(Debug, Clone, PartialEq)]
pub struct Order {
    pub side: Side,
    pub price: u32,
    pub quantity: u32,
}

#[derive(Debug, Clone, PartialEq)]
pub struct OrderBook {
    pub bids: Vec<Order>,
    pub asks: Vec<Order>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct TradePlan {
    pub instructions: Vec<(String, u32, u32)>, // (dex_id, allocated quantity, original price)
}

pub struct DexAggregator {
    order_books: HashMap<String, OrderBook>,
    fees: HashMap<String, u32>, // Fee per DEX
}

impl DexAggregator {
    pub fn new() -> Self {
        Self {
            order_books: HashMap::new(),
            fees: HashMap::new(),
        }
    }

    pub fn update_order_book(&mut self, dex_id: String, order_book: OrderBook) {
        self.order_books.insert(dex_id, order_book);
    }

    pub fn remove_order_book(&mut self, dex_id: &str) {
        self.order_books.remove(dex_id);
        self.fees.remove(dex_id);
    }

    pub fn set_fee(&mut self, dex_id: String, fee: u32) {
        self.fees.insert(dex_id, fee);
    }

    pub fn aggregate_order_books(&self) -> OrderBook {
        let mut all_bids: Vec<Order> = Vec::new();
        let mut all_asks: Vec<Order> = Vec::new();
        for order_book in self.order_books.values() {
            all_bids.extend(order_book.bids.clone());
            all_asks.extend(order_book.asks.clone());
        }
        // For bids, sort descending by price.
        all_bids.sort_by(|a, b| b.price.cmp(&a.price));
        // For asks, sort ascending by price.
        all_asks.sort_by(|a, b| a.price.cmp(&b.price));
        OrderBook {
            bids: all_bids,
            asks: all_asks,
        }
    }

    pub fn route_order(&self, order: Order, slippage_tolerance: f64) -> Result<TradePlan, String> {
        match order.side {
            Side::Ask => {
                // For buying, we use the ask side orders. Effective price = price + fee.
                let mut candidates: Vec<(String, u32, u32, u32)> = Vec::new();
                for (dex_id, order_book) in self.order_books.iter() {
                    let fee = *self.fees.get(dex_id).unwrap_or(&0);
                    for ask in &order_book.asks {
                        candidates.push((dex_id.clone(), ask.price, ask.quantity, fee));
                    }
                }
                // Sort candidates by effective price (price + fee) in ascending order.
                candidates.sort_by(|a, b| {
                    let effective_a = a.1 + a.3;
                    let effective_b = b.1 + b.3;
                    effective_a.cmp(&effective_b)
                });
                let mut remaining = order.quantity;
                let mut instructions: Vec<(String, u32, u32)> = Vec::new();
                let mut total_cost: u64 = 0;
                let mut total_allocated: u32 = 0;
                let mut best_effective: Option<u32> = None;
                for (dex_id, price, available, fee) in candidates {
                    if remaining == 0 {
                        break;
                    }
                    let take = if available >= remaining { remaining } else { available };
                    let effective_price = price + fee;
                    if best_effective.is_none() {
                        best_effective = Some(effective_price);
                    }
                    instructions.push((dex_id, take, price));
                    total_cost += (effective_price as u64) * (take as u64);
                    total_allocated += take;
                    remaining -= take;
                }
                if total_allocated < order.quantity {
                    return Err("Not enough liquidity".to_string());
                }
                let weighted_avg = total_cost as f64 / total_allocated as f64;
                let best = best_effective.ok_or("No available orders".to_string())?;
                if weighted_avg > (best as f64 * (1.0 + slippage_tolerance)) {
                    return Err("Slippage tolerance exceeded".to_string());
                }
                Ok(TradePlan { instructions })
            }
            Side::Bid => {
                // For selling, we use the bid side orders. Effective price = price - fee.
                let mut candidates: Vec<(String, u32, u32, u32)> = Vec::new();
                for (dex_id, order_book) in self.order_books.iter() {
                    let fee = *self.fees.get(dex_id).unwrap_or(&0);
                    for bid in &order_book.bids {
                        candidates.push((dex_id.clone(), bid.price, bid.quantity, fee));
                    }
                }
                // Sort candidates by effective price (price - fee) in descending order.
                candidates.sort_by(|a, b| {
                    let effective_a = a.1.saturating_sub(a.3);
                    let effective_b = b.1.saturating_sub(b.3);
                    effective_b.cmp(&effective_a)
                });
                let mut remaining = order.quantity;
                let mut instructions: Vec<(String, u32, u32)> = Vec::new();
                let mut total_gain: u64 = 0;
                let mut total_allocated: u32 = 0;
                let mut best_effective: Option<u32> = None;
                for (dex_id, price, available, fee) in candidates {
                    if remaining == 0 {
                        break;
                    }
                    let take = if available >= remaining { remaining } else { available };
                    let effective_price = price.saturating_sub(fee);
                    if best_effective.is_none() {
                        best_effective = Some(effective_price);
                    }
                    instructions.push((dex_id, take, price));
                    total_gain += (effective_price as u64) * (take as u64);
                    total_allocated += take;
                    remaining -= take;
                }
                if total_allocated < order.quantity {
                    return Err("Not enough liquidity".to_string());
                }
                let weighted_avg = total_gain as f64 / total_allocated as f64;
                let best = best_effective.ok_or("No available orders".to_string())?;
                if weighted_avg < (best as f64 * (1.0 - slippage_tolerance)) {
                    return Err("Slippage tolerance exceeded".to_string());
                }
                Ok(TradePlan { instructions })
            }
        }
    }
}