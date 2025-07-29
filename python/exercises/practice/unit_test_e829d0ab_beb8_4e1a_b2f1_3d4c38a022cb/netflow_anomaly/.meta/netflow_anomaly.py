import numpy as np
from collections import defaultdict, deque
import time
from typing import Dict, Any

class FeatureExtractor:
    def __init__(self, window_size: int = 300):  # 5-minute window
        self.window_size = window_size
        self.ip_port_history = defaultdict(lambda: deque(maxlen=window_size))
        self.ip_packet_history = defaultdict(lambda: deque(maxlen=window_size))
        self.protocol_history = defaultdict(lambda: deque(maxlen=window_size))
        
    def extract_features(self, flow: Dict[str, Any]) -> np.ndarray:
        src_ip = flow['source_ip']
        dst_ip = flow['destination_ip']
        
        # Update histories
        self.ip_port_history[src_ip].append(flow['source_port'])
        self.ip_port_history[dst_ip].append(flow['destination_port'])
        self.ip_packet_history[src_ip].append((flow['packet_size'], flow['packet_count']))
        self.protocol_history[src_ip].append(flow['protocol'])
        
        # Feature 1: Port entropy for source IP
        src_ports = list(self.ip_port_history[src_ip])
        port_entropy = self._calculate_entropy(src_ports) if src_ports else 0
        
        # Feature 2: Average packet size and count for source IP
        packet_stats = list(self.ip_packet_history[src_ip])
        if packet_stats:
            avg_packet_size = np.mean([x[0] for x in packet_stats])
            avg_packet_count = np.mean([x[1] for x in packet_stats])
        else:
            avg_packet_size = flow['packet_size']
            avg_packet_count = flow['packet_count']
        
        # Feature 3: Protocol ratio for source IP
        protocol_ratio = self._calculate_protocol_ratio(src_ip)
        
        # Feature 4: Current flow metrics
        current_metrics = np.array([
            flow['packet_size'],
            flow['packet_count'],
            flow['source_port'],
            flow['destination_port']
        ])
        
        # Combine all features
        features = np.array([
            port_entropy,
            avg_packet_size,
            avg_packet_count,
            protocol_ratio,
            *current_metrics
        ])
        
        return features
    
    def _calculate_entropy(self, values) -> float:
        if not values:
            return 0.0
        
        # Calculate frequency distribution
        value_counts = defaultdict(int)
        for value in values:
            value_counts[value] += 1
        
        # Calculate entropy
        total = len(values)
        entropy = 0
        for count in value_counts.values():
            p = count / total
            entropy -= p * np.log2(p)
        
        return entropy
    
    def _calculate_protocol_ratio(self, ip: str) -> float:
        protocols = list(self.protocol_history[ip])
        if not protocols:
            return 0.0
        
        tcp_count = sum(1 for p in protocols if p == 'TCP')
        return tcp_count / len(protocols)

class AnomalyDetector:
    def __init__(self, window_size: int = 300):
        self.feature_extractor = FeatureExtractor(window_size)
        self.feature_history = deque(maxlen=window_size)
        self.mean = None
        self.std = None
        
    def process_flow(self, flow: Dict[str, Any]) -> float:
        # Validate input
        self._validate_flow(flow)
        
        # Extract features
        features = self.feature_extractor.extract_features(flow)
        
        # Update statistics
        self.feature_history.append(features)
        
        if len(self.feature_history) >= 10:  # Minimum samples needed
            # Update mean and standard deviation
            self.mean = np.mean(self.feature_history, axis=0)
            self.std = np.std(self.feature_history, axis=0) + 1e-10  # Add small constant to avoid division by zero
            
            # Calculate Mahalanobis distance
            diff = features - self.mean
            mahalanobis_dist = np.sqrt(np.sum((diff / self.std) ** 2))
            
            # Convert to anomaly score between 0 and 1
            score = 1 - np.exp(-mahalanobis_dist / 10)  # Scale factor of 10 can be adjusted
            return min(max(score, 0), 1)  # Ensure score is between 0 and 1
        
        return 0.0  # Return 0 while collecting initial data
    
    def _validate_flow(self, flow: Dict[str, Any]) -> None:
        required_fields = {
            'timestamp': int,
            'source_ip': str,
            'destination_ip': str,
            'source_port': int,
            'destination_port': int,
            'protocol': str,
            'packet_size': int,
            'packet_count': int
        }
        
        for field, field_type in required_fields.items():
            if field not in flow:
                raise KeyError(f"Missing required field: {field}")
            if not isinstance(flow[field], field_type):
                raise ValueError(f"Invalid type for field {field}: expected {field_type}, got {type(flow[field])}")