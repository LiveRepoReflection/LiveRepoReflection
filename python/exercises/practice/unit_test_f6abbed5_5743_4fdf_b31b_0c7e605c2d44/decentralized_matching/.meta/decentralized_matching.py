import time
import threading

class MatchingEngine:
    def __init__(self):
        self.buy_orders = []   # list of buy orders
        self.sell_orders = []  # list of sell orders
        self.trade_records = []
        self.trade_counter = 1
        self.lock = threading.Lock()

    def submit_order(self, order):
        with self.lock:
            # Make a copy of the order dictionary to avoid external mutations.
            order_copy = order.copy()
            # Add the order to the appropriate order book.
            if order_copy["order_type"] == "BUY":
                self.buy_orders.append(order_copy)
                self._sort_buy_orders()
            elif order_copy["order_type"] == "SELL":
                self.sell_orders.append(order_copy)
                self._sort_sell_orders()
            # Attempt to match orders after submission.
            self._match_orders()

    def _sort_buy_orders(self):
        # Buy orders: sort descending by price; if equal, ascending by timestamp.
        self.buy_orders.sort(key=lambda x: (-x["price"], x["timestamp"]))

    def _sort_sell_orders(self):
        # Sell orders: sort ascending by price; if equal, ascending by timestamp.
        self.sell_orders.sort(key=lambda x: (x["price"], x["timestamp"]))

    def _match_orders(self):
        # Continuously check for matching orders.
        while self.buy_orders and self.sell_orders:
            best_buy = self.buy_orders[0]
            best_sell = self.sell_orders[0]
            
            # Check if the best buy order can match the best sell order.
            if best_buy["price"] >= best_sell["price"]:
                # Determine trade quantity.
                trade_quantity = min(best_buy["quantity"], best_sell["quantity"])
                
                # Determine trade price based on rules.
                if best_buy["price"] > best_sell["price"]:
                    trade_price = best_sell["price"]
                else:
                    trade_price = best_buy["price"]
                
                # Create trade record.
                trade_record = {
                    "trade_id": f"trade_{self.trade_counter}",
                    "buy_order_id": best_buy["order_id"],
                    "sell_order_id": best_sell["order_id"],
                    "price": trade_price,
                    "quantity": trade_quantity,
                    "timestamp": int(time.time())
                }
                self.trade_records.append(trade_record)
                self.trade_counter += 1

                # Update quantities from orders.
                best_buy["quantity"] -= trade_quantity
                best_sell["quantity"] -= trade_quantity

                # Remove the order if it is completely filled.
                if abs(best_buy["quantity"]) < 1e-9:  # Using tolerance for floating point.
                    self.buy_orders.pop(0)
                if abs(best_sell["quantity"]) < 1e-9:
                    self.sell_orders.pop(0)

                # Re-sort the order books only if needed (because quantities changed).
                self._sort_buy_orders()
                self._sort_sell_orders()
            else:
                # No matching orders are present.
                break

    def get_trade_records(self):
        # Return a copy of trade records to ensure immutability.
        with self.lock:
            return [trade.copy() for trade in self.trade_records]

    def get_order_book(self, order_type):
        # Return a copy of the order_book list based on order type.
        with self.lock:
            if order_type == "BUY":
                return [order.copy() for order in self.buy_orders]
            elif order_type == "SELL":
                return [order.copy() for order in self.sell_orders]
            else:
                return []