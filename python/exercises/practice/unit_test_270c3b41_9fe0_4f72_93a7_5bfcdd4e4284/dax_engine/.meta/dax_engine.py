import json
from collections import defaultdict
from decimal import Decimal
import heapq

# Initialize order book
buy_orders = {}  # Order ID -> Order
sell_orders = {}  # Order ID -> Order

# Price levels for quick matching
# For buys, we use negative prices to make heapq behave as max-heap
buy_price_levels = defaultdict(list)  # Price -> [Order IDs]
sell_price_levels = defaultdict(list)  # Price -> [Order IDs]

# Heaps for quick access to best prices
# For buys, we use negative price to get highest price first
buy_prices = []  # Max heap (negative prices)
sell_prices = []  # Min heap

def clear_order_book():
    """Clear the order book for testing"""
    global buy_orders, sell_orders, buy_price_levels, sell_price_levels, buy_prices, sell_prices
    buy_orders = {}
    sell_orders = {}
    buy_price_levels = defaultdict(list)
    sell_price_levels = defaultdict(list)
    buy_prices = []
    sell_prices = []

def validate_order(order):
    """Validate an order"""
    # Check for required fields
    required_fields = ["order_id", "timestamp", "type", "side", "quantity"]
    for field in required_fields:
        if field not in order:
            return False
    
    # Validate order type
    if order["type"] not in ["LIMIT", "MARKET"]:
        return False
    
    # Validate order side
    if order["side"] not in ["BUY", "SELL"]:
        return False
    
    # Validate quantity is positive
    if order["quantity"] <= 0:
        return False
    
    # Validate price for limit orders
    if order["type"] == "LIMIT":
        if "price" not in order:
            return False
        if order["price"] <= 0:
            return False
    
    return True

def add_to_order_book(order):
    """Add an order to the order book"""
    if order["side"] == "BUY":
        buy_orders[order["order_id"]] = order
        price = order["price"]
        buy_price_levels[price].append(order["order_id"])
        # Use negative price for max heap
        if -price not in buy_prices:
            heapq.heappush(buy_prices, -price)
    else:  # SELL
        sell_orders[order["order_id"]] = order
        price = order["price"]
        sell_price_levels[price].append(order["order_id"])
        if price not in sell_prices:
            heapq.heappush(sell_prices, price)

def get_best_buy_price():
    """Get the highest buy price in the order book"""
    while buy_prices and not buy_price_levels[-buy_prices[0]]:
        heapq.heappop(buy_prices)  # Remove empty price levels
    
    return -buy_prices[0] if buy_prices else None

def get_best_sell_price():
    """Get the lowest sell price in the order book"""
    while sell_prices and not sell_price_levels[sell_prices[0]]:
        heapq.heappop(sell_prices)  # Remove empty price levels
    
    return sell_prices[0] if sell_prices else None

def match_limit_order(order):
    """Match a limit order against the order book"""
    trades = []
    remaining_quantity = order["quantity"]
    
    if order["side"] == "BUY":
        # Match against sell orders
        while remaining_quantity > 0 and sell_prices:
            best_price = get_best_sell_price()
            if best_price is None or best_price > order["price"]:
                break  # No matching sell orders
            
            # Process orders at this price level
            while remaining_quantity > 0 and sell_price_levels[best_price]:
                matching_order_id = sell_price_levels[best_price][0]
                matching_order = sell_orders[matching_order_id]
                
                traded_quantity = min(remaining_quantity, matching_order["quantity"])
                remaining_quantity -= traded_quantity
                matching_order["quantity"] -= traded_quantity
                
                # Create a trade
                trade = {
                    "buy_order_id": order["order_id"],
                    "sell_order_id": matching_order_id,
                    "quantity": traded_quantity,
                    "price": best_price,
                    "timestamp": order["timestamp"]
                }
                trades.append(trade)
                
                # Remove filled orders
                if matching_order["quantity"] == 0:
                    sell_price_levels[best_price].pop(0)
                    del sell_orders[matching_order_id]
    else:  # SELL
        # Match against buy orders
        while remaining_quantity > 0 and buy_prices:
            best_price = get_best_buy_price()
            if best_price is None or best_price < order["price"]:
                break  # No matching buy orders
            
            # Process orders at this price level
            while remaining_quantity > 0 and buy_price_levels[best_price]:
                matching_order_id = buy_price_levels[best_price][0]
                matching_order = buy_orders[matching_order_id]
                
                traded_quantity = min(remaining_quantity, matching_order["quantity"])
                remaining_quantity -= traded_quantity
                matching_order["quantity"] -= traded_quantity
                
                # Create a trade
                trade = {
                    "buy_order_id": matching_order_id,
                    "sell_order_id": order["order_id"],
                    "quantity": traded_quantity,
                    "price": best_price,
                    "timestamp": order["timestamp"]
                }
                trades.append(trade)
                
                # Remove filled orders
                if matching_order["quantity"] == 0:
                    buy_price_levels[best_price].pop(0)
                    del buy_orders[matching_order_id]
    
    # Add remaining order to the book
    if remaining_quantity > 0:
        order["quantity"] = remaining_quantity
        add_to_order_book(order)
    
    return trades

def match_market_order(order):
    """Match a market order against the order book"""
    trades = []
    remaining_quantity = order["quantity"]
    
    if order["side"] == "BUY":
        # Match against sell orders
        while remaining_quantity > 0 and sell_prices:
            best_price = get_best_sell_price()
            if best_price is None:
                break  # No sell orders
            
            # Process orders at this price level
            while remaining_quantity > 0 and sell_price_levels[best_price]:
                matching_order_id = sell_price_levels[best_price][0]
                matching_order = sell_orders[matching_order_id]
                
                traded_quantity = min(remaining_quantity, matching_order["quantity"])
                remaining_quantity -= traded_quantity
                matching_order["quantity"] -= traded_quantity
                
                # Create a trade
                trade = {
                    "buy_order_id": order["order_id"],
                    "sell_order_id": matching_order_id,
                    "quantity": traded_quantity,
                    "price": best_price,
                    "timestamp": order["timestamp"]
                }
                trades.append(trade)
                
                # Remove filled orders
                if matching_order["quantity"] == 0:
                    sell_price_levels[best_price].pop(0)
                    del sell_orders[matching_order_id]
    else:  # SELL
        # Match against buy orders
        while remaining_quantity > 0 and buy_prices:
            best_price = get_best_buy_price()
            if best_price is None:
                break  # No buy orders
            
            # Process orders at this price level
            while remaining_quantity > 0 and buy_price_levels[best_price]:
                matching_order_id = buy_price_levels[best_price][0]
                matching_order = buy_orders[matching_order_id]
                
                traded_quantity = min(remaining_quantity, matching_order["quantity"])
                remaining_quantity -= traded_quantity
                matching_order["quantity"] -= traded_quantity
                
                # Create a trade
                trade = {
                    "buy_order_id": matching_order_id,
                    "sell_order_id": order["order_id"],
                    "quantity": traded_quantity,
                    "price": best_price,
                    "timestamp": order["timestamp"]
                }
                trades.append(trade)
                
                # Remove filled orders
                if matching_order["quantity"] == 0:
                    buy_price_levels[best_price].pop(0)
                    del buy_orders[matching_order_id]
    
    # Market orders that can't be fully filled are discarded (not added to book)
    return trades

def process_order(order):
    """Process an order and return resulting trades"""
    # Validate the order
    if not validate_order(order):
        return []
    
    # Convert quantity to float if it's not already
    if isinstance(order["quantity"], (str, int)):
        order["quantity"] = float(order["quantity"])
    
    # For limit orders, convert price to float if it's not already
    if order["type"] == "LIMIT" and isinstance(order["price"], (str, int)):
        order["price"] = float(order["price"])
    
    # Match the order
    if order["type"] == "LIMIT":
        return match_limit_order(order)
    else:  # MARKET
        return match_market_order(order)

def cancel_order(order_id):
    """Cancel an order by removing it from the order book"""
    if order_id in buy_orders:
        order = buy_orders[order_id]
        price = order["price"]
        
        # Remove from price level
        if order_id in buy_price_levels[price]:
            buy_price_levels[price].remove(order_id)
        
        # Remove from orders dictionary
        del buy_orders[order_id]
        
        return True
    elif order_id in sell_orders:
        order = sell_orders[order_id]
        price = order["price"]
        
        # Remove from price level
        if order_id in sell_price_levels[price]:
            sell_price_levels[price].remove(order_id)
        
        # Remove from orders dictionary
        del sell_orders[order_id]
        
        return True
    
    return False  # Order not found