use std::collections::{BTreeMap, VecDeque};

#[derive(Debug, Clone, PartialEq)]
pub enum OrderSide {
    Buy,
    Sell,
}

#[derive(Debug, Clone, PartialEq)]
pub enum OrderAction {
    New,
    Cancel,
}

#[derive(Debug, Clone)]
pub struct OrderEvent {
    pub timestamp: u64,
    pub order_id: String,
    pub user_id: String,
    pub side: OrderSide,
    pub price: u64,
    pub quantity: u64,
    pub action: OrderAction,
}

#[derive(Debug, Clone, PartialEq)]
pub struct TradeEvent {
    pub timestamp: u64,
    pub buy_order_id: String,
    pub sell_order_id: String,
    pub price: u64,
    pub quantity: u64,
}

#[derive(Debug, Clone)]
struct Order {
    order_id: String,
    user_id: String,
    price: u64,
    quantity: u64,
    timestamp: u64,
}

pub struct OrderMatcher {
    // For buy orders, key: price, value: orders in FIFO order.
    // Buy orders are stored in a BTreeMap in ascending order.
    // We'll iterate in reverse order for matching (highest price first).
    buy_orders: BTreeMap<u64, VecDeque<Order>>,
    // For sell orders, key: price, value: orders in FIFO order.
    sell_orders: BTreeMap<u64, VecDeque<Order>>,
}

impl OrderMatcher {
    pub fn new() -> Self {
        OrderMatcher {
            buy_orders: BTreeMap::new(),
            sell_orders: BTreeMap::new(),
        }
    }

    pub fn process_event(&mut self, event: OrderEvent) -> Vec<TradeEvent> {
        match event.action {
            OrderAction::New => self.process_new_order(event),
            OrderAction::Cancel => {
                self.cancel_order(&event.order_id);
                Vec::new()
            }
        }
    }

    fn process_new_order(&mut self, event: OrderEvent) -> Vec<TradeEvent> {
        let mut trades: Vec<TradeEvent> = Vec::new();
        let mut new_order = Order {
            order_id: event.order_id,
            user_id: event.user_id,
            price: event.price,
            quantity: event.quantity,
            timestamp: event.timestamp,
        };

        match event.side {
            OrderSide::Buy => {
                // For a buy order, match against sell orders with price <= buy price.
                // Iterate sell_orders in ascending order.
                let mut prices_to_remove = Vec::new();
                // Get all sell prices that are <= new_order.price
                for (&sell_price, queue) in self.sell_orders.range_mut(..=new_order.price) {
                    while new_order.quantity > 0 && !queue.is_empty() {
                        // Peek the first sell order in FIFO order.
                        let mut sell_order = queue.pop_front().unwrap();
                        // Determine trade quantity.
                        let trade_qty = if new_order.quantity < sell_order.quantity {
                            new_order.quantity
                        } else {
                            sell_order.quantity
                        };
                        // Record trade event with timestamp from the incoming order.
                        trades.push(TradeEvent {
                            timestamp: new_order.timestamp,
                            buy_order_id: new_order.order_id.clone(),
                            sell_order_id: sell_order.order_id.clone(),
                            price: sell_order.price,
                            quantity: trade_qty,
                        });
                        // Update quantities.
                        new_order.quantity -= trade_qty;
                        sell_order.quantity -= trade_qty;
                        // If the sell order is partially filled, push it back at front.
                        if sell_order.quantity > 0 {
                            queue.push_front(sell_order);
                        }
                    }
                    // If the queue is empty after matching, mark the price level for removal.
                    if queue.is_empty() {
                        prices_to_remove.push(sell_price);
                    }
                    if new_order.quantity == 0 {
                        break;
                    }
                }
                // Clean up empty price levels.
                for price in prices_to_remove {
                    self.sell_orders.remove(&price);
                }
                // If there is remaining quantity, add the order to the buy order book.
                if new_order.quantity > 0 {
                    self.add_order(OrderSide::Buy, new_order);
                }
            }
            OrderSide::Sell => {
                // For a sell order, match against buy orders with price >= sell price.
                // Iterate buy_orders in descending order.
                let mut prices_to_remove = Vec::new();
                // Collect keys in descending order that are >= new_order.price.
                let matching_prices: Vec<u64> = self.buy_orders
                    .range(new_order.price..)
                    .map(|(&price, _)| price)
                    .collect();
                for buy_price in matching_prices.into_iter().rev() {
                    if new_order.quantity == 0 {
                        break;
                    }
                    if let Some(queue) = self.buy_orders.get_mut(&buy_price) {
                        while new_order.quantity > 0 && !queue.is_empty() {
                            let mut buy_order = queue.pop_front().unwrap();
                            let trade_qty = if new_order.quantity < buy_order.quantity {
                                new_order.quantity
                            } else {
                                buy_order.quantity
                            };
                            trades.push(TradeEvent {
                                timestamp: new_order.timestamp,
                                buy_order_id: buy_order.order_id.clone(),
                                sell_order_id: new_order.order_id.clone(),
                                price: buy_order.price,
                                quantity: trade_qty,
                            });
                            new_order.quantity -= trade_qty;
                            buy_order.quantity -= trade_qty;
                            if buy_order.quantity > 0 {
                                queue.push_front(buy_order);
                            }
                        }
                        if queue.is_empty() {
                            prices_to_remove.push(buy_price);
                        }
                    }
                }
                for price in prices_to_remove {
                    self.buy_orders.remove(&price);
                }
                if new_order.quantity > 0 {
                    self.add_order(OrderSide::Sell, new_order);
                }
            }
        }
        trades
    }

    fn add_order(&mut self, side: OrderSide, order: Order) {
        match side {
            OrderSide::Buy => {
                self.buy_orders
                    .entry(order.price)
                    .or_insert_with(VecDeque::new)
                    .push_back(order);
            }
            OrderSide::Sell => {
                self.sell_orders
                    .entry(order.price)
                    .or_insert_with(VecDeque::new)
                    .push_back(order);
            }
        }
    }

    fn cancel_order(&mut self, order_id: &str) {
        // Attempt to remove from buy orders.
        for (_price, queue) in self.buy_orders.iter_mut() {
            if let Some(pos) = queue.iter().position(|order| order.order_id == order_id) {
                queue.remove(pos);
                return;
            }
        }
        // Attempt to remove from sell orders.
        for (_price, queue) in self.sell_orders.iter_mut() {
            if let Some(pos) = queue.iter().position(|order| order.order_id == order_id) {
                queue.remove(pos);
                return;
            }
        }
    }
}