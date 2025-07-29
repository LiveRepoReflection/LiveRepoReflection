from collections import defaultdict
from typing import List, Dict, Any
import heapq
from time import time

class SlidingWindowMetric:
    def __init__(self):
        self.values = []  # min-heap of (timestamp, value) pairs
        self.sum = 0
        self.count = 0

    def add_value(self, timestamp: int, value: float) -> None:
        heapq.heappush(self.values, (timestamp, value))
        self.sum += value
        self.count += 1

    def remove_old_values(self, current_time: int) -> None:
        while self.values and self.values[0][0] < current_time - 60000:  # 60 seconds in milliseconds
            old_timestamp, old_value = heapq.heappop(self.values)
            self.sum -= old_value
            self.count -= 1

    def get_average(self) -> float:
        return self.sum / self.count if self.count > 0 else 0.0

class CentralAnalysisSystem:
    def __init__(self, anomaly_threshold: float):
        self.anomaly_threshold = anomaly_threshold
        self.historical_averages = defaultdict(lambda: defaultdict(float))  # {service: {metric: avg}}
        self.sliding_windows = defaultdict(lambda: defaultdict(SlidingWindowMetric))  # {service: {metric: SlidingWindowMetric}}
        self.N = 100  # Historical average window size

    def _update_historical_average(self, service: str, metric: str, current_value: float) -> None:
        historical_avg = self.historical_averages[service][metric]
        self.historical_averages[service][metric] = (historical_avg * (self.N - 1) + current_value) / self.N

    def _is_valid_metric_value(self, value: Any) -> bool:
        try:
            float_value = float(value)
            return True
        except (ValueError, TypeError):
            return False

    def process_logs(self, logs: List[Dict]) -> List[Dict]:
        # Sort logs by timestamp to ensure correct processing order
        sorted_logs = sorted(logs, key=lambda x: x['timestamp'], reverse=True)
        current_time = int(time() * 1000)

        # Process each log entry
        for log in sorted_logs:
            service_name = log['service_name']
            timestamp = log['timestamp']
            metrics = log['metrics']

            # Process each metric in the log entry
            for metric_name, metric_value in metrics.items():
                if not self._is_valid_metric_value(metric_value):
                    continue

                metric_value = float(metric_value)
                sliding_window = self.sliding_windows[service_name][metric_name]
                sliding_window.add_value(timestamp, metric_value)

        # Detect anomalies and prepare report
        anomalies = []
        
        for service_name, service_metrics in self.sliding_windows.items():
            for metric_name, sliding_window in service_metrics.items():
                # Remove old values outside the 60-second window
                sliding_window.remove_old_values(current_time)
                
                if sliding_window.count == 0:
                    continue

                current_avg = sliding_window.get_average()
                historical_avg = self.historical_averages[service_name][metric_name]
                difference = abs(current_avg - historical_avg)

                # Check for anomaly
                if difference > self.anomaly_threshold:
                    anomalies.append({
                        "service_name": service_name,
                        "metric_name": metric_name,
                        "current_value": current_avg,
                        "historical_average": historical_avg,
                        "difference": difference,
                        "timestamp": sorted_logs[0]['timestamp'] if sorted_logs else current_time
                    })

                # Update historical average
                self._update_historical_average(service_name, metric_name, current_avg)

        # Sort anomalies by timestamp in descending order
        return sorted(anomalies, key=lambda x: x['timestamp'], reverse=True)
