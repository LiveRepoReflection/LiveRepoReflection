import unittest
from unittest.mock import MagicMock, patch
from data_median import (
    SensorNode,
    AggregationServer,
    CentralServer,
    MedianCalculator
)
import random

class TestSensorNode(unittest.TestCase):
    def test_sensor_initialization(self):
        sensor = SensorNode(id=1, aggregation_server_id=2)
        self.assertEqual(sensor.id, 1)
        self.assertEqual(sensor.aggregation_server_id, 2)
        
    def test_sensor_generate_data(self):
        sensor = SensorNode(id=1, aggregation_server_id=2)
        data = sensor.generate_data()
        self.assertIsInstance(data, int)
        
    def test_sensor_send_data(self):
        sensor = SensorNode(id=1, aggregation_server_id=2)
        mock_server = MagicMock()
        sensor.send_data_to_server(mock_server, 42)
        mock_server.receive_data.assert_called_once_with(1, 42)


class TestAggregationServer(unittest.TestCase):
    def test_aggregation_server_initialization(self):
        server = AggregationServer(id=1)
        self.assertEqual(server.id, 1)
        self.assertEqual(len(server.sensor_data), 0)
        
    def test_receive_data(self):
        server = AggregationServer(id=1)
        server.receive_data(sensor_id=2, data=42)
        self.assertIn(2, server.sensor_data)
        self.assertEqual(server.sensor_data[2], 42)
        
    def test_get_aggregated_data(self):
        server = AggregationServer(id=1)
        server.receive_data(sensor_id=2, data=42)
        server.receive_data(sensor_id=3, data=100)
        aggregated_data = server.get_aggregated_data()
        self.assertIsNotNone(aggregated_data)


class TestCentralServer(unittest.TestCase):
    def setUp(self):
        self.central_server = CentralServer(num_sensors=6, num_aggregation_servers=2)
        self.central_server.sensor_server_mapping = {
            0: 0, 1: 0, 2: 0,  # First 3 sensors assigned to aggregation server 0
            3: 1, 4: 1, 5: 1   # Next 3 sensors assigned to aggregation server 1
        }
        self.agg_server0 = AggregationServer(id=0)
        self.agg_server1 = AggregationServer(id=1)
        self.central_server.aggregation_servers = [self.agg_server0, self.agg_server1]
    
    def test_central_server_initialization(self):
        self.assertEqual(self.central_server.num_sensors, 6)
        self.assertEqual(self.central_server.num_aggregation_servers, 2)
        
    def test_calculate_median_with_no_data(self):
        median = self.central_server.calculate_median()
        self.assertIsNone(median)
        
    def test_calculate_median_with_data(self):
        # Simulate data received by aggregation servers
        self.agg_server0.receive_data(0, 10)
        self.agg_server0.receive_data(1, 20)
        self.agg_server0.receive_data(2, 30)
        
        self.agg_server1.receive_data(3, 40)
        self.agg_server1.receive_data(4, 50)
        self.agg_server1.receive_data(5, 60)
        
        median = self.central_server.calculate_median()
        # Expected median is (30 + 40) / 2 = 35
        self.assertEqual(median, 35)
        
    def test_calculate_median_with_missing_data(self):
        # Some sensors don't report data
        self.agg_server0.receive_data(0, 10)
        self.agg_server0.receive_data(2, 30)
        
        self.agg_server1.receive_data(4, 50)
        
        median = self.central_server.calculate_median()
        # Expected median is 30 (the middle value from 10, 30, 50)
        self.assertEqual(median, 30)
        
    def test_calculate_median_with_duplicate_values(self):
        self.agg_server0.receive_data(0, 10)
        self.agg_server0.receive_data(1, 10)
        self.agg_server0.receive_data(2, 20)
        
        self.agg_server1.receive_data(3, 20)
        self.agg_server1.receive_data(4, 30)
        
        median = self.central_server.calculate_median()
        # Expected median is 20 (the values are 10, 10, 20, 20, 30)
        self.assertEqual(median, 20)


class TestMedianCalculator(unittest.TestCase):
    def test_exact_median_odd_length(self):
        data = [3, 1, 4, 2, 5]
        median = MedianCalculator.calculate_exact_median(data)
        self.assertEqual(median, 3)
        
    def test_exact_median_even_length(self):
        data = [3, 1, 4, 2]
        median = MedianCalculator.calculate_exact_median(data)
        self.assertEqual(median, 2.5)
        
    def test_approximate_median(self):
        # This test will depend on your implementation
        data = list(range(1, 101))  # 1 to 100
        approx_median = MedianCalculator.calculate_approximate_median(data)
        # The exact median would be 50.5, check if approximate is close
        self.assertTrue(45 <= approx_median <= 55)


class TestSystemIntegration(unittest.TestCase):
    def setUp(self):
        # Create a simulated system with sensors, aggregation servers, and central server
        self.num_sensors = 10
        self.num_agg_servers = 2
        
        # Create sensor -> server mapping
        self.sensor_server_mapping = {}
        for i in range(self.num_sensors):
            self.sensor_server_mapping[i] = i % self.num_agg_servers
        
        # Create central server
        self.central_server = CentralServer(
            num_sensors=self.num_sensors,
            num_aggregation_servers=self.num_agg_servers
        )
        self.central_server.sensor_server_mapping = self.sensor_server_mapping
        
        # Create aggregation servers
        self.agg_servers = [AggregationServer(id=i) for i in range(self.num_agg_servers)]
        self.central_server.aggregation_servers = self.agg_servers
        
        # Create sensors
        self.sensors = [
            SensorNode(id=i, aggregation_server_id=self.sensor_server_mapping[i])
            for i in range(self.num_sensors)
        ]
    
    def test_system_with_random_data(self):
        # Generate random data for each sensor
        data_values = []
        
        for sensor in self.sensors:
            value = random.randint(1, 100)
            data_values.append(value)
            # Send data to appropriate aggregation server
            agg_server = self.agg_servers[sensor.aggregation_server_id]
            sensor.send_data_to_server(agg_server, value)
        
        # Calculate expected median
        expected_median = MedianCalculator.calculate_exact_median(data_values)
        
        # Calculate median through the system
        calculated_median = self.central_server.calculate_median()
        
        # Verify the calculated median is correct
        self.assertEqual(calculated_median, expected_median)
    
    def test_system_with_large_data_volume(self):
        # Test performance with larger data volume
        data_values = []
        
        for _ in range(5):  # Simulate multiple data points per sensor
            for sensor in self.sensors:
                value = random.randint(1, 1000)
                data_values.append(value)
                agg_server = self.agg_servers[sensor.aggregation_server_id]
                sensor.send_data_to_server(agg_server, value)
        
        # Calculate median - this should handle the larger data volume
        calculated_median = self.central_server.calculate_median()
        self.assertIsNotNone(calculated_median)
    
    def test_system_with_server_failure(self):
        # Simulate some data
        values_sent_to_server0 = []
        values_sent_to_server1 = []
        
        for sensor in self.sensors:
            value = random.randint(1, 100)
            if sensor.aggregation_server_id == 0:
                values_sent_to_server0.append(value)
            else:
                values_sent_to_server1.append(value)
            
            # Send data to appropriate aggregation server
            agg_server = self.agg_servers[sensor.aggregation_server_id]
            sensor.send_data_to_server(agg_server, value)
        
        # Calculate median with all servers
        original_median = self.central_server.calculate_median()
        
        # Simulate failure of aggregation server 0
        self.central_server.aggregation_servers = [self.agg_servers[1]]
        
        # Calculate new median with only server 1
        failover_median = self.central_server.calculate_median()
        
        # The new median should only consider data from server 1
        expected_failover_median = MedianCalculator.calculate_exact_median(values_sent_to_server1)
        self.assertEqual(failover_median, expected_failover_median)


if __name__ == '__main__':
    unittest.main()