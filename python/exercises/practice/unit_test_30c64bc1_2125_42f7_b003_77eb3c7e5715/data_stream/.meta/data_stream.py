from collections import defaultdict, Counter
from typing import List, Tuple
import heapq

class DataStreamAnalyzer:
    def __init__(self):
        # Store packets by protocol and time
        self.protocol_time_data = defaultdict(lambda: defaultdict(list))
        # Store data sizes by source IP and time
        self.source_time_data = defaultdict(lambda: defaultdict(int))

    def process_packet(self, timestamp: int, source_ip: str, 
                      destination_ip: str, protocol: str, data_size: int) -> None:
        """Process a single packet from the data stream."""
        # Store packet info for TopK queries
        self.protocol_time_data[protocol][timestamp].append((destination_ip, data_size))
        
        # Store data size for Aggregate and DetectMalicious queries
        self.source_time_data[source_ip][timestamp] += data_size

    def top_k(self, protocol: str, start_time: int, end_time: int, k: int) -> List[Tuple[str, int]]:
        """Return k most frequent destination IPs for given protocol and time range."""
        ip_counter = Counter()
        
        # Count occurrences of destination IPs within time range
        for time in range(start_time, end_time + 1):
            if time in self.protocol_time_data[protocol]:
                for dest_ip, _ in self.protocol_time_data[protocol][time]:
                    ip_counter[dest_ip] += 1

        # Get top k destinations
        return sorted(
            [(ip, count) for ip, count in ip_counter.items()],
            key=lambda x: (-x[1], x[0])
        )[:k]

    def aggregate(self, source_ip: str, start_time: int, end_time: int) -> int:
        """Return total data size sent by source_ip within time range."""
        total_size = 0
        
        # Sum up data sizes within time range
        for time in range(start_time, end_time + 1):
            if time in self.source_time_data[source_ip]:
                total_size += self.source_time_data[source_ip][time]
                
        return total_size

    def detect_malicious(self, threshold: float, time_window: int) -> List[str]:
        """Detect IPs exceeding threshold in any time window."""
        malicious_ips = set()
        
        # For each source IP
        for source_ip in self.source_time_data:
            # Get all timestamps for this IP
            timestamps = sorted(self.source_time_data[source_ip].keys())
            if not timestamps:
                continue
                
            # Use sliding window to check traffic volume
            window_sum = 0
            window_start = 0
            
            for window_end in range(len(timestamps)):
                current_time = timestamps[window_end]
                window_sum += self.source_time_data[source_ip][current_time]
                
                # Remove timestamps outside the window
                while (window_start < window_end and 
                       timestamps[window_start] < current_time - time_window + 1):
                    window_sum -= self.source_time_data[source_ip][timestamps[window_start]]
                    window_start += 1
                
                # Check if average exceeds threshold
                window_size = min(time_window, 
                                timestamps[window_end] - timestamps[window_start] + 1)
                if window_sum / window_size > threshold:
                    malicious_ips.add(source_ip)
                    break
        
        return sorted(list(malicious_ips))