import datetime
from bisect import bisect_left
from copy import deepcopy
from collections import deque


def backtest_strategy(snapshots, strategy_func, bid_impact, ask_impact, latency, transaction_cost, 
                     inventory_limit, order_lifetime):
    """
    Backtests a trading strategy against historical order book data.
    
    Args:
        snapshots: List of order book snapshots, each containing timestamp, bids and asks
        strategy_func: Function that takes (orderbook, timestamp, inventory) and returns list of orders
        bid_impact: Market impact factor for bid (buying) orders
        ask_impact: Market impact factor for ask (selling) orders
        latency: Latency in milliseconds between placing an order and its execution
        transaction_cost: Transaction cost as a fraction of the trade value
        inventory_limit: Maximum inventory (long or short) allowed
        order_lifetime: Maximum lifetime of an order in milliseconds
    
    Returns:
        Dictionary containing:
        - profit_loss: Total profit/loss from the strategy
        - final_inventory: Final inventory position
        - trades: List of executed trades
        - max_inventory: Maximum inventory reached during backtest
    """
    
    if not snapshots:
        return {
            'profit_loss': 0,
            'final_inventory': 0,
            'trades': [],
            'max_inventory': 0
        }
    
    # Initialize
    current_inventory = 0
    max_inventory = 0
    profit_loss = 0
    trades = []
    active_orders = []  # List of orders waiting to be executed
    
    # Create a timeline of snapshots indexed by timestamp for quick lookup
    timeline = {snapshot['timestamp']: snapshot for snapshot in snapshots}
    timestamps = sorted(timeline.keys())
    
    # Process each snapshot
    for i, timestamp in enumerate(timestamps):
        snapshot = timeline[timestamp]
        
        # Process active orders first
        new_active_orders = []
        for order in active_orders:
            # Check if order should be executed at this timestamp
            execution_time = order['placement_time'] + datetime.timedelta(milliseconds=latency)
            expiration_time = order['placement_time'] + datetime.timedelta(milliseconds=order_lifetime)
            
            # If order has expired before this timestamp, skip it
            if timestamp > expiration_time:
                continue
                
            # If not yet time to execute, keep in active orders
            if timestamp < execution_time:
                new_active_orders.append(order)
                continue
            
            # Execute the order
            executed_trade = execute_order(order, snapshot, bid_impact, ask_impact, transaction_cost)
            
            if executed_trade:
                # Update inventory
                if executed_trade['side'] == 'buy':
                    new_inventory = current_inventory + executed_trade['quantity']
                    # Check inventory limit
                    if new_inventory <= inventory_limit:
                        current_inventory = new_inventory
                        profit_loss -= executed_trade['price'] * executed_trade['quantity']
                        trades.append(executed_trade)
                    else:
                        # Adjust quantity to respect inventory limit
                        allowed_quantity = inventory_limit - current_inventory
                        if allowed_quantity > 0:
                            executed_trade['quantity'] = allowed_quantity
                            current_inventory = inventory_limit
                            profit_loss -= executed_trade['price'] * executed_trade['quantity']
                            trades.append(executed_trade)
                else:  # sell
                    new_inventory = current_inventory - executed_trade['quantity']
                    # Check inventory limit (for short selling)
                    if new_inventory >= -inventory_limit:
                        current_inventory = new_inventory
                        profit_loss += executed_trade['price'] * executed_trade['quantity']
                        trades.append(executed_trade)
                    else:
                        # Adjust quantity to respect inventory limit
                        allowed_quantity = current_inventory + inventory_limit
                        if allowed_quantity > 0:
                            executed_trade['quantity'] = allowed_quantity
                            current_inventory = -inventory_limit
                            profit_loss += executed_trade['price'] * executed_trade['quantity']
                            trades.append(executed_trade)
            
            # Update max inventory (in absolute terms)
            max_inventory = max(max_inventory, abs(current_inventory))
        
        # Replace active orders with remaining ones
        active_orders = new_active_orders
        
        # Get new orders from strategy
        try:
            new_orders = strategy_func(deepcopy(snapshot), timestamp, current_inventory)
        except Exception as e:
            # If strategy fails, continue without new orders
            print(f"Strategy error at {timestamp}: {str(e)}")
            new_orders = []
        
        # Process new orders
        for order in new_orders:
            if not validate_order(order):
                continue
                
            # Check inventory limits before placing orders
            if order['side'] == 'buy':
                if current_inventory + order['quantity'] > inventory_limit:
                    # Adjust quantity to respect inventory limit
                    order['quantity'] = max(0, inventory_limit - current_inventory)
                    if order['quantity'] == 0:
                        continue
            else:  # sell
                if current_inventory - order['quantity'] < -inventory_limit:
                    # Adjust quantity to respect inventory limit
                    order['quantity'] = max(0, current_inventory + inventory_limit)
                    if order['quantity'] == 0:
                        continue
            
            # Add placement time
            order['placement_time'] = timestamp
            
            # Check if we can execute immediately (0 latency)
            if latency == 0:
                executed_trade = execute_order(order, snapshot, bid_impact, ask_impact, transaction_cost)
                if executed_trade:
                    # Update inventory and P&L
                    if executed_trade['side'] == 'buy':
                        current_inventory += executed_trade['quantity']
                        profit_loss -= executed_trade['price'] * executed_trade['quantity']
                    else:  # sell
                        current_inventory -= executed_trade['quantity']
                        profit_loss += executed_trade['price'] * executed_trade['quantity']
                    
                    trades.append(executed_trade)
                    max_inventory = max(max_inventory, abs(current_inventory))
            else:
                # Add to active orders
                active_orders.append(order)
    
    return {
        'profit_loss': profit_loss,
        'final_inventory': current_inventory,
        'trades': trades,
        'max_inventory': max_inventory
    }


def validate_order(order):
    """Validate if an order has the required fields and values."""
    if not isinstance(order, dict):
        return False
    
    required_fields = ['side', 'price', 'quantity']
    if not all(field in order for field in required_fields):
        return False
    
    if order['side'] not in ['buy', 'sell']:
        return False
    
    if not isinstance(order['price'], (int, float)) or order['price'] <= 0:
        return False
    
    if not isinstance(order['quantity'], (int, float)) or order['quantity'] <= 0:
        return False
    
    return True


def execute_order(order, snapshot, bid_impact, ask_impact, transaction_cost):
    """
    Execute an order against the current order book snapshot.
    
    Args:
        order: Order to execute (side, price, quantity)
        snapshot: Current order book snapshot
        bid_impact: Market impact for buy orders
        ask_impact: Market impact for sell orders
        transaction_cost: Transaction cost as fraction of trade value
        
    Returns:
        Trade details if order executed, None otherwise
    """
    side = order['side']
    limit_price = order['price']
    quantity = order['quantity']
    
    if not snapshot['bids'] or not snapshot['asks']:
        return None  # Can't execute if order book is empty
    
    # Apply market impact based on side
    impact = bid_impact if side == 'buy' else ask_impact
    
    if side == 'buy':
        # Buy order - check against asks
        sorted_asks = sorted(snapshot['asks'], key=lambda x: x['price'])
        
        # Check if we can execute at all
        if not sorted_asks or sorted_asks[0]['price'] > limit_price:
            return None
        
        # Walk the book to fill the order
        filled_quantity = 0
        avg_price = 0
        remaining = quantity
        
        for level in sorted_asks:
            if level['price'] > limit_price:
                break
                
            # Apply market impact
            level_price = level['price'] * (1 + impact * filled_quantity)
            if level_price > limit_price:
                break
                
            level_quantity = min(remaining, level['quantity'])
            avg_price = (avg_price * filled_quantity + level_price * level_quantity) / (filled_quantity + level_quantity)
            filled_quantity += level_quantity
            remaining -= level_quantity
            
            if remaining == 0:
                break
        
        if filled_quantity > 0:
            # Apply transaction cost
            final_price = avg_price * (1 + transaction_cost)
            return {
                'timestamp': snapshot['timestamp'],
                'side': 'buy',
                'price': final_price,
                'quantity': filled_quantity
            }
    else:  # sell
        # Sell order - check against bids
        sorted_bids = sorted(snapshot['bids'], key=lambda x: x['price'], reverse=True)
        
        # Check if we can execute at all
        if not sorted_bids or sorted_bids[0]['price'] < limit_price:
            return None
        
        # Walk the book to fill the order
        filled_quantity = 0
        avg_price = 0
        remaining = quantity
        
        for level in sorted_bids:
            if level['price'] < limit_price:
                break
                
            # Apply market impact
            level_price = level['price'] * (1 - impact * filled_quantity)
            if level_price < limit_price:
                break
                
            level_quantity = min(remaining, level['quantity'])
            avg_price = (avg_price * filled_quantity + level_price * level_quantity) / (filled_quantity + level_quantity)
            filled_quantity += level_quantity
            remaining -= level_quantity
            
            if remaining == 0:
                break
        
        if filled_quantity > 0:
            # Apply transaction cost
            final_price = avg_price * (1 - transaction_cost)
            return {
                'timestamp': snapshot['timestamp'],
                'side': 'sell',
                'price': final_price,
                'quantity': filled_quantity
            }
    
    return None