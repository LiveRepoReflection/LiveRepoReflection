import heapq
import threading
from collections import defaultdict

class MarketArbDetector:
    def __init__(self, data_retention_ms=1000):
        self.data_retention_ms = data_retention_ms
        self.bids = defaultdict(list)  # Max heap (using negative prices)
        self.asks = defaultdict(list)  # Min heap
        self.arbitrage_events = []
        self.lock = threading.Lock()
        self.last_arbitrage = defaultdict(int)
        
    def process_quote(self, timestamp, symbol, side, price, quantity):
        with self.lock:
            self._clean_old_quotes(timestamp)
            
            if side == 'bid':
                heapq.heappush(self.bids[symbol], (-price, timestamp, quantity))
            elif side == 'ask':
                heapq.heappush(self.asks[symbol], (price, timestamp, quantity))
            
            self._check_arbitrage(timestamp, symbol)
    
    def process_execution(self, timestamp, symbol, price, quantity):
        with self.lock:
            self._clean_old_quotes(timestamp)
            self._remove_executed_quotes(symbol, price, quantity)
            self._check_arbitrage(timestamp, symbol)
    
    def get_arbitrage_opportunities(self):
        with self.lock:
            return self.arbitrage_events.copy()
    
    def _clean_old_quotes(self, current_timestamp):
        cutoff = current_timestamp - self.data_retention_ms
        
        for symbol in list(self.bids.keys()):
            while self.bids[symbol] and self.bids[symbol][0][1] < cutoff:
                heapq.heappop(self.bids[symbol])
            if not self.bids[symbol]:
                del self.bids[symbol]
        
        for symbol in list(self.asks.keys()):
            while self.asks[symbol] and self.asks[symbol][0][1] < cutoff:
                heapq.heappop(self.asks[symbol])
            if not self.asks[symbol]:
                del self.asks[symbol]
    
    def _remove_executed_quotes(self, symbol, price, quantity):
        if symbol in self.asks and self.asks[symbol] and self.asks[symbol][0][0] == price:
            _, ts, qty = self.asks[symbol][0]
            if qty <= quantity:
                heapq.heappop(self.asks[symbol])
            else:
                self.asks[symbol][0] = (price, ts, qty - quantity)
        
        if symbol in self.bids and self.bids[symbol] and -self.bids[symbol][0][0] == price:
            _, ts, qty = self.bids[symbol][0]
            if qty <= quantity:
                heapq.heappop(self.bids[symbol])
            else:
                self.bids[symbol][0] = (-price, ts, qty - quantity)
    
    def _check_arbitrage(self, timestamp, symbol):
        if symbol in self.bids and symbol in self.asks and self.bids[symbol] and self.asks[symbol]:
            best_bid = -self.bids[symbol][0][0]
            best_ask = self.asks[symbol][0][0]
            
            if best_bid > best_ask and timestamp > self.last_arbitrage.get(symbol, 0):
                self.arbitrage_events.append((timestamp, symbol))
                self.last_arbitrage[symbol] = timestamp