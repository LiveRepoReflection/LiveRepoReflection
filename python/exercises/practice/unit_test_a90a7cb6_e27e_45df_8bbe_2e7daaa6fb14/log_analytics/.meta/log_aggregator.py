import time
import threading
from collections import defaultdict, deque
from heapq import nlargest

class LogAggregator:
    def __init__(self, max_logs=1000000, anomaly_threshold=10):
        self.logs = deque(maxlen=max_logs)
        self.lock = threading.Lock()
        self.message_counts = defaultdict(lambda: defaultdict(int))
        self.error_counts = defaultdict(int)
        self.last_anomaly_check = time.time()
        self.anomaly_threshold = anomaly_threshold
        self.anomalies = []

    def ingest_log(self, log):
        if not all(key in log for key in ['timestamp', 'service_id', 'log_level', 'message']):
            raise ValueError("Invalid log format. Missing required fields.")
        
        if not isinstance(log['timestamp'], int) or log['timestamp'] <= 0:
            raise ValueError("Invalid timestamp value.")
        
        with self.lock:
            self.logs.append(log)
            service = log['service_id']
            message = log['message']
            level = log['log_level']
            
            # Update message counts
            self.message_counts[service][message] += 1
            
            # Track error rates for anomaly detection
            if level == "ERROR":
                self.error_counts[service] += 1

    def query_logs(self, service_id=None, log_level=None, start_time=None, end_time=None, keyword=None):
        results = []
        with self.lock:
            for log in self.logs:
                match = True
                
                if service_id and log['service_id'] != service_id:
                    match = False
                if log_level and log['log_level'] != log_level:
                    match = False
                if start_time and log['timestamp'] < start_time:
                    match = False
                if end_time and log['timestamp'] > end_time:
                    match = False
                if keyword and keyword.lower() not in log['message'].lower():
                    match = False
                    
                if match:
                    results.append(log)
        return results

    def detect_anomalies(self, time_window=300):
        current_time = time.time()
        anomalies = []
        
        with self.lock:
            # Check for error rate spikes
            for service, count in self.error_counts.items():
                recent_errors = len([log for log in self.logs 
                                   if log['service_id'] == service 
                                   and log['log_level'] == "ERROR"
                                   and log['timestamp'] >= current_time - time_window])
                
                if recent_errors > self.anomaly_threshold:
                    anomalies.append({
                        'service_id': service,
                        'type': 'error_spike',
                        'count': recent_errors,
                        'timestamp': current_time
                    })
            
            # Check for unusual message patterns
            for service in self.message_counts:
                messages = self.message_counts[service]
                if messages and max(messages.values()) > 100:  # Arbitrary threshold
                    anomalies.append({
                        'service_id': service,
                        'type': 'message_repetition',
                        'message': max(messages.items(), key=lambda x: x[1])[0],
                        'count': max(messages.values()),
                        'timestamp': current_time
                    })
            
            self.anomalies.extend(anomalies)
            self.last_anomaly_check = current_time
            return anomalies

    def get_top_messages(self, service_id=None, n=5):
        with self.lock:
            if service_id:
                messages = self.message_counts.get(service_id, {})
                top = nlargest(n, messages.items(), key=lambda x: x[1])
                return [{'message': msg, 'count': cnt} for msg, cnt in top]
            else:
                all_messages = defaultdict(int)
                for service in self.message_counts:
                    for msg, cnt in self.message_counts[service].items():
                        all_messages[msg] += cnt
                top = nlargest(n, all_messages.items(), key=lambda x: x[1])
                return [{'message': msg, 'count': cnt} for msg, cnt in top]

    def clear_logs(self):
        with self.lock:
            self.logs.clear()
            self.message_counts.clear()
            self.error_counts.clear()
            self.anomalies.clear()