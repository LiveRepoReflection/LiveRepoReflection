import heapq
import math

TOLERANCE = 1e-6

class Order:
    def __init__(self, timestamp, order_id, order_type, price, quantity):
        self.timestamp = timestamp
        self.order_id = order_id
        self.order_type = order_type  # "BID" or "ASK"
        self.price = price
        self.quantity = quantity
        self.active = True

class OrderMatchingEngine:
    def __init__(self):
        # For BID orders, use max-heap by storing negative prices.
        self.bid_heap = []  # Entries: (-price, timestamp, order_id, order)
        # For ASK orders, use min-heap.
        self.ask_heap = []  # Entries: (price, timestamp, order_id, order)
        # Dictionary to track orders by order_id.
        self.orders = {}

    def process_order(self, event):
        """
        Process an incoming order event.
        event: tuple (timestamp, order_id, order_type, price, quantity, is_cancellation)
        Returns a list of trade executions. Each execution is a tuple:
        (taker_order_id, maker_order_id, price, quantity)
        """
        timestamp, order_id, order_type, price, quantity, is_cancellation = event
        trades = []
        
        # Cancellation event
        if is_cancellation:
            if order_id in self.orders:
                order = self.orders[order_id]
                order.active = False
                order.quantity = 0
            return trades
        
        # Create new order.
        new_order = Order(timestamp, order_id, order_type, price, quantity)
        self.orders[order_id] = new_order

        if order_type == "BID":
            # Try to match incoming BID with existing ASK orders.
            while new_order.quantity > 0 and self.ask_heap:
                ask_entry = self.ask_heap[0]
                ask_price, ask_timestamp, ask_order_id, ask_order = ask_entry
                
                # Skip inactive or fully filled orders.
                if not ask_order.active or ask_order.quantity <= 0:
                    heapq.heappop(self.ask_heap)
                    continue

                # Check if the ask order price is acceptable: ask.price <= bid.price
                if ask_price <= new_order.price + TOLERANCE:
                    trade_qty = min(new_order.quantity, ask_order.quantity)
                    # Maker is the resting ask order; incoming order is taker.
                    trades.append((new_order.order_id, ask_order.order_id, ask_order.price, trade_qty))
                    new_order.quantity -= trade_qty
                    ask_order.quantity -= trade_qty
                    # If maker order is fully filled, mark inactive and pop from heap.
                    if math.isclose(ask_order.quantity, 0, abs_tol=TOLERANCE) or ask_order.quantity <= 0:
                        ask_order.active = False
                        heapq.heappop(self.ask_heap)
                else:
                    break
            
            # If new order is not fully filled, add it to the BID book.
            if new_order.quantity > 0:
                heapq.heappush(self.bid_heap, (-new_order.price, new_order.timestamp, new_order.order_id, new_order))
        
        elif order_type == "ASK":
            # Try to match incoming ASK with existing BID orders.
            while new_order.quantity > 0 and self.bid_heap:
                bid_entry = self.bid_heap[0]
                neg_bid_price, bid_timestamp, bid_order_id, bid_order = bid_entry
                bid_price = -neg_bid_price
                
                # Skip inactive or fully filled orders.
                if not bid_order.active or bid_order.quantity <= 0:
                    heapq.heappop(self.bid_heap)
                    continue

                # Check if the bid order price is acceptable: bid.price >= ask.price
                if bid_price + TOLERANCE >= new_order.price:
                    trade_qty = min(new_order.quantity, bid_order.quantity)
                    # Maker is the resting bid order; incoming order is taker.
                    trades.append((new_order.order_id, bid_order.order_id, bid_order.price, trade_qty))
                    new_order.quantity -= trade_qty
                    bid_order.quantity -= trade_qty
                    # If maker order is fully filled, mark inactive and pop from heap.
                    if math.isclose(bid_order.quantity, 0, abs_tol=TOLERANCE) or bid_order.quantity <= 0:
                        bid_order.active = False
                        heapq.heappop(self.bid_heap)
                else:
                    break
            
            # If new order is not fully filled, add it to the ASK book.
            if new_order.quantity > 0:
                heapq.heappush(self.ask_heap, (new_order.price, new_order.timestamp, new_order.order_id, new_order))
        
        return trades