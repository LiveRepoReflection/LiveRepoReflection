import numpy as np
from collections import deque
import math

class StreamAnomalyDetector:
    def __init__(self, window_size=100, threshold=3.0, seasonality_window=24):
        self.window_size = window_size
        self.threshold = threshold
        self.seasonality_window = seasonality_window
        self.window = deque(maxlen=window_size)
        self.seasonal_window = deque(maxlen=seasonality_window)
        self.mean = 0
        self.std = 1
        self.seasonal_mean = 0
        self.seasonal_std = 1
        self.count = 0
        self.seasonal_count = 0

    def update_stats(self, value):
        if value is None:
            return False
            
        self.window.append(value)
        self.count += 1
        
        if len(self.window) >= 2:
            self.mean = np.mean(self.window)
            self.std = np.std(self.window)
            if self.std == 0:
                self.std = 1e-6
                
        if self.seasonality_window > 0:
            self.seasonal_window.append(value)
            self.seasonal_count += 1
            
            if len(self.seasonal_window) >= 2:
                self.seasonal_mean = np.mean(self.seasonal_window)
                self.seasonal_std = np.std(self.seasonal_window)
                if self.seasonal_std == 0:
                    self.seasonal_std = 1e-6

    def is_anomaly(self, value):
        if value is None:
            return False
            
        if self.count < 2:
            return False
            
        z_score = abs((value - self.mean) / self.std)
        
        if self.seasonality_window > 0 and self.seasonal_count >= 2:
            seasonal_z = abs((value - self.seasonal_mean) / self.seasonal_std)
            z_score = min(z_score, seasonal_z)
            
        return z_score > self.threshold

def detect_anomalies(data_stream, window_size=100, threshold=3.0, seasonality_window=24):
    detector = StreamAnomalyDetector(
        window_size=window_size,
        threshold=threshold,
        seasonality_window=seasonality_window
    )
    
    for value in data_stream:
        is_anomaly = detector.is_anomaly(value)
        detector.update_stats(value)
        yield is_anomaly