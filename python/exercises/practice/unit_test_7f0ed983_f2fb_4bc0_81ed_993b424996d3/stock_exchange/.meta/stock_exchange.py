import heapq
import threading

class Exchange:
    def __init__(self):
        # Dictionary mapping stock symbols to their order books.
        # Each order book is a dictionary with two keys "BUY" and "SELL", holding heaps.
        self.order_books = {}
        self.lock = threading.Lock()
    
    def process_order(self, order):
        """
        Process an incoming order.
        Order format: (order_id, timestamp, stock_symbol, order_type, quantity, price)
        Returns a list of executed trades in the form:
          (buy_order_id, sell_order_id, quantity, price)
        """
        with self.lock:
            order_id, timestamp, stock_symbol, order_type, quantity, price = order
            trades = []
            # Validate order quantity; if non-positive, ignore the order.
            if quantity <= 0:
                return trades
            
            # Initialize the order book for this stock_symbol if not exists.
            if stock_symbol not in self.order_books:
                self.order_books[stock_symbol] = {"BUY": [], "SELL": []}
            
            book = self.order_books[stock_symbol]
            
            # Create an order dictionary to handle mutable quantity.
            current_order = {
                "order_id": order_id,
                "timestamp": timestamp,
                "stock_symbol": stock_symbol,
                "order_type": order_type,
                "quantity": quantity,
                "price": price
            }
            
            if order_type == "BUY":
                # Attempt to match BUY order with existing SELL orders.
                while current_order["quantity"] > 0 and book["SELL"]:
                    # Peek the sell order with lowest price (and earliest timestamp).
                    sell_price, sell_timestamp, sell_order = book["SELL"][0]
                    # Only match if BUY price is >= SELL price.
                    if current_order["price"] >= sell_price:
                        heapq.heappop(book["SELL"])
                        execution_qty = min(current_order["quantity"], sell_order["quantity"])
                        # Record the trade with seller's price.
                        trades.append((current_order["order_id"], sell_order["order_id"], execution_qty, sell_order["price"]))
                        current_order["quantity"] -= execution_qty
                        sell_order["quantity"] -= execution_qty
                        # If sell order still has remaining quantity, push it back.
                        if sell_order["quantity"] > 0:
                            heapq.heappush(book["SELL"], (sell_order["price"], sell_order["timestamp"], sell_order))
                    else:
                        break
                # If BUY order not completely filled, add to BUY order book.
                if current_order["quantity"] > 0:
                    # For BUY orders, we use a max heap by using negative price.
                    heapq.heappush(book["BUY"], (-current_order["price"], current_order["timestamp"], current_order))
            
            elif order_type == "SELL":
                # Attempt to match SELL order with existing BUY orders.
                while current_order["quantity"] > 0 and book["BUY"]:
                    # Peek the BUY order with highest price (stored as negative price).
                    neg_buy_price, buy_timestamp, buy_order = book["BUY"][0]
                    buy_price = -neg_buy_price
                    # Only match if BUY price is >= SELL price.
                    if buy_price >= current_order["price"]:
                        heapq.heappop(book["BUY"])
                        execution_qty = min(current_order["quantity"], buy_order["quantity"])
                        # Trade is recorded at SELL order's price.
                        trades.append((buy_order["order_id"], current_order["order_id"], execution_qty, current_order["price"]))
                        current_order["quantity"] -= execution_qty
                        buy_order["quantity"] -= execution_qty
                        # If buy order still has remaining quantity, push it back.
                        if buy_order["quantity"] > 0:
                            heapq.heappush(book["BUY"], (-buy_order["price"], buy_order["timestamp"], buy_order))
                    else:
                        break
                # If SELL order not completely filled, add to SELL order book.
                if current_order["quantity"] > 0:
                    heapq.heappush(book["SELL"], (current_order["price"], current_order["timestamp"], current_order))
            
            # Return list of trades executed during the processing of this order.
            return trades