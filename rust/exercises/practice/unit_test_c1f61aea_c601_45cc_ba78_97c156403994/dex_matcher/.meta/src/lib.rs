use std::collections::HashSet;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum OrderType {
    Buy,
    Sell,
}

#[derive(Debug, Clone)]
pub struct Order {
    pub order_id: u64,
    pub timestamp: u64,
    pub order_type: OrderType,
    pub price: u64,
    pub quantity: u64,
}

#[derive(Debug, Clone)]
pub struct Cancellation {
    pub order_id: u64,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Trade {
    pub buy_order_id: u64,
    pub sell_order_id: u64,
    pub price: u64,
    pub quantity: u64,
}

pub fn process_orderbook(orders: Vec<Order>, cancellations: Vec<Cancellation>) -> Vec<Trade> {
    // Create a set of cancelled order ids.
    let cancelled_orders: HashSet<u64> = cancellations.into_iter().map(|c| c.order_id).collect();

    // Filter out cancelled orders and orders with zero quantity.
    let valid_orders: Vec<Order> = orders
        .into_iter()
        .filter(|order| !cancelled_orders.contains(&order.order_id) && order.quantity > 0)
        .collect();

    // Partition orders into buy and sell orders.
    let mut buy_orders: Vec<Order> = valid_orders
        .iter()
        .filter(|order| order.order_type == OrderType::Buy)
        .cloned()
        .collect();
    let mut sell_orders: Vec<Order> = valid_orders
        .iter()
        .filter(|order| order.order_type == OrderType::Sell)
        .cloned()
        .collect();

    // Sort buy orders: higher price first, if equal price then earlier timestamp first.
    buy_orders.sort_by(|a, b| b.price.cmp(&a.price).then(a.timestamp.cmp(&b.timestamp)));
    // Sort sell orders: lower price first, if equal price then earlier timestamp first.
    sell_orders.sort_by(|a, b| a.price.cmp(&b.price).then(a.timestamp.cmp(&b.timestamp)));

    let mut trades = Vec::new();
    let mut buy_index = 0;
    let mut sell_index = 0;

    // Process matching until either list of orders is exhausted.
    while buy_index < buy_orders.len() && sell_index < sell_orders.len() {
        let buy_order = &mut buy_orders[buy_index];
        let sell_order = &mut sell_orders[sell_index];

        // Check if the top buy order and sell order can be matched.
        if buy_order.price >= sell_order.price {
            // Determine the quantity to trade.
            let trade_qty = if buy_order.quantity < sell_order.quantity {
                buy_order.quantity
            } else {
                sell_order.quantity
            };

            // Record the trade with the sell order's price.
            trades.push(Trade {
                buy_order_id: buy_order.order_id,
                sell_order_id: sell_order.order_id,
                price: sell_order.price,
                quantity: trade_qty,
            });

            // Update orders quantities after the trade.
            buy_order.quantity -= trade_qty;
            sell_order.quantity -= trade_qty;

            // If the buy order is completely filled, move to the next buy order.
            if buy_order.quantity == 0 {
                buy_index += 1;
            }
            // If the sell order is completely filled, move to the next sell order.
            if sell_order.quantity == 0 {
                sell_index += 1;
            }
        } else {
            // No match is possible if the best buy order's price is less than the best sell order's price.
            break;
        }
    }

    trades
}