import heapq
import math
import random
from typing import Dict, List, Optional, Any, Tuple, Union


class SensorNode:
    """
    Represents a sensor node in the distributed system.
    Each sensor node generates data and sends it to an assigned aggregation server.
    """
    def __init__(self, id: int, aggregation_server_id: int):
        """
        Initialize a sensor node.
        
        Args:
            id: The unique identifier for this sensor.
            aggregation_server_id: The ID of the aggregation server this sensor reports to.
        """
        self.id = id
        self.aggregation_server_id = aggregation_server_id
        self.current_value = None
        
    def generate_data(self) -> int:
        """
        Generate a random data point.
        
        Returns:
            A randomly generated integer value.
        """
        # For simulation purposes, generate a random value
        self.current_value = random.randint(1, 1000)
        return self.current_value
        
    def send_data_to_server(self, aggregation_server: 'AggregationServer', data: int) -> None:
        """
        Send the generated data to the assigned aggregation server.
        
        Args:
            aggregation_server: The server to send data to.
            data: The data value to send.
        """
        aggregation_server.receive_data(self.id, data)


class MedianCalculator:
    """
    Utility class for calculating exact and approximate medians.
    """
    @staticmethod
    def calculate_exact_median(data: List[int]) -> Union[int, float]:
        """
        Calculate the exact median of a list of values.
        
        Args:
            data: A list of numeric values.
            
        Returns:
            The median value.
        """
        if not data:
            return None
            
        sorted_data = sorted(data)
        n = len(sorted_data)
        
        if n % 2 == 0:
            # Even number of elements, return average of middle two
            return (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
        else:
            # Odd number of elements, return middle element
            return sorted_data[n // 2]
    
    @staticmethod
    def calculate_approximate_median(data: List[int]) -> float:
        """
        Calculate an approximate median using a sampling technique.
        This is useful when dealing with very large datasets.
        
        Args:
            data: A list of numeric values.
            
        Returns:
            An approximation of the median value.
        """
        if not data:
            return None
            
        if len(data) <= 1000:
            return MedianCalculator.calculate_exact_median(data)
            
        # For large datasets, use reservoir sampling to get a representative sample
        sample_size = min(1000, len(data))
        sample = random.sample(data, sample_size)
        return MedianCalculator.calculate_exact_median(sample)
        

class MedianSketch:
    """
    A sketch data structure for estimating the median with limited memory.
    Uses a quantile sketch approach based on histogram buckets.
    """
    def __init__(self, min_value: int = 0, max_value: int = 1000, num_buckets: int = 100):
        """
        Initialize the median sketch with specified parameters.
        
        Args:
            min_value: The minimum possible value in the data stream.
            max_value: The maximum possible value in the data stream.
            num_buckets: Number of buckets to use in the sketch.
        """
        self.min_value = min_value
        self.max_value = max_value
        self.num_buckets = num_buckets
        self.bucket_size = (max_value - min_value) / num_buckets
        self.buckets = [0] * num_buckets
        self.total_count = 0
        
    def insert(self, value: int) -> None:
        """
        Insert a value into the sketch.
        
        Args:
            value: The value to insert.
        """
        if value < self.min_value or value > self.max_value:
            # Value outside of our range - can either clamp it or ignore it
            # Here we clamp it to our range
            value = max(self.min_value, min(value, self.max_value))
        
        # Determine which bucket this value belongs in
        bucket_idx = min(
            self.num_buckets - 1, 
            int((value - self.min_value) / self.bucket_size)
        )
        self.buckets[bucket_idx] += 1
        self.total_count += 1
        
    def merge(self, other_sketch: 'MedianSketch') -> None:
        """
        Merge another sketch into this one.
        
        Args:
            other_sketch: Another MedianSketch object to merge.
        """
        if (self.min_value != other_sketch.min_value or 
            self.max_value != other_sketch.max_value or 
            self.num_buckets != other_sketch.num_buckets):
            raise ValueError("Cannot merge sketches with different parameters")
            
        for i in range(self.num_buckets):
            self.buckets[i] += other_sketch.buckets[i]
        self.total_count += other_sketch.total_count
        
    def estimate_median(self) -> float:
        """
        Estimate the median based on the current state of the sketch.
        
        Returns:
            The estimated median value.
        """
        if self.total_count == 0:
            return None
            
        # Find the bucket that contains the median
        target_count = self.total_count / 2
        cumulative_count = 0
        
        for i in range(self.num_buckets):
            cumulative_count += self.buckets[i]
            if cumulative_count >= target_count:
                # The median is in this bucket
                # For simplicity, return the middle value of this bucket
                bucket_start = self.min_value + i * self.bucket_size
                bucket_end = bucket_start + self.bucket_size
                return (bucket_start + bucket_end) / 2
                
        # This should not happen if buckets are properly updated
        return self.min_value + (self.max_value - self.min_value) / 2


class AggregationServer:
    """
    Represents an aggregation server that collects data from multiple sensor nodes.
    """
    def __init__(self, id: int):
        """
        Initialize an aggregation server.
        
        Args:
            id: The unique identifier for this server.
        """
        self.id = id
        self.sensor_data = {}  # Maps sensor_id to its most recent value
        # For more advanced aggregation, use a median sketch instead of keeping all values
        self.median_sketch = MedianSketch(0, 1000, 100)
        
    def receive_data(self, sensor_id: int, data: int) -> None:
        """
        Process data received from a sensor node.
        
        Args:
            sensor_id: The ID of the sensor sending the data.
            data: The data value received.
        """
        # Store the most recent value from this sensor
        self.sensor_data[sensor_id] = data
        # Update our sketch with this value
        self.median_sketch.insert(data)
        
    def get_aggregated_data(self) -> Dict[str, Any]:
        """
        Prepare aggregated data to be sent to the central server.
        
        Returns:
            A dictionary containing the aggregated data and metadata.
        """
        # Option 1: Send all current sensor readings
        # return {
        #     'sensor_data': self.sensor_data.copy(),
        #     'server_id': self.id
        # }
        
        # Option 2: Send a compact representation (sketch) to minimize bandwidth
        return {
            'server_id': self.id,
            'median_sketch': self.median_sketch,
            'sensor_count': len(self.sensor_data),
            # Also include current values for exact calculation if bandwidth allows
            'sensor_data': self.sensor_data.copy()
        }


class CentralServer:
    """
    Represents the central server that calculates the global median.
    """
    def __init__(self, num_sensors: int, num_aggregation_servers: int):
        """
        Initialize the central server.
        
        Args:
            num_sensors: The total number of sensors in the system.
            num_aggregation_servers: The number of aggregation servers.
        """
        self.num_sensors = num_sensors
        self.num_aggregation_servers = num_aggregation_servers
        self.sensor_server_mapping = {}  # Maps sensor_id to aggregation_server_id
        self.aggregation_servers = []  # List of aggregation server objects
        
        # For storing the latest combined median sketch
        self.combined_sketch = MedianSketch(0, 1000, 100)
        self.last_update_time = None
        
    def update_from_aggregation_servers(self) -> None:
        """
        Collect and process the latest data from all aggregation servers.
        """
        # Reset combined sketch
        self.combined_sketch = MedianSketch(0, 1000, 100)
        
        # Collect data from all aggregation servers
        for server in self.aggregation_servers:
            agg_data = server.get_aggregated_data()
            self.combined_sketch.merge(agg_data['median_sketch'])
            
        self.last_update_time = "now"  # In a real system, this would be a timestamp
        
    def calculate_median(self) -> Union[float, None]:
        """
        Calculate the current global median across all sensor readings.
        
        Returns:
            The global median value, or None if no data is available.
        """
        # Option 1: Collect all current sensor values and calculate exact median
        all_values = []
        
        for server in self.aggregation_servers:
            all_values.extend(server.sensor_data.values())
            
        if not all_values:
            return None
            
        return MedianCalculator.calculate_exact_median(all_values)
        
        # Option 2: Use the combined sketch for an approximate median
        # return self.combined_sketch.estimate_median()
    
    def get_median_estimate(self) -> Dict[str, Any]:
        """
        Return the current median estimate along with metadata.
        
        Returns:
            A dictionary with the median value and related metadata.
        """
        # Update from aggregation servers if needed
        self.update_from_aggregation_servers()
        
        # Calculate the median
        median = self.calculate_median()
        
        return {
            'median': median,
            'last_update_time': self.last_update_time,
            'reporting_sensors': sum(len(server.sensor_data) for server in self.aggregation_servers),
            'total_sensors': self.num_sensors
        }


def create_system(num_sensors: int, num_agg_servers: int) -> Tuple[List[SensorNode], List[AggregationServer], CentralServer]:
    """
    Create and initialize the entire distributed system.
    
    Args:
        num_sensors: The number of sensor nodes to create.
        num_agg_servers: The number of aggregation servers to create.
        
    Returns:
        A tuple containing lists of all sensors, aggregation servers, and the central server.
    """
    # Create sensor -> server mapping (simple round-robin assignment)
    sensor_server_mapping = {}
    for i in range(num_sensors):
        sensor_server_mapping[i] = i % num_agg_servers
    
    # Create central server
    central_server = CentralServer(
        num_sensors=num_sensors,
        num_aggregation_servers=num_agg_servers
    )
    central_server.sensor_server_mapping = sensor_server_mapping
    
    # Create aggregation servers
    agg_servers = [AggregationServer(id=i) for i in range(num_agg_servers)]
    central_server.aggregation_servers = agg_servers
    
    # Create sensors
    sensors = [
        SensorNode(id=i, aggregation_server_id=sensor_server_mapping[i])
        for i in range(num_sensors)
    ]
    
    return sensors, agg_servers, central_server


def simulate_system(num_sensors: int = 100, num_agg_servers: int = 5, iterations: int = 10) -> None:
    """
    Run a simulation of the distributed median calculation system.
    
    Args:
        num_sensors: The number of sensor nodes to simulate.
        num_agg_servers: The number of aggregation servers to simulate.
        iterations: The number of data generation iterations to run.
    """
    # Create the system components
    sensors, agg_servers, central_server = create_system(num_sensors, num_agg_servers)
    
    print(f"Simulating system with {num_sensors} sensors and {num_agg_servers} aggregation servers")
    
    for iteration in range(iterations):
        print(f"\nIteration {iteration+1}:")
        
        # Simulate data generation from sensors
        all_values = []
        for sensor in sensors:
            value = sensor.generate_data()
            all_values.append(value)
            
            # Send to appropriate aggregation server
            server_id = sensor.aggregation_server_id
            agg_servers[server_id].receive_data(sensor.id, value)
        
        # Calculate true median for comparison
        true_median = MedianCalculator.calculate_exact_median(all_values)
        
        # Get median from central server
        estimated_median = central_server.calculate_median()
        
        print(f"True median: {true_median}")
        print(f"Estimated median: {estimated_median}")
        
        if true_median == estimated_median:
            print("✓ Medians match exactly")
        else:
            error = abs(true_median - estimated_median) / max(1, abs(true_median)) * 100
            print(f"Δ Medians differ by {error:.2f}%")


if __name__ == "__main__":
    # Example usage
    simulate_system(num_sensors=100, num_agg_servers=5, iterations=5)