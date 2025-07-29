import bisect
from collections import Counter

class LogSystem:
    def __init__(self):
        self.logs = []  # list of tuples: (timestamp, server_id, log_level, message)
        self.timestamps = []  # parallel list of timestamps for binary search
        self.server_logs = {}  # dict mapping server_id to list of logs

    def ingest(self, timestamp, server_id, log_level, message):
        log_entry = (timestamp, server_id, log_level, message)
        self.logs.append(log_entry)
        self.timestamps.append(timestamp)
        
        if server_id not in self.server_logs:
            self.server_logs[server_id] = []
        self.server_logs[server_id].append(log_entry)

    def query_time_range(self, start, end):
        # Use binary search on self.timestamps
        left = bisect.bisect_left(self.timestamps, start)
        right = bisect.bisect_right(self.timestamps, end)
        return self.logs[left:right]

    def query_server_log_level(self, server_id, min_log_level):
        if server_id not in self.server_logs:
            return []
        # Since logs are ingested in order and stored in list, they are already sorted by timestamp.
        return [log for log in self.server_logs[server_id] if log[2] >= min_log_level]

    def top_k_frequent_messages(self, start, end, k):
        # Retrieve logs within time range
        logs_in_range = self.query_time_range(start, end)
        # Count frequency of each message
        freq_counter = Counter()
        for log in logs_in_range:
            freq_counter[log[3]] += 1
        # Sort by frequency descending, then by message lexicographically ascending
        sorted_messages = sorted(freq_counter.items(), key=lambda x: (-x[1], x[0]))
        # Return top k as list of tuples (message, frequency)
        return sorted_messages[:k]