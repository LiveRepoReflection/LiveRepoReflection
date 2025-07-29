import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any


@dataclass
class WindowStats:
    """Class to keep track of statistics for a sliding window."""
    window_size: int
    values: List[float] = field(default_factory=list)
    sum: float = 0
    sum_squares: float = 0

    def add_value(self, value: float) -> None:
        """Add a new value to the sliding window statistics."""
        self.values.append(value)
        self.sum += value
        self.sum_squares += value * value

        # Remove oldest value if window size is exceeded
        if len(self.values) > self.window_size:
            old_value = self.values.pop(0)
            self.sum -= old_value
            self.sum_squares -= old_value * old_value

    def get_mean(self) -> float:
        """Calculate the mean of the current values in the window."""
        if not self.values:
            return 0
        return self.sum / len(self.values)

    def get_std_dev(self) -> float:
        """Calculate the standard deviation of the current values in the window."""
        if len(self.values) <= 1:
            return 0

        mean = self.get_mean()
        variance = (self.sum_squares / len(self.values)) - (mean * mean)
        # Handle floating point precision issues that can cause small negative variances
        if variance < 0:
            variance = 0
        return math.sqrt(variance)

    def get_z_score(self, value: float) -> float:
        """Calculate the Z-score for a new value."""
        std_dev = self.get_std_dev()
        if std_dev == 0:
            # If standard deviation is zero, use a small epsilon to avoid division by zero
            # This handles cases where all values are the same
            if value == self.get_mean():
                return 0
            # If the value is different from the mean when all values are the same,
            # it's definitely an anomaly
            epsilon = 0.001 * self.get_mean() if self.get_mean() != 0 else 0.001
            std_dev = epsilon
        return abs(value - self.get_mean()) / std_dev


class AnomalyDetector:
    """Class for detecting anomalies in network traffic."""
    def __init__(self, window_size: int = 100, threshold: float = 3.0):
        """Initialize the anomaly detector.
        
        Args:
            window_size: The size of the sliding window for computing statistics
            threshold: The threshold Z-score above which a value is considered anomalous
        """
        self.window_size = window_size
        self.threshold = threshold
        self.stats = defaultdict(lambda: WindowStats(window_size))
        self.min_data_points = 3  # Minimum data points required for anomaly detection

    def _get_connection_key(self, record: Dict[str, Any]) -> Tuple[str, str, str]:
        """Create a unique key for each connection based on source, destination, and protocol."""
        return (record["source_node"], record["destination_node"], record["protocol"])

    def process_record(self, record: Dict[str, Any]) -> Tuple[bool, float]:
        """Process a single traffic record and check if it's anomalous.
        
        Args:
            record: Dictionary containing traffic data
            
        Returns:
            Tuple of (is_anomalous, anomaly_score)
        """
        key = self._get_connection_key(record)
        packet_size = record["packet_size"]
        stats = self.stats[key]
        
        # Calculate anomaly score before adding the new value
        # This prevents the anomaly from affecting its own baseline
        z_score = stats.get_z_score(packet_size)
        
        # Add the value to update statistics
        stats.add_value(packet_size)
        
        # Check if we have enough data points and if it exceeds the threshold
        is_anomalous = (len(stats.values) >= self.min_data_points and z_score > self.threshold)
        
        return is_anomalous, z_score

    def detect_anomalies(self, traffic_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a list of traffic records and detect anomalies.
        
        Args:
            traffic_data: List of dictionaries containing traffic data
            
        Returns:
            List of records flagged as anomalous, with added anomaly_score field
        """
        anomalies = []
        
        for record in traffic_data:
            is_anomalous, anomaly_score = self.process_record(record)
            
            if is_anomalous:
                # Create a copy to avoid modifying the original record
                anomaly_record = dict(record)
                anomaly_record["anomaly_score"] = anomaly_score
                anomalies.append(anomaly_record)
                
        return anomalies


def detect_anomalies(traffic_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect anomalies in network traffic data.
    
    Args:
        traffic_data: List of dictionaries containing traffic data
        
    Returns:
        List of records flagged as anomalous, with added anomaly_score field
    """
    detector = AnomalyDetector(window_size=100, threshold=3.0)
    return detector.detect_anomalies(traffic_data)