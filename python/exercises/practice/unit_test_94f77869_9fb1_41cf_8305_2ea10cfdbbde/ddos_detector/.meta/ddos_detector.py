#!/usr/bin/env python3
import sys
import json
import time
from collections import defaultdict
import math

# Constants
WINDOW_SIZE = 60  # 60 seconds sliding window
THRESHOLD = 1000  # Anomaly score threshold
DECAY_FACTOR = 0.1  # Lambda for time decay

class CountMinSketch:
    """
    Count-Min Sketch implementation for approximate frequency counting
    with limited memory usage.
    """
    def __init__(self, width=10000, depth=5):
        self.width = width
        self.depth = depth
        self.sketch = [[0 for _ in range(width)] for _ in range(depth)]
        # Different prime numbers for each hash function
        self.primes = [104729, 104743, 104759, 104761, 104773][:depth]
        
    def _hash(self, key, i):
        """Hash function for string keys"""
        return hash(f"{key}:{i}") % self.primes[i] % self.width
        
    def add(self, key, count=1):
        """Increment the count for a key"""
        for i in range(self.depth):
            self.sketch[i][self._hash(key, i)] += count
            
    def get(self, key):
        """Get the estimated count for a key"""
        return min(self.sketch[i][self._hash(key, i)] for i in range(self.depth))
        
    def clear(self):
        """Reset the sketch"""
        self.sketch = [[0 for _ in range(self.width)] for _ in range(self.depth)]

class DDOSDetector:
    """
    Real-time network anomaly detection system to identify potential DDoS attacks
    """
    def __init__(self):
        # We'll track data per destination IP
        self.destination_data = {}
        # Currently identified DDoS targets
        self.ddos_targets = []
        
    def _get_dest_data(self, dest_ip):
        """Get or create data structure for a destination IP"""
        if dest_ip not in self.destination_data:
            self.destination_data[dest_ip] = {
                'source_ips': defaultdict(lambda: {'first_seen': 0, 'weight': 0}),
                'anomaly_score': 0,
                'sketch': CountMinSketch(width=10000, depth=5)
            }
        return self.destination_data[dest_ip]
            
    def process_packet(self, packet):
        """Process a single network packet"""
        try:
            # Extract relevant fields
            timestamp = packet['timestamp']
            source_ip = packet['source_ip']
            dest_ip = packet['destination_ip']
            
            # Get data for this destination
            dest_data = self._get_dest_data(dest_ip)
            
            # If this is a new source IP for this destination
            if source_ip not in dest_data['source_ips']:
                # Record first seen time
                dest_data['source_ips'][source_ip]['first_seen'] = timestamp
                # Add to sketch for approximate counting
                dest_data['sketch'].add(source_ip)
                
            # Update the weight based on time decay
            current_time = timestamp
            first_seen = dest_data['source_ips'][source_ip]['first_seen']
            weight = math.exp(-DECAY_FACTOR * (current_time - first_seen))
            dest_data['source_ips'][source_ip]['weight'] = weight
            
            # Clean up old packets that are outside the sliding window
            self._clean_old_packets(timestamp)
            
            # Recalculate anomaly score for this destination
            self._update_anomaly_score(dest_ip)
            
            # Check if this destination is a potential DDoS target
            self._check_ddos_target(dest_ip)
                
        except (KeyError, ValueError) as e:
            # Skip malformed packets
            pass
        
    def _clean_old_packets(self, current_time):
        """Remove source IPs that are outside the sliding window"""
        cutoff_time = current_time - WINDOW_SIZE
        
        # For each destination IP
        for dest_ip in list(self.destination_data.keys()):
            dest_data = self.destination_data[dest_ip]
            
            # Remove sources that are too old
            outdated_sources = [
                src for src, data in dest_data['source_ips'].items()
                if data['first_seen'] < cutoff_time
            ]
            
            for src in outdated_sources:
                del dest_data['source_ips'][src]
            
            # If no more sources for this destination, clean it up
            if not dest_data['source_ips']:
                del self.destination_data[dest_ip]
                if dest_ip in self.ddos_targets:
                    self.ddos_targets.remove(dest_ip)
    
    def _update_anomaly_score(self, dest_ip):
        """Update the anomaly score for a destination IP"""
        if dest_ip not in self.destination_data:
            return
            
        dest_data = self.destination_data[dest_ip]
        
        # For accurate counting with decay, we need to sum up the weights
        weighted_count = sum(data['weight'] for data in dest_data['source_ips'].values())
        
        # For large numbers of sources, use the sketch for approximation
        # This is more memory efficient but less accurate
        if len(dest_data['source_ips']) > 5000:
            cardinality_estimate = sum(1 for src in dest_data['source_ips'])
            # A more sophisticated approach might use HyperLogLog for better cardinality estimation
            dest_data['anomaly_score'] = cardinality_estimate
        else:
            # For smaller sets, use the weighted count
            dest_data['anomaly_score'] = weighted_count
    
    def _check_ddos_target(self, dest_ip):
        """Check if a destination IP is a potential DDoS target"""
        if dest_ip not in self.destination_data:
            return
            
        dest_data = self.destination_data[dest_ip]
        
        # If anomaly score exceeds threshold, mark as DDoS target
        if dest_data['anomaly_score'] > THRESHOLD:
            if dest_ip not in self.ddos_targets:
                self.ddos_targets.append(dest_ip)
        # If score drops below threshold, remove from targets
        elif dest_ip in self.ddos_targets:
            self.ddos_targets.remove(dest_ip)
    
    def get_ddos_targets(self):
        """Return the current list of potential DDoS targets"""
        return self.ddos_targets

def detect_ddos():
    """Main function to process packet stream and detect DDoS attacks"""
    detector = DDOSDetector()
    
    try:
        for line in sys.stdin:
            # Skip empty lines
            line = line.strip()
            if not line:
                continue
                
            try:
                # Parse the packet JSON
                packet = json.loads(line)
                # Process the packet
                detector.process_packet(packet)
            except json.JSONDecodeError:
                # Skip invalid JSON
                continue
    except KeyboardInterrupt:
        # Handle graceful termination
        pass
        
    # Output the final result
    print(json.dumps(detector.get_ddos_targets()))

if __name__ == "__main__":
    detect_ddos()