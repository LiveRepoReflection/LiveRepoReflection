from collections import defaultdict
from typing import Dict, List, Optional
import heapq

class OrderBook:
    def __init__(self):
        # Price level -> List of orders at that price
        self.price_levels = defaultdict(list)
        # Order ID -> (price, index in price_level list)
        self.order_lookup = {}
        
    def add_order(self, order: dict) -> None:
        price = order["price"]
        self.price_levels[price].append(order)
        self.order_lookup[order["order_id"]] = (price, len(self.price_levels[price]) - 1)
        
    def remove_order(self, order_id: str) -> bool:
        if order_id not in self.order_lookup:
            return False
            
        price, idx = self.order_lookup[order_id]
        # Remove from lookup first
        del self.order_lookup[order_id]
        
        # Remove from price level
        orders = self.price_levels[price]
        # If this is not the last order in the list, swap with last order and update lookup
        if idx < len(orders) - 1:
            orders[idx] = orders[-1]
            self.order_lookup[orders[idx]["order_id"]] = (price, idx)
        orders.pop()
        
        # Remove empty price level
        if not orders:
            del self.price_levels[price]
            
        return True
        
    def get_best_price(self) -> Optional[int]:
        if not self.price_levels:
            return None
        return next(iter(sorted(self.price_levels.keys(), reverse=True)))
        
    def get_order(self, order_id: str) -> Optional[dict]:
        if order_id not in self.order_lookup:
            return None
        price, idx = self.order_lookup[order_id]
        return self.price_levels[price][idx]

class DEXMatcher:
    def __init__(self):
        self.buy_orders = OrderBook()
        self.sell_orders = OrderBook()
        
    def process_message(self, message: dict) -> Optional[List[dict]]:
        if message["type"] == "order":
            return self._process_order(message)
        elif message["type"] == "cancel":
            return self._process_cancel(message)
        return None
        
    def _process_order(self, order: dict) -> List[dict]:
        if order["quantity"] <= 0:
            return []
            
        trades = []
        remaining_quantity = order["quantity"]
        
        # If buy order, match against sell orders
        if order["side"] == "buy":
            while remaining_quantity > 0:
                best_price = self.sell_orders.get_best_price()
                if best_price is None or best_price > order["price"]:
                    break
                    
                for sell_order in self.sell_orders.price_levels[best_price][:]:
                    if remaining_quantity <= 0:
                        break
                        
                    trade_quantity = min(remaining_quantity, sell_order["quantity"])
                    trades.append({
                        "taker_order_id": order["order_id"],
                        "maker_order_id": sell_order["order_id"],
                        "price": sell_order["price"],
                        "quantity": trade_quantity,
                        "timestamp": order["timestamp"]
                    })
                    
                    remaining_quantity -= trade_quantity
                    sell_order["quantity"] -= trade_quantity
                    
                    if sell_order["quantity"] == 0:
                        self.sell_orders.remove_order(sell_order["order_id"])
                        
        # If sell order, match against buy orders
        else:
            while remaining_quantity > 0:
                best_price = self.buy_orders.get_best_price()
                if best_price is None or best_price < order["price"]:
                    break
                    
                for buy_order in self.buy_orders.price_levels[best_price][:]:
                    if remaining_quantity <= 0:
                        break
                        
                    trade_quantity = min(remaining_quantity, buy_order["quantity"])
                    trades.append({
                        "taker_order_id": order["order_id"],
                        "maker_order_id": buy_order["order_id"],
                        "price": buy_order["price"],
                        "quantity": trade_quantity,
                        "timestamp": order["timestamp"]
                    })
                    
                    remaining_quantity -= trade_quantity
                    buy_order["quantity"] -= trade_quantity
                    
                    if buy_order["quantity"] == 0:
                        self.buy_orders.remove_order(buy_order["order_id"])
                        
        # If order is not fully filled, add to order book
        if remaining_quantity > 0:
            new_order = order.copy()
            new_order["quantity"] = remaining_quantity
            if order["side"] == "buy":
                self.buy_orders.add_order(new_order)
            else:
                self.sell_orders.add_order(new_order)
                
        return trades
        
    def _process_cancel(self, cancel: dict) -> None:
        # Try to remove from both buy and sell order books
        if not self.buy_orders.remove_order(cancel["order_id"]):
            self.sell_orders.remove_order(cancel["order_id"])
            
    def get_order_book(self) -> Dict:
        return {
            "buy": dict(self.buy_orders.price_levels),
            "sell": dict(self.sell_orders.price_levels)
        }