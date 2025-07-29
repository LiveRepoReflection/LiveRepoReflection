use std::collections::HashMap;
use std::time::{Duration, Instant};

#[derive(Clone, Debug, PartialEq)]
pub struct Order {
    pub order_id: u128,
    pub is_bid: bool,
    pub price: u64,
    pub quantity: u64,
}

#[derive(Clone, Debug)]
pub enum Message {
    AddOrder {
        order_id: u128,
        is_bid: bool,
        price: u64,
        quantity: u64,
        timestamp: Instant,
    },
    CancelOrder {
        order_id: u128,
        timestamp: Instant,
    },
    ExecuteOrder {
        order_id: u128,
        executed_quantity: u64,
        timestamp: Instant,
    },
}

impl Message {
    fn timestamp(&self) -> Instant {
        match self {
            Message::AddOrder { timestamp, .. } => *timestamp,
            Message::CancelOrder { timestamp, .. } => *timestamp,
            Message::ExecuteOrder { timestamp, .. } => *timestamp,
        }
    }
}

pub fn reconcile_order_books(
    primary: Vec<Order>,
    secondary: Vec<Order>,
    messages: Vec<Message>,
    time_window: Duration,
) -> (Vec<Order>, Vec<Order>) {
    // Build initial order map from primary and secondary.
    let mut order_map: HashMap<u128, Order> = HashMap::new();
    for ord in primary.into_iter() {
        order_map.insert(ord.order_id, ord);
    }
    for ord in secondary.into_iter() {
        // Only add if not already present in primary.
        order_map.entry(ord.order_id).or_insert(ord);
    }

    // Determine the maximum timestamp from messages.
    let max_timestamp = messages
        .iter()
        .map(|msg| msg.timestamp())
        .max()
        .unwrap_or_else(Instant::now);
    // Calculate lower bound for messages to be processed.
    let lower_bound = max_timestamp - time_window;

    // Process messages in chronological order.
    for msg in messages.into_iter() {
        if msg.timestamp() < lower_bound {
            continue;
        }
        match msg {
            Message::AddOrder {
                order_id,
                is_bid,
                price,
                quantity,
                ..
            } => {
                // Add only if the order does not exist.
                if !order_map.contains_key(&order_id) {
                    order_map.insert(
                        order_id,
                        Order {
                            order_id,
                            is_bid,
                            price,
                            quantity,
                        },
                    );
                }
            }
            Message::CancelOrder { order_id, .. } => {
                order_map.remove(&order_id);
            }
            Message::ExecuteOrder {
                order_id,
                executed_quantity,
                ..
            } => {
                if let Some(order) = order_map.get_mut(&order_id) {
                    // Prevent underflow.
                    if executed_quantity >= order.quantity {
                        order_map.remove(&order_id);
                    } else {
                        order.quantity -= executed_quantity;
                    }
                }
            }
        }
    }

    // Separate orders into bids and asks.
    let mut bids: Vec<Order> = order_map
        .values()
        .filter(|order| order.is_bid)
        .cloned()
        .collect();
    let mut asks: Vec<Order> = order_map
        .values()
        .filter(|order| !order.is_bid)
        .cloned()
        .collect();

    // Sort bids in descending order by price.
    bids.sort_by(|a, b| b.price.cmp(&a.price));
    // Sort asks in ascending order by price.
    asks.sort_by(|a, b| a.price.cmp(&b.price));

    (bids, asks)
}