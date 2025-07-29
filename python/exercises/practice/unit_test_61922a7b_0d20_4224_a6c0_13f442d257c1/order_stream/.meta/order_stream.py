class OrderStream:
    def __init__(self):
        # Store all events as a list of tuples: (timestamp, order_id, side, price, quantity, event_type)
        self.events = []

    def process_event(self, event):
        # Append each incoming event to the events list
        self.events.append(event)

    def get_order_book(self, side, depth):
        # Process all events in chronological order
        orders = {}
        # Sort events by timestamp
        sorted_events = sorted(self.events, key=lambda e: e[0])
        for event in sorted_events:
            timestamp, order_id, evt_side, price, quantity, event_type = event
            if event_type == "new":
                # If the order_id already exists, ignore duplicate new order events
                if order_id not in orders:
                    orders[order_id] = {"side": evt_side, "price": price, "quantity": quantity, "timestamp": timestamp}
            elif event_type == "cancel":
                # Cancel event: set quantity to 0 if order exists
                if order_id in orders:
                    orders[order_id]["quantity"] = 0
            elif event_type == "execute":
                # Execute event: ensure the execution quantity is positive
                if quantity <= 0:
                    continue
                if order_id in orders:
                    # Subtract executed quantity, ensuring it does not drop below 0
                    orders[order_id]["quantity"] = max(orders[order_id]["quantity"] - quantity, 0)

        # Aggregate orders by price for the specified side
        price_levels = {}
        for order in orders.values():
            if order["side"] == side:
                level_price = order["price"]
                qty = order["quantity"]
                price_levels[level_price] = price_levels.get(level_price, 0) + qty

        # Sort price levels: descending for "buy" side and ascending for "sell" side
        if side == "buy":
            sorted_levels = sorted(price_levels.items(), key=lambda x: x[0], reverse=True)
        else:
            sorted_levels = sorted(price_levels.items(), key=lambda x: x[0])

        # Return the top 'depth' levels
        return sorted_levels[:depth]