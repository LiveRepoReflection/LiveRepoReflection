from enum import Enum
import bisect
from collections import defaultdict

class Side(Enum):
    BID = "BID"  # Buy orders
    ASK = "ASK"  # Sell orders

class Order:
    """
    Represents an order in the order book.
    """
    def __init__(self, order_id, user_id, side, price, quantity, timestamp):
        """Initialize an order with required attributes."""
        self.order_id = order_id
        self.user_id = user_id
        self.side = side
        self.price = price
        self.quantity = quantity
        self.timestamp = timestamp
        
        # Validation
        if quantity <= 0:
            raise ValueError("Order quantity must be greater than zero")
            
    def __repr__(self):
        """String representation for debugging."""
        return f"Order(id={self.order_id}, {self.side.value}, price={self.price}, qty={self.quantity})"
        
    def __lt__(self, other):
        """
        Define comparison for sorting orders based on:
        - For BIDs: Higher price first, then earlier timestamp
        - For ASKs: Lower price first, then earlier timestamp
        """
        if self.side == Side.BID:
            # For bids, higher price has priority
            if self.price != other.price:
                return self.price > other.price
            return self.timestamp < other.timestamp
        else:
            # For asks, lower price has priority
            if self.price != other.price:
                return self.price < other.price
            return self.timestamp < other.timestamp

class OrderBook:
    """
    A decentralized order book implementation optimized for gas efficiency.
    """
    def __init__(self, max_orders_per_side=1000):
        """Initialize the order book."""
        # Main data structures for the order book
        self.bids = []  # Buy orders, sorted by price (highest first) then time
        self.asks = []  # Sell orders, sorted by price (lowest first) then time
        self.orders_by_id = {}  # Fast lookup for cancellation by order_id
        
        # Additional data structures for efficient operations
        self.bid_price_points = defaultdict(list)  # Maps price -> list of order indices in bids
        self.ask_price_points = defaultdict(list)  # Maps price -> list of order indices in asks
        
        # Constraints
        self.max_orders_per_side = max_orders_per_side
    
    def add_limit_order(self, order):
        """
        Add a limit order to the order book. If it matches with existing orders,
        execute the trades immediately. Otherwise, add the order to the book.
        
        Args:
            order (Order): The limit order to add
            
        Returns:
            None
            
        Raises:
            Exception: If the order book is full
        """
        if order.quantity <= 0:
            raise ValueError("Order quantity must be greater than zero")
            
        # Check if we're adding a buy (BID) or sell (ASK) order
        if order.side == Side.BID:
            # This is a buy order, so check against the ask side for matches
            remaining_qty = self._match_with_asks(order)
            
            # If there's remaining quantity, add it to the bid side
            if remaining_qty > 0:
                if len(self.bids) >= self.max_orders_per_side:
                    raise Exception(f"Order book is full on the bid side (max: {self.max_orders_per_side})")
                
                order.quantity = remaining_qty
                self._insert_bid(order)
                
        else:  # order.side == Side.ASK
            # This is a sell order, so check against the bid side for matches
            remaining_qty = self._match_with_bids(order)
            
            # If there's remaining quantity, add it to the ask side
            if remaining_qty > 0:
                if len(self.asks) >= self.max_orders_per_side:
                    raise Exception(f"Order book is full on the ask side (max: {self.max_orders_per_side})")
                
                order.quantity = remaining_qty
                self._insert_ask(order)
                
    def _match_with_asks(self, bid_order):
        """
        Match a bid (buy) order with existing ask (sell) orders.
        
        Args:
            bid_order (Order): The bid order to match
            
        Returns:
            int: The remaining quantity of the bid order after matching
        """
        remaining_qty = bid_order.quantity
        
        # Keep matching while:
        # 1. We have quantity to fill
        # 2. There are ask orders available
        # 3. The best ask price is less than or equal to our bid price
        while remaining_qty > 0 and self.asks and self.asks[0].price <= bid_order.price:
            ask_order = self.asks[0]
            
            # Calculate the trade quantity
            trade_qty = min(remaining_qty, ask_order.quantity)
            
            # Update the remaining quantities
            remaining_qty -= trade_qty
            ask_order.quantity -= trade_qty
            
            # If the ask order is completely filled, remove it
            if ask_order.quantity == 0:
                self._remove_order_from_asks(0)
            
        return remaining_qty
    
    def _match_with_bids(self, ask_order):
        """
        Match an ask (sell) order with existing bid (buy) orders.
        
        Args:
            ask_order (Order): The ask order to match
            
        Returns:
            int: The remaining quantity of the ask order after matching
        """
        remaining_qty = ask_order.quantity
        
        # Keep matching while:
        # 1. We have quantity to fill
        # 2. There are bid orders available
        # 3. The best bid price is greater than or equal to our ask price
        while remaining_qty > 0 and self.bids and self.bids[0].price >= ask_order.price:
            bid_order = self.bids[0]
            
            # Calculate the trade quantity
            trade_qty = min(remaining_qty, bid_order.quantity)
            
            # Update the remaining quantities
            remaining_qty -= trade_qty
            bid_order.quantity -= trade_qty
            
            # If the bid order is completely filled, remove it
            if bid_order.quantity == 0:
                self._remove_order_from_bids(0)
            
        return remaining_qty
    
    def execute_market_order(self, side, quantity):
        """
        Execute a market order against the order book.
        
        Args:
            side (Side): The side of the market order (BID for buy, ASK for sell)
            quantity (int): The quantity to execute
            
        Returns:
            int: The remaining quantity if the market order could not be fully filled
        """
        if quantity <= 0:
            raise ValueError("Market order quantity must be greater than zero")
            
        remaining_qty = quantity
        
        if side == Side.BID:
            # Execute a market buy order against the ask side
            while remaining_qty > 0 and self.asks:
                ask_order = self.asks[0]
                
                # Calculate the trade quantity
                trade_qty = min(remaining_qty, ask_order.quantity)
                
                # Update the remaining quantities
                remaining_qty -= trade_qty
                ask_order.quantity -= trade_qty
                
                # If the ask order is completely filled, remove it
                if ask_order.quantity == 0:
                    self._remove_order_from_asks(0)
        else:  # side == Side.ASK
            # Execute a market sell order against the bid side
            while remaining_qty > 0 and self.bids:
                bid_order = self.bids[0]
                
                # Calculate the trade quantity
                trade_qty = min(remaining_qty, bid_order.quantity)
                
                # Update the remaining quantities
                remaining_qty -= trade_qty
                bid_order.quantity -= trade_qty
                
                # If the bid order is completely filled, remove it
                if bid_order.quantity == 0:
                    self._remove_order_from_bids(0)
                    
        return remaining_qty
    
    def cancel_order(self, order_id):
        """
        Cancel an order with the specified ID.
        
        Args:
            order_id (int): The ID of the order to cancel
            
        Raises:
            Exception: If the order ID is not found
        """
        if order_id not in self.orders_by_id:
            raise Exception(f"Order ID {order_id} not found")
        
        # Get the order details
        order_info = self.orders_by_id[order_id]
        side = order_info["side"]
        index = order_info["index"]
        
        # Remove the order from the appropriate side
        if side == Side.BID:
            self._remove_order_from_bids(index)
        else:  # side == Side.ASK
            self._remove_order_from_asks(index)
            
    def _insert_bid(self, order):
        """
        Insert a bid order into the bid side of the book, maintaining sort order.
        
        Args:
            order (Order): The bid order to insert
        """
        # Find the insertion point using binary search for efficiency
        index = bisect.bisect_left(self.bids, order)
        self.bids.insert(index, order)
        
        # Update the lookup dictionaries
        self.orders_by_id[order.order_id] = {
            "side": Side.BID,
            "index": index
        }
        
        # Update indices for all orders after the inserted order
        for i in range(index + 1, len(self.bids)):
            if self.bids[i].order_id in self.orders_by_id:
                self.orders_by_id[self.bids[i].order_id]["index"] = i
                
        # Add to price point mapping
        self.bid_price_points[order.price].append(index)
    
    def _insert_ask(self, order):
        """
        Insert an ask order into the ask side of the book, maintaining sort order.
        
        Args:
            order (Order): The ask order to insert
        """
        # Find the insertion point using binary search for efficiency
        index = bisect.bisect_left(self.asks, order)
        self.asks.insert(index, order)
        
        # Update the lookup dictionaries
        self.orders_by_id[order.order_id] = {
            "side": Side.ASK,
            "index": index
        }
        
        # Update indices for all orders after the inserted order
        for i in range(index + 1, len(self.asks)):
            if self.asks[i].order_id in self.orders_by_id:
                self.orders_by_id[self.asks[i].order_id]["index"] = i
                
        # Add to price point mapping
        self.ask_price_points[order.price].append(index)
    
    def _remove_order_from_bids(self, index):
        """
        Remove a bid order at the specified index from the bid side.
        
        Args:
            index (int): The index of the order to remove
        """
        order = self.bids[index]
        
        # Remove from orders_by_id
        if order.order_id in self.orders_by_id:
            del self.orders_by_id[order.order_id]
            
        # Remove from price points
        if order.price in self.bid_price_points:
            if index in self.bid_price_points[order.price]:
                self.bid_price_points[order.price].remove(index)
            if not self.bid_price_points[order.price]:
                del self.bid_price_points[order.price]
        
        # Remove from bids list
        self.bids.pop(index)
        
        # Update indices for all orders after the removed order
        for i in range(index, len(self.bids)):
            if self.bids[i].order_id in self.orders_by_id:
                self.orders_by_id[self.bids[i].order_id]["index"] = i
                
            # Update price point indices as well
            price = self.bids[i].price
            if price in self.bid_price_points:
                for j in range(len(self.bid_price_points[price])):
                    if self.bid_price_points[price][j] > index:
                        self.bid_price_points[price][j] -= 1
                        
    def _remove_order_from_asks(self, index):
        """
        Remove an ask order at the specified index from the ask side.
        
        Args:
            index (int): The index of the order to remove
        """
        order = self.asks[index]
        
        # Remove from orders_by_id
        if order.order_id in self.orders_by_id:
            del self.orders_by_id[order.order_id]
            
        # Remove from price points
        if order.price in self.ask_price_points:
            if index in self.ask_price_points[order.price]:
                self.ask_price_points[order.price].remove(index)
            if not self.ask_price_points[order.price]:
                del self.ask_price_points[order.price]
        
        # Remove from asks list
        self.asks.pop(index)
        
        # Update indices for all orders after the removed order
        for i in range(index, len(self.asks)):
            if self.asks[i].order_id in self.orders_by_id:
                self.orders_by_id[self.asks[i].order_id]["index"] = i
                
            # Update price point indices as well
            price = self.asks[i].price
            if price in self.ask_price_points:
                for j in range(len(self.ask_price_points[price])):
                    if self.ask_price_points[price][j] > index:
                        self.ask_price_points[price][j] -= 1