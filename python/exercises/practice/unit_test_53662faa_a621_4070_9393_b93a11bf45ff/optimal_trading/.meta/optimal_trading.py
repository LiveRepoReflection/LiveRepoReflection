import time
from typing import Dict, List, Tuple, Optional
import statistics

# Define constants for the algorithm
# These can be adjusted based on market conditions
N = 3  # Number of order book levels to consider
T = 0.01  # Transaction cost per share
I = 100  # Maximum inventory limit
O = 20  # Maximum order size
L = 100  # Latency in milliseconds
M = 0.001  # Market impact factor

class OrderBookAnalyzer:
    """Class to analyze order book data and generate trading signals"""
    
    def __init__(self, window_size=10):
        self.window_size = window_size
        self.price_history = []
        self.mid_price_history = []
        self.spread_history = []
        self.volume_imbalance_history = []
    
    def update(self, snapshot: Dict):
        """Update the order book analyzer with a new snapshot"""
        # Extract key metrics from the snapshot
        best_bid = snapshot['bids'][0][0] if snapshot['bids'] else 0
        best_ask = snapshot['asks'][0][0] if snapshot['asks'] else float('inf')
        spread = best_ask - best_bid
        
        # Calculate volume imbalance
        bid_volume = sum(size for _, size in snapshot['bids'])
        ask_volume = sum(size for _, size in snapshot['asks'])
        
        if bid_volume + ask_volume > 0:
            volume_imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)
        else:
            volume_imbalance = 0
        
        # Update histories
        self.price_history.append((best_bid, best_ask))
        self.mid_price_history.append(snapshot['mid_price'])
        self.spread_history.append(spread)
        self.volume_imbalance_history.append(volume_imbalance)
        
        # Keep only the most recent window_size values
        if len(self.price_history) > self.window_size:
            self.price_history.pop(0)
            self.mid_price_history.pop(0)
            self.spread_history.pop(0)
            self.volume_imbalance_history.pop(0)
    
    def calc_price_momentum(self) -> float:
        """Calculate price momentum as a signal for trading"""
        if len(self.mid_price_history) < 2:
            return 0
        
        # Simple momentum: difference between current and previous price
        return self.mid_price_history[-1] - self.mid_price_history[0]
    
    def calc_volume_imbalance_signal(self) -> float:
        """Calculate volume imbalance signal"""
        if not self.volume_imbalance_history:
            return 0
        
        # Use the most recent volume imbalance as signal
        return self.volume_imbalance_history[-1]
    
    def calc_spread_signal(self) -> float:
        """Calculate spread signal"""
        if not self.spread_history:
            return 0
        
        # Compare current spread to average spread
        avg_spread = statistics.mean(self.spread_history) if self.spread_history else 0
        if avg_spread == 0:
            return 0
        
        # Normalize: negative when spread is tight (good for trading)
        return (self.spread_history[-1] - avg_spread) / avg_spread
    
    def calc_volatility(self) -> float:
        """Calculate recent price volatility"""
        if len(self.mid_price_history) < 2:
            return 0
        
        # Standard deviation of mid prices
        if len(self.mid_price_history) > 1:
            return statistics.stdev(self.mid_price_history)
        return 0


class OrderBookSimulator:
    """Simulates order execution with market impact and latency"""
    
    def __init__(self):
        self.pending_orders = []  # (timestamp, action, quantity, execution_price)
    
    def place_order(self, timestamp: int, action: str, quantity: int, current_price: float) -> None:
        """Place an order with the simulator"""
        execution_price = current_price
        # Apply market impact to execution price
        if action == "BUY":
            execution_price += M * quantity
        elif action == "SELL":
            execution_price -= M * quantity
        
        # Schedule order execution after latency
        execution_time = timestamp + L
        self.pending_orders.append((execution_time, action, quantity, execution_price))
    
    def get_executed_orders(self, current_timestamp: int) -> List[Tuple[str, int, float]]:
        """Get orders that have been executed by the current timestamp"""
        executed = []
        still_pending = []
        
        for order in self.pending_orders:
            exec_time, action, quantity, price = order
            if exec_time <= current_timestamp:
                executed.append((action, quantity, price))
            else:
                still_pending.append(order)
        
        self.pending_orders = still_pending
        return executed


class InventoryManager:
    """Manages trading inventory within limits"""
    
    def __init__(self, max_inventory=I):
        self.inventory = 0
        self.max_inventory = max_inventory
        self.trade_history = []  # (timestamp, action, quantity, price)
    
    def can_buy(self, quantity: int) -> bool:
        """Check if buying specified quantity is within inventory limits"""
        return self.inventory + quantity <= self.max_inventory
    
    def can_sell(self, quantity: int) -> bool:
        """Check if selling specified quantity is within inventory limits"""
        return self.inventory - quantity >= -self.max_inventory
    
    def execute_trade(self, timestamp: int, action: str, quantity: int, price: float) -> None:
        """Execute a trade and update inventory"""
        if action == "BUY":
            self.inventory += quantity
        elif action == "SELL":
            self.inventory -= quantity
        
        self.trade_history.append((timestamp, action, quantity, price))
    
    def calculate_pnl(self) -> float:
        """Calculate profit and loss from trade history"""
        pnl = 0
        for timestamp, action, quantity, price in self.trade_history:
            if action == "BUY":
                pnl -= quantity * (price + T)  # Cost of buying including transaction cost
            elif action == "SELL":
                pnl += quantity * (price - T)  # Revenue from selling minus transaction cost
        return pnl


class TradingStrategy:
    """Implements the core trading strategy"""
    
    def __init__(self):
        self.analyzer = OrderBookAnalyzer(window_size=10)
        self.simulator = OrderBookSimulator()
        self.inventory_manager = InventoryManager(max_inventory=I)
        self.last_decision_time = 0
        self.cooldown_period = 500  # milliseconds between decisions
    
    def decide_action(self, snapshot: Dict, current_inventory: int, last_trade_timestamp: int) -> Tuple[Optional[str], int]:
        """Decide trading action based on order book analysis"""
        current_timestamp = snapshot['timestamp']
        
        # Update analyzer with new data
        self.analyzer.update(snapshot)
        
        # Process any executed orders
        executed_orders = self.simulator.get_executed_orders(current_timestamp)
        for action, quantity, price in executed_orders:
            self.inventory_manager.execute_trade(current_timestamp, action, quantity, price)
        
        # If we're in cooldown period, don't make new decisions
        if current_timestamp - self.last_decision_time < self.cooldown_period:
            return None, 0
        
        # Get trading signals
        momentum = self.analyzer.calc_price_momentum()
        volume_imbalance = self.analyzer.calc_volume_imbalance_signal()
        spread_signal = self.analyzer.calc_spread_signal()
        volatility = self.analyzer.calc_volatility()
        
        # Combined signal: positive -> buy, negative -> sell
        combined_signal = momentum + 2 * volume_imbalance - spread_signal
        
        # Adjust signal based on current inventory
        inventory_factor = -current_inventory / self.inventory_manager.max_inventory
        combined_signal += inventory_factor * 0.5  # Lean against existing position
        
        # Higher threshold during high volatility
        threshold = 0.002 * (1 + 5 * volatility)
        
        # Determine action and quantity
        if combined_signal > threshold and self.inventory_manager.can_buy(O):
            self.last_decision_time = current_timestamp
            return "BUY", min(O, self.inventory_manager.max_inventory - current_inventory)
        elif combined_signal < -threshold and self.inventory_manager.can_sell(O):
            self.last_decision_time = current_timestamp
            return "SELL", min(O, self.inventory_manager.max_inventory + current_inventory)
        
        return None, 0


# Initialize global strategy object
_strategy = TradingStrategy()

def trading_algorithm(order_book_snapshot: Dict, current_inventory: int, last_trade_timestamp: int) -> Tuple[Optional[str], int]:
    """
    Main trading algorithm function that processes order book snapshots and makes trading decisions.
    
    Args:
        order_book_snapshot: Dictionary containing order book data
        current_inventory: Current inventory position
        last_trade_timestamp: Timestamp of the last executed trade
        
    Returns:
        Tuple of (action, quantity) where action is "BUY", "SELL", or None
    """
    start_time = time.time()
    
    # Use the global strategy object
    global _strategy
    
    # Make trading decision
    action, quantity = _strategy.decide_action(order_book_snapshot, current_inventory, last_trade_timestamp)
    
    # Simulate order execution if a trade decision was made
    if action in ("BUY", "SELL") and quantity > 0:
        best_price = order_book_snapshot['bids'][0][0] if action == "SELL" else order_book_snapshot['asks'][0][0]
        _strategy.simulator.place_order(order_book_snapshot['timestamp'], action, quantity, best_price)
    
    # Check time limit
    execution_time = (time.time() - start_time) * 1000  # convert to milliseconds
    if execution_time > 10:  # 10ms time limit
        # If exceeded time limit, return no action
        return None, 0
    
    return action, quantity