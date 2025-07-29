import threading
import math
from collections import deque

class AnomalyDetector:
    def __init__(self, window_size, z_threshold, log_file):
        self.window_size = window_size  # window size in seconds
        self.z_threshold = z_threshold
        self.log_file = log_file
        self.log_lock = threading.Lock()
        # Dictionary mapping stock_id to its data structure:
        # Each value is a dictionary with keys:
        # 'lock': threading.Lock() for thread safety,
        # 'ticks': deque of (timestamp, price) tuples,
        # 'sum': cumulative sum of prices,
        # 'sum_sq': cumulative sum of squared prices.
        self.stocks = {}
        self.window_size_ns = int(window_size * 1e9)
    
    def process_tick(self, tick):
        timestamp = tick['timestamp']
        stock_id = tick['stock_id']
        price = tick['price']
        volume = tick['volume']
        
        if stock_id not in self.stocks:
            self.stocks[stock_id] = {
                'lock': threading.Lock(),
                'ticks': deque(),
                'sum': 0.0,
                'sum_sq': 0.0
            }
        
        stock_data = self.stocks[stock_id]
        
        anomaly_str = None
        
        with stock_data['lock']:
            # Remove expired ticks from the sliding window.
            while stock_data['ticks'] and stock_data['ticks'][0][0] < timestamp - self.window_size_ns:
                old_timestamp, old_price = stock_data['ticks'].popleft()
                stock_data['sum'] -= old_price
                stock_data['sum_sq'] -= old_price * old_price
            
            count = len(stock_data['ticks'])
            if count > 0:
                mu = stock_data['sum'] / count
                variance = (stock_data['sum_sq'] - (stock_data['sum'] ** 2) / count) / count
                variance = max(variance, 0.0)
                sigma = math.sqrt(variance)
                if sigma > 0:
                    z_score = abs(price - mu) / sigma
                    if z_score > self.z_threshold:
                        anomaly_str = "Anomaly: timestamp={}, stock_id={}, price={}, volume={}, mu={}, sigma={}, z_score={}".format(
                            timestamp, stock_id, price, volume, mu, sigma, z_score
                        )
                        self._log_anomaly(anomaly_str)
            # Add the current tick to the sliding window.
            stock_data['ticks'].append((timestamp, price))
            stock_data['sum'] += price
            stock_data['sum_sq'] += price * price

        if anomaly_str is not None:
            print(anomaly_str)
        return anomaly_str

    def _log_anomaly(self, message):
        with self.log_lock:
            with open(self.log_file, "a") as f:
                f.write(message + "\n")