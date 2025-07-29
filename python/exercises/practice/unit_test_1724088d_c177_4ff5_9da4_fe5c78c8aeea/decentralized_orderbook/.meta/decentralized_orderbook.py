from typing import List, Tuple, Optional
from threading import Lock
import heapq
from collections import defaultdict
import time

class OrderBook:
    def __init__(self):
        # Order books for buy and sell orders
        # Using min heap for sell orders (lowest price first)
        # Using max heap for buy orders (highest price first, hence negative price)
        self._sell_orders = []
        self._buy_orders = []
        
        # Maps to track orders by ID for quick cancellation
        self._orders_map = {}
        
        # Locks for thread safety
        self._buy_lock = Lock()
        self._sell_lock = Lock()
        self._map_lock = Lock()

    def _validate_order(self, order: Tuple) -> None:
        """Validate order format and values"""
        order_id, trader_id, side, price, quantity = order
        
        if not isinstance(price, (int, float)) or price <= 0:
            raise ValueError("Price must be a positive number")
        
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer")
            
        if side not in ["buy", "sell"]:
            raise ValueError("Side must be either 'buy' or 'sell'")

    def submit_order(self, order: Tuple) -> List[Tuple]:
        """
        Submit a new order to the order book.
        Returns a list of executed trades.
        """
        self._validate_order(order)
        order_id, trader_id, side, price, quantity = order
        trades = []

        if side == "buy":
            trades = self._process_buy_order(order)
        else:
            trades = self._process_sell_order(order)

        return trades

    def _process_buy_order(self, order: Tuple) -> List[Tuple]:
        """Process a buy order and return resulting trades"""
        order_id, trader_id, side, price, quantity = order
        trades = []
        remaining_quantity = quantity

        with self._sell_lock:
            # Match against existing sell orders
            while (self._sell_orders and 
                  remaining_quantity > 0 and 
                  self._sell_orders[0][0] <= price):  # Compare with best sell price
                
                sell_price, timestamp, sell_order = self._sell_orders[0]
                sell_quantity = sell_order[4]
                trade_quantity = min(remaining_quantity, sell_quantity)
                
                # Execute trade
                trades.append((order_id, sell_order[0], sell_price, trade_quantity))
                
                remaining_quantity -= trade_quantity
                
                if trade_quantity == sell_quantity:
                    heapq.heappop(self._sell_orders)
                    with self._map_lock:
                        del self._orders_map[sell_order[0]]
                else:
                    # Update sell order with remaining quantity
                    updated_sell_order = (sell_order[0], sell_order[1], sell_order[2],
                                        sell_order[3], sell_quantity - trade_quantity)
                    heapq.heapreplace(self._sell_orders, 
                                    (sell_price, timestamp, updated_sell_order))
                    with self._map_lock:
                        self._orders_map[sell_order[0]] = updated_sell_order

        # If order is not fully filled, add to buy book
        if remaining_quantity > 0:
            updated_order = (order_id, trader_id, side, price, remaining_quantity)
            with self._buy_lock:
                heapq.heappush(self._buy_orders, 
                              (-price, time.time(), updated_order))  # Negative price for max heap
            with self._map_lock:
                self._orders_map[order_id] = updated_order

        return trades

    def _process_sell_order(self, order: Tuple) -> List[Tuple]:
        """Process a sell order and return resulting trades"""
        order_id, trader_id, side, price, quantity = order
        trades = []
        remaining_quantity = quantity

        with self._buy_lock:
            # Match against existing buy orders
            while (self._buy_orders and 
                  remaining_quantity > 0 and 
                  -self._buy_orders[0][0] >= price):  # Compare with best buy price
                
                buy_price, timestamp, buy_order = self._buy_orders[0]
                buy_quantity = buy_order[4]
                trade_quantity = min(remaining_quantity, buy_quantity)
                
                # Execute trade
                trades.append((buy_order[0], order_id, -buy_price, trade_quantity))
                
                remaining_quantity -= trade_quantity
                
                if trade_quantity == buy_quantity:
                    heapq.heappop(self._buy_orders)
                    with self._map_lock:
                        del self._orders_map[buy_order[0]]
                else:
                    # Update buy order with remaining quantity
                    updated_buy_order = (buy_order[0], buy_order[1], buy_order[2],
                                       buy_order[3], buy_quantity - trade_quantity)
                    heapq.heapreplace(self._buy_orders, 
                                    (buy_price, timestamp, updated_buy_order))
                    with self._map_lock:
                        self._orders_map[buy_order[0]] = updated_buy_order

        # If order is not fully filled, add to sell book
        if remaining_quantity > 0:
            updated_order = (order_id, trader_id, side, price, remaining_quantity)
            with self._sell_lock:
                heapq.heappush(self._sell_orders, 
                              (price, time.time(), updated_order))
            with self._map_lock:
                self._orders_map[order_id] = updated_order

        return trades

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order"""
        with self._map_lock:
            if order_id not in self._orders_map:
                return False
            
            order = self._orders_map[order_id]
            del self._orders_map[order_id]

        if order[2] == "buy":
            with self._buy_lock:
                self._buy_orders = [o for o in self._buy_orders if o[2][0] != order_id]
                heapq.heapify(self._buy_orders)
        else:
            with self._sell_lock:
                self._sell_orders = [o for o in self._sell_orders if o[2][0] != order_id]
                heapq.heapify(self._sell_orders)

        return True

    def get_buy_orders(self) -> List[Tuple]:
        """Get all buy orders sorted by price-time priority"""
        with self._buy_lock:
            return [order[2] for order in sorted(self._buy_orders)]

    def get_sell_orders(self) -> List[Tuple]:
        """Get all sell orders sorted by price-time priority"""
        with self._sell_lock:
            return [order[2] for order in sorted(self._sell_orders)]

    def get_order_book_snapshot(self) -> Tuple[List[Tuple], List[Tuple]]:
        """Get a snapshot of the current order book"""
        with self._buy_lock, self._sell_lock:
            buy_orders = self.get_buy_orders()
            sell_orders = self.get_sell_orders()
            return buy_orders, sell_orders