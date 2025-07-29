class AnomalyDetector:
    def __init__(self, window_size, threshold):
        self.window_size = window_size
        self.threshold = threshold
        self.sensor_data = {}

    def process_reading(self, sensor_id, timestamp, value):
        if value is None:
            return None

        if sensor_id not in self.sensor_data:
            self.sensor_data[sensor_id] = []

        readings = self.sensor_data[sensor_id]
        if len(readings) < self.window_size:
            readings.append(value)
            return None

        avg = sum(readings) / len(readings)
        anomaly_score = abs(value - avg)

        # Update the historical window for the sensor
        readings.pop(0)
        readings.append(value)

        if anomaly_score >= self.threshold:
            return (sensor_id, timestamp, value, anomaly_score)
        else:
            return None