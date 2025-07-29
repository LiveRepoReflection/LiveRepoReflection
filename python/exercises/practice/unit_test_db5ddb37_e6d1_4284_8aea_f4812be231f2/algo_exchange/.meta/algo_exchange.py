import heapq

class AlgorithmicStockExchange:
    def __init__(self):
        # Dictionary mapping stock symbol to a book containing BUY and SELL heaps.
        # BUY heap stores tuples (-price, timestamp, order_id) for max-heap behavior.
        # SELL heap stores tuples (price, timestamp, order_id) for min-heap behavior.
        self.books = {}
        # Global dictionary mapping order_id to order record.
        self.orders = {}

    def _get_book(self, stock_symbol):
        if stock_symbol not in self.books:
            self.books[stock_symbol] = {"BUY": [], "SELL": []}
        return self.books[stock_symbol]

    def add_order(self, order_id, timestamp, stock_symbol, order_type, price, quantity):
        book = self._get_book(stock_symbol)
        order = {
            "order_id": order_id,
            "timestamp": timestamp,
            "stock": stock_symbol,
            "type": order_type,
            "price": price,
            "quantity": quantity,
            "active": True
        }
        self.orders[order_id] = order

        if order_type == "BUY":
            # Attempt to match with SELL orders in the order book.
            sell_heap = book["SELL"]
            while order["quantity"] > 0 and sell_heap:
                sell_price, sell_timestamp, sell_order_id = sell_heap[0]
                sell_order = self.orders.get(sell_order_id)
                # Lazy removal check for inactive or depleted orders.
                if sell_order is None or (not sell_order["active"]) or sell_order["quantity"] <= 0:
                    heapq.heappop(sell_heap)
                    continue
                if sell_order["price"] <= order["price"]:
                    trade_qty = min(order["quantity"], sell_order["quantity"])
                    order["quantity"] -= trade_qty
                    sell_order["quantity"] -= trade_qty
                    if sell_order["quantity"] == 0:
                        sell_order["active"] = False
                        heapq.heappop(sell_heap)
                else:
                    break
            # If there is remaining quantity, push the BUY order onto the BUY heap.
            if order["quantity"] > 0:
                heapq.heappush(book["BUY"], (-price, timestamp, order_id))
        elif order_type == "SELL":
            # Attempt to match with BUY orders in the order book.
            buy_heap = book["BUY"]
            while order["quantity"] > 0 and buy_heap:
                neg_buy_price, buy_timestamp, buy_order_id = buy_heap[0]
                buy_order = self.orders.get(buy_order_id)
                # Lazy removal check for inactive or depleted orders.
                if buy_order is None or (not buy_order["active"]) or buy_order["quantity"] <= 0:
                    heapq.heappop(buy_heap)
                    continue
                if buy_order["price"] >= order["price"]:
                    trade_qty = min(order["quantity"], buy_order["quantity"])
                    order["quantity"] -= trade_qty
                    buy_order["quantity"] -= trade_qty
                    if buy_order["quantity"] == 0:
                        buy_order["active"] = False
                        heapq.heappop(buy_heap)
                else:
                    break
            # If there is remaining quantity, push the SELL order onto the SELL heap.
            if order["quantity"] > 0:
                heapq.heappush(book["SELL"], (price, timestamp, order_id))

    def cancel_order(self, order_id, timestamp):
        order = self.orders.get(order_id)
        if order is None or not order["active"]:
            return
        # Cancellation timestamp must be strictly greater than the order's original timestamp.
        if timestamp <= order["timestamp"]:
            return
        order["active"] = False
        order["quantity"] = 0

    def get_top_of_book(self, stock_symbol):
        if stock_symbol not in self.books:
            return (None, None)
        book = self.books[stock_symbol]

        best_bid = None
        buy_heap = book["BUY"]
        while buy_heap:
            neg_price, ts, order_id = buy_heap[0]
            order = self.orders.get(order_id)
            if order is None or (not order["active"]) or order["quantity"] <= 0:
                heapq.heappop(buy_heap)
                continue
            best_bid = -neg_price
            break

        best_ask = None
        sell_heap = book["SELL"]
        while sell_heap:
            price, ts, order_id = sell_heap[0]
            order = self.orders.get(order_id)
            if order is None or (not order["active"]) or order["quantity"] <= 0:
                heapq.heappop(sell_heap)
                continue
            best_ask = price
            break

        return (best_bid, best_ask)