from collections import defaultdict
import heapq
from typing import Dict, List, Optional

class OrderBook:
    def __init__(self):
        # Min heap for sell orders (asks) - lowest price first
        self.asks: List = []
        # Max heap for buy orders (bids) - highest price first
        self.bids: List = []
        # Track orders by ID for cancellation
        self.orders_by_id: Dict = {}
        # Track active status of orders
        self.active_orders: Dict = {}

    def add_order(self, order: Dict) -> None:
        order_id = order["order_id"]
        self.orders_by_id[order_id] = order
        self.active_orders[order_id] = True

        if order["order_type"] == "SELL":
            # For asks (sell orders), use actual price for min heap
            heapq.heappush(self.asks, (order["price"], order["timestamp"], order_id))
        else:
            # For bids (buy orders), use negative price for max heap
            heapq.heappush(self.bids, (-order["price"], order["timestamp"], order_id))

    def get_best_bid(self) -> Optional[Dict]:
        while self.bids:
            neg_price, timestamp, order_id = self.bids[0]
            if self.active_orders.get(order_id, False):
                order = self.orders_by_id[order_id]
                if order["quantity"] > 0:
                    return order
            heapq.heappop(self.bids)
        return None

    def get_best_ask(self) -> Optional[Dict]:
        while self.asks:
            price, timestamp, order_id = self.asks[0]
            if self.active_orders.get(order_id, False):
                order = self.orders_by_id[order_id]
                if order["quantity"] > 0:
                    return order
            heapq.heappop(self.asks)
        return None

    def remove_order(self, order_id: str) -> bool:
        if order_id in self.active_orders:
            self.active_orders[order_id] = False
            return True
        return False

    def get_order_book(self) -> Dict:
        bids = []
        asks = []

        # Process bids (buy orders)
        temp_bids = []
        while self.bids and len(bids) < 100:  # Limit to top 100 orders
            neg_price, timestamp, order_id = heapq.heappop(self.bids)
            if self.active_orders.get(order_id, False):
                order = self.orders_by_id[order_id]
                if order["quantity"] > 0:
                    bids.append(order)
            temp_bids.append((neg_price, timestamp, order_id))
        
        # Restore bids heap
        for bid in temp_bids:
            heapq.heappush(self.bids, bid)

        # Process asks (sell orders)
        temp_asks = []
        while self.asks and len(asks) < 100:  # Limit to top 100 orders
            price, timestamp, order_id = heapq.heappop(self.asks)
            if self.active_orders.get(order_id, False):
                order = self.orders_by_id[order_id]
                if order["quantity"] > 0:
                    asks.append(order)
            temp_asks.append((price, timestamp, order_id))
        
        # Restore asks heap
        for ask in temp_asks:
            heapq.heappush(self.asks, ask)

        return {
            "bids": sorted(bids, key=lambda x: (-x["price"], x["timestamp"])),
            "asks": sorted(asks, key=lambda x: (x["price"], x["timestamp"]))
        }

class DASE:
    def __init__(self):
        self.order_books: Dict[str, OrderBook] = defaultdict(OrderBook)
        self.trades: Dict[str, List] = defaultdict(list)
        self.last_trade_prices: Dict[str, int] = {}
        self.trade_id_counter: int = 0

    def _validate_order(self, order: Dict) -> bool:
        required_fields = {"order_id", "user_id", "stock_symbol", "order_type", 
                         "price", "quantity", "timestamp"}
        
        # Check all required fields are present
        if not all(field in order for field in required_fields):
            return False

        # Validate order type
        if order["order_type"] not in ["BUY", "SELL"]:
            return False

        # Validate numeric fields
        if not isinstance(order["price"], int) or order["price"] <= 0:
            return False
        if not isinstance(order["quantity"], int) or order["quantity"] <= 0:
            return False
        if not isinstance(order["timestamp"], int) or order["timestamp"] <= 0:
            return False

        return True

    def _try_match_order(self, order: Dict) -> None:
        order_book = self.order_books[order["stock_symbol"]]
        
        while order["quantity"] > 0:
            matching_order = None
            if order["order_type"] == "BUY":
                best_ask = order_book.get_best_ask()
                if best_ask and best_ask["price"] <= order["price"]:
                    matching_order = best_ask
            else:  # SELL order
                best_bid = order_book.get_best_bid()
                if best_bid and best_bid["price"] >= order["price"]:
                    matching_order = best_bid

            if not matching_order:
                break

            # Calculate trade quantity
            trade_quantity = min(order["quantity"], matching_order["quantity"])
            
            # Execute trade
            self.trade_id_counter += 1
            trade = {
                "trade_id": str(self.trade_id_counter),
                "buy_order_id": order["order_id"] if order["order_type"] == "BUY" else matching_order["order_id"],
                "sell_order_id": matching_order["order_id"] if order["order_type"] == "SELL" else order["order_id"],
                "price": matching_order["price"],
                "quantity": trade_quantity,
                "timestamp": order["timestamp"]
            }

            # Update quantities
            order["quantity"] -= trade_quantity
            matching_order["quantity"] -= trade_quantity

            # Record trade
            self.trades[order["stock_symbol"]].append(trade)
            self.last_trade_prices[order["stock_symbol"]] = matching_order["price"]

            # Remove fully filled matching order
            if matching_order["quantity"] == 0:
                order_book.remove_order(matching_order["order_id"])

    def submit_order(self, order: Dict) -> bool:
        if not self._validate_order(order):
            return False

        order = order.copy()  # Create a copy to avoid modifying the input
        
        # Try to match the order first
        self._try_match_order(order)

        # If order is not fully filled, add to order book
        if order["quantity"] > 0:
            self.order_books[order["stock_symbol"]].add_order(order)

        return True

    def cancel_order(self, order_id: str) -> bool:
        # Search through all order books
        for order_book in self.order_books.values():
            if order_book.remove_order(order_id):
                return True
        return False

    def get_order_book(self, stock_symbol: str) -> Dict:
        return self.order_books[stock_symbol].get_order_book()

    def get_trades(self, stock_symbol: str) -> List:
        return self.trades[stock_symbol]

    def get_last_traded_price(self, stock_symbol: str) -> Optional[int]:
        return self.last_trade_prices.get(stock_symbol)