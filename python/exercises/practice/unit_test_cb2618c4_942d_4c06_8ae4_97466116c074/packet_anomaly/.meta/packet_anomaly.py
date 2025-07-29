import math

class AnomalyDetector:
    def __init__(self):
        # Initialize variables for Welford's online algorithm for packet_size.
        self.count = 0
        self.mean = 0.0
        self.M2 = 0.0

    def process(self, packet):
        packet_size = packet.get("packet_size", 0)

        # Compute anomaly score using current statistics.
        if self.count < 2:
            anomaly = 0.0
        else:
            # Compute variance and standard deviation.
            variance = self.M2 / (self.count)
            std = math.sqrt(variance)
            # Ensure a minimum standard deviation to avoid division by zero.
            std = std if std >= 1 else 1.0
            diff = abs(packet_size - self.mean)
            if diff <= std:
                anomaly = 0.0
            else:
                anomaly = (diff - std) / std
                if anomaly > 1.0:
                    anomaly = 1.0

        # Update running statistics using Welford's algorithm.
        self.count += 1
        delta = packet_size - self.mean
        self.mean += delta / self.count
        delta2 = packet_size - self.mean
        self.M2 += delta * delta2

        return float(anomaly)