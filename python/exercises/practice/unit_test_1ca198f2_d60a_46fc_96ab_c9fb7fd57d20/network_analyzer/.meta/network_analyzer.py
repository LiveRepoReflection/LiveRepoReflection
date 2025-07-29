import time
import threading
from collections import defaultdict, deque
from heapq import heappush, heappop

class Flow:
    def __init__(self, key):
        self.key = key
        self.packets = []
        self.bytes = 0
        self.last_activity = time.time()
        self.dst_ports = set()
        self.syn_count = 0

    def add_packet(self, packet):
        self.packets.append(packet)
        self.bytes += packet['packet_size']
        self.last_activity = packet['timestamp']
        self.dst_ports.add(packet['dst_port'])
        if packet['protocol'] == 'TCP' and packet['flags'].get('SYN', False):
            self.syn_count += 1

    def get_features(self, current_time, feature_window):
        recent_packets = [p for p in self.packets 
                         if p['timestamp'] >= current_time - feature_window]
        total_packets = len(recent_packets)
        total_bytes = sum(p['packet_size'] for p in recent_packets)
        
        return {
            'total_packets': total_packets,
            'total_bytes': total_bytes,
            'avg_packet_size': total_bytes / total_packets if total_packets > 0 else 0,
            'packet_rate': total_packets / feature_window,
            'byte_rate': total_bytes / feature_window,
            'unique_dst_ports': len(self.dst_ports),
            'syn_ratio': self.syn_count / total_packets if total_packets > 0 else 0
        }

class NetworkAnalyzer:
    def __init__(self, is_anomalous, K=10, T=60, inactivity_timeout=300, feature_window=60):
        self.is_anomalous = is_anomalous
        self.K = K
        self.T = T
        self.inactivity_timeout = inactivity_timeout
        self.feature_window = feature_window
        
        self.flows = {}
        self.anomalous_flows = deque()
        self.rate_limit_queue = deque()
        self.lock = threading.Lock()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_inactive_flows, daemon=True)
        self.cleanup_thread.start()

    def _get_flow_key(self, packet):
        return (packet['src_ip'], packet['dst_ip'], 
                packet['src_port'], packet['dst_port'], 
                packet['protocol'])

    def process_packet(self, packet):
        with self.lock:
            flow_key = self._get_flow_key(packet)
            
            # Create or update flow
            if flow_key not in self.flows:
                self.flows[flow_key] = Flow(flow_key)
            flow = self.flows[flow_key]
            flow.add_packet(packet)
            
            # Check for anomalies
            features = flow.get_features(packet['timestamp'], self.feature_window)
            if self.is_anomalous(features):
                self._handle_anomaly(flow_key, packet['timestamp'])

    def _handle_anomaly(self, flow_key, timestamp):
        # Check rate limiting
        while self.rate_limit_queue and self.rate_limit_queue[0] <= timestamp - self.T:
            self.rate_limit_queue.popleft()
            
        if len(self.rate_limit_queue) < self.K:
            self.rate_limit_queue.append(timestamp)
            self.anomalous_flows.append(flow_key)

    def _cleanup_inactive_flows(self):
        while True:
            time.sleep(self.inactivity_timeout / 2)
            current_time = time.time()
            with self.lock:
                to_remove = [k for k, f in self.flows.items() 
                            if f.last_activity < current_time - self.inactivity_timeout]
                for k in to_remove:
                    del self.flows[k]

    def get_anomalous_flows(self):
        with self.lock:
            return list(self.anomalous_flows)