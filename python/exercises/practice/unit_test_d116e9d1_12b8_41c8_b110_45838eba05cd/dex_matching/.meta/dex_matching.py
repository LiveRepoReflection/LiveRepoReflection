import heapq
from collections import defaultdict, deque
from typing import List, Dict, Tuple, Optional, Set


class Order:
    """Represents a limit order in the order book."""
    
    def __init__(self, order_id: int, price: int, quantity: int, is_buy: bool, timestamp: int):
        self.order_id = order_id
        self.price = price
        self.quantity = quantity
        self.is_buy = is_buy
        self.timestamp = timestamp  # Used for price-time priority


class OrderBook:
    """A decentralized order book implementation optimized for gas efficiency."""
    
    def __init__(self):
        # Using min-heaps for buy orders (negative price for max-heap behavior)
        # and sell orders (positive price for min-heap behavior)
        self.buy_orders: List[Tuple[int, int, int]] = []  # (-price, timestamp, order_id)
        self.sell_orders: List[Tuple[int, int, int]] = []  # (price, timestamp, order_id)
        
        # Maps to store orders by ID for O(1) lookups and cancellations
        self.orders: Dict[int, Order] = {}
        self.order_to_heap_map: Dict[int, Tuple[int, int, int]] = {}
        
        # Track deleted orders without immediately removing from heap (lazy deletion)
        self.cancelled_orders: Set[int] = set()
        
        # Timestamp counter for maintaining price-time priority
        self.timestamp = 0
    
    def _get_timestamp(self) -> int:
        """Get a monotonically increasing timestamp."""
        self.timestamp += 1
        return self.timestamp
    
    def add_order(self, order_id: int, price: int, quantity: int, is_buy: bool) -> None:
        """Add a new limit order to the order book."""
        timestamp = self._get_timestamp()
        order = Order(order_id, price, quantity, is_buy, timestamp)
        self.orders[order_id] = order
        
        if is_buy:
            heap_entry = (-price, timestamp, order_id)  # Negate price for max-heap behavior
            self.order_to_heap_map[order_id] = heap_entry
            heapq.heappush(self.buy_orders, heap_entry)
        else:
            heap_entry = (price, timestamp, order_id)
            self.order_to_heap_map[order_id] = heap_entry
            heapq.heappush(self.sell_orders, heap_entry)
    
    def cancel_order(self, order_id: int) -> None:
        """Cancel an order by marking it as cancelled."""
        if order_id in self.orders and order_id not in self.cancelled_orders:
            self.cancelled_orders.add(order_id)
    
    def _clean_cancelled_orders(self, heap: List[Tuple[int, int, int]]) -> None:
        """Clean cancelled orders from the top of the heap."""
        while heap and heap[0][2] in self.cancelled_orders:
            order_id = heapq.heappop(heap)[2]
            self.cancelled_orders.remove(order_id)
            del self.orders[order_id]
            del self.order_to_heap_map[order_id]
    
    def get_best_buy_order(self) -> Optional[Order]:
        """Get the highest priority buy order."""
        self._clean_cancelled_orders(self.buy_orders)
        if not self.buy_orders:
            return None
        
        price, timestamp, order_id = self.buy_orders[0]
        return self.orders[order_id]
    
    def get_best_sell_order(self) -> Optional[Order]:
        """Get the highest priority sell order."""
        self._clean_cancelled_orders(self.sell_orders)
        if not self.sell_orders:
            return None
        
        price, timestamp, order_id = self.sell_orders[0]
        return self.orders[order_id]
    
    def remove_order(self, order_id: int) -> None:
        """Remove an order from the book completely."""
        if order_id in self.cancelled_orders:
            self.cancelled_orders.remove(order_id)
        
        if order_id in self.orders:
            del self.orders[order_id]
            del self.order_to_heap_map[order_id]
    
    def update_order_quantity(self, order_id: int, new_quantity: int) -> None:
        """Update the quantity of an existing order."""
        if order_id in self.orders:
            self.orders[order_id].quantity = new_quantity
    
    def _pop_best_buy_order(self) -> Optional[Order]:
        """Pop the highest priority buy order from the book."""
        self._clean_cancelled_orders(self.buy_orders)
        if not self.buy_orders:
            return None
        
        price, timestamp, order_id = heapq.heappop(self.buy_orders)
        order = self.orders[order_id]
        del self.orders[order_id]
        del self.order_to_heap_map[order_id]
        return order
    
    def _pop_best_sell_order(self) -> Optional[Order]:
        """Pop the highest priority sell order from the book."""
        self._clean_cancelled_orders(self.sell_orders)
        if not self.sell_orders:
            return None
        
        price, timestamp, order_id = heapq.heappop(self.sell_orders)
        order = self.orders[order_id]
        del self.orders[order_id]
        del self.order_to_heap_map[order_id]
        return order


class MatchingEngine:
    """Matching engine for processing orders."""
    
    def __init__(self):
        self.order_book = OrderBook()
    
    def place_limit_order(self, order_id: int, price: int, quantity: int, is_buy: bool) -> None:
        """Place a new limit order in the order book."""
        self.order_book.add_order(order_id, price, quantity, is_buy)
    
    def cancel_order(self, order_id: int) -> None:
        """Cancel an existing order."""
        self.order_book.cancel_order(order_id)
    
    def process_market_order(self, quantity: int, is_buy: bool) -> List[Tuple[int, int, int]]:
        """
        Process a market order, matching against the order book.
        
        Returns a list of trades executed, each represented as (order_id, price, quantity).
        """
        trades = []
        remaining_quantity = quantity
        
        while remaining_quantity > 0:
            matching_order = (
                self.order_book.get_best_sell_order() if is_buy 
                else self.order_book.get_best_buy_order()
            )
            
            if matching_order is None:
                break  # No more matching orders
            
            trade_quantity = min(remaining_quantity, matching_order.quantity)
            trade_price = matching_order.price
            
            # Record the trade
            trades.append((matching_order.order_id, trade_price, trade_quantity))
            
            # Update remaining quantities
            remaining_quantity -= trade_quantity
            matching_order.quantity -= trade_quantity
            
            if matching_order.quantity == 0:
                # Order fully filled, remove it
                if is_buy:
                    self.order_book._pop_best_sell_order()
                else:
                    self.order_book._pop_best_buy_order()
            else:
                # Order partially filled, update its quantity
                self.order_book.update_order_quantity(matching_order.order_id, matching_order.quantity)
        
        return trades


def process_operations(operations: List[str]) -> List[List[Tuple[int, int, int]]]:
    """
    Process a list of operations and return the trades executed for each market order.
    
    Args:
        operations: List of operation strings
    
    Returns:
        List of trade lists, one for each market order
    """
    engine = MatchingEngine()
    results = []
    
    for operation in operations:
        parts = operation.split()
        
        if parts[0] == "LIMIT":
            # LIMIT [BUY/SELL] <order_id> <price> <quantity>
            is_buy = parts[1] == "BUY"
            order_id = int(parts[2])
            price = int(parts[3])
            quantity = int(parts[4])
            engine.place_limit_order(order_id, price, quantity, is_buy)
        
        elif parts[0] == "MARKET":
            # MARKET [BUY/SELL] <quantity>
            is_buy = parts[1] == "BUY"
            quantity = int(parts[2])
            trades = engine.process_market_order(quantity, is_buy)
            results.append(trades)
        
        elif parts[0] == "CANCEL":
            # CANCEL <order_id>
            order_id = int(parts[1])
            engine.cancel_order(order_id)
    
    return results