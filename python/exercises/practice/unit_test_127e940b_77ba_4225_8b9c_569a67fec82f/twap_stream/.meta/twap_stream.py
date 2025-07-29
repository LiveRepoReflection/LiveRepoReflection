import threading
import collections

class TWAPStream:
    def __init__(self, window_ms):
        self.window_ms = window_ms
        self.assets = {}
        self.lock = threading.Lock()

    def update_trade(self, timestamp, asset_id, price, volume):
        with self.lock:
            if asset_id not in self.assets:
                self.assets[asset_id] = collections.deque()
            trades = self.assets[asset_id]
            trades.append((timestamp, price, volume))
            # Prune trades that are outside the current window
            earliest_allowed = timestamp - self.window_ms
            while trades and trades[0][0] < earliest_allowed:
                trades.popleft()

    def get_twap(self, asset_id):
        with self.lock:
            if asset_id not in self.assets or not self.assets[asset_id]:
                return 0.0
            trades = self.assets[asset_id]
            current_time = trades[-1][0]
            window_start = current_time - self.window_ms
            numerator = 0.0
            denominator = 0.0
            for t, price, volume in trades:
                weight = (t - window_start) / self.window_ms
                numerator += price * volume * weight
                denominator += volume * weight
            if denominator == 0:
                return 0.0
            return round(numerator / denominator, 4)