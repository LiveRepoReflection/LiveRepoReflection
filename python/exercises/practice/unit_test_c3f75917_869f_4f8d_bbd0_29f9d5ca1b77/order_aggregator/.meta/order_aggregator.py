import threading
import time

class Order:
    def __init__(self, exchange_id, order_id, timestamp, side, price, quantity, action):
        self.exchange_id = exchange_id
        self.order_id = order_id
        self.timestamp = timestamp  # Unix epoch ms
        self.side = side  # "BID" or "ASK"
        self.price = price
        self.quantity = quantity
        self.action = action  # "NEW", "AMEND", or "CANCEL"

class OrderBookAggregator:
    def __init__(self, stale_threshold):
        # stale_threshold in milliseconds
        self.stale_threshold = stale_threshold
        self._lock = threading.Lock()
        # Active orders: key = (exchange_id, order_id), value = dict with details: side, price, quantity, timestamp.
        self.orders = {}
        # Aggregated order book: For each side, dictionary mapping price -> aggregated quantity
        self.book = {"BID": {}, "ASK": {}}

    def _is_stale(self, order_timestamp):
        current_time = int(time.time() * 1000)
        return order_timestamp < (current_time - self.stale_threshold)

    def process_order(self, order):
        # Ignore stale orders
        if self._is_stale(order.timestamp):
            return
        
        key = (order.exchange_id, order.order_id)
        with self._lock:
            if order.action == "NEW":
                # In case the order already exists, ignore new duplicate NEW order
                existing = self.orders.get(key)
                if existing is not None and order.timestamp < existing["timestamp"]:
                    return
                # Add new order
                self.orders[key] = {
                    "side": order.side,
                    "price": order.price,
                    "quantity": order.quantity,
                    "timestamp": order.timestamp
                }
                self._update_book(order.side, order.price, order.quantity)
            elif order.action == "AMEND":
                # Amend an existing order if exists and order timestamp is newer
                existing = self.orders.get(key)
                if existing is None or order.timestamp < existing["timestamp"]:
                    return
                # Calculate quantity difference
                delta = order.quantity - existing["quantity"]
                # Update stored order
                existing["quantity"] = order.quantity
                existing["timestamp"] = order.timestamp
                self._update_book(existing["side"], existing["price"], delta)
            elif order.action == "CANCEL":
                existing = self.orders.get(key)
                if existing is None or order.timestamp < existing["timestamp"]:
                    return
                # Subtract the entire quantity
                self._update_book(existing["side"], existing["price"], -existing["quantity"])
                del self.orders[key]

    def _update_book(self, side, price, quantity_delta):
        # Update aggregated levels
        levels = self.book.get(side, {})
        new_qty = levels.get(price, 0) + quantity_delta
        if new_qty <= 0:
            if price in levels:
                del levels[price]
        else:
            levels[price] = new_qty
        self.book[side] = levels

    def get_top_n_levels(self, side, n):
        with self._lock:
            levels = self.book.get(side, {})
            # For BID, highest prices first; for ASK, lowest prices first.
            if side == "BID":
                sorted_levels = sorted(levels.items(), key=lambda x: x[0], reverse=True)
            else:
                sorted_levels = sorted(levels.items(), key=lambda x: x[0])
            return sorted_levels[:n]