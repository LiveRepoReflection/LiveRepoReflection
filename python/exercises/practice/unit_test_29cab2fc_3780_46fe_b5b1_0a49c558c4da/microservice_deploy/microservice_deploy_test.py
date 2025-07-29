import unittest
import json
from microservice_deploy import deploy_microservices

class TestMicroserviceDeploy(unittest.TestCase):
    
    def test_simple_deployment(self):
        """Test a simple deployment with 2 microservices and 2 servers."""
        input_data = {
            "microservices": [
                {"id": "ms1", "cpu_requirement": 2, "memory_requirement": 4, "bandwidth_requirement": 1},
                {"id": "ms2", "cpu_requirement": 3, "memory_requirement": 2, "bandwidth_requirement": 2}
            ],
            "servers": [
                {"id": "s1", "cpu_capacity": 4, "memory_capacity": 8, "bandwidth_capacity": 2},
                {"id": "s2", "cpu_capacity": 3, "memory_capacity": 4, "bandwidth_capacity": 3}
            ],
            "dependencies": [
                ["ms1", "ms2"]
            ],
            "network_latency": [
                ["s1", "s2", 5]
            ]
        }
        
        result = deploy_microservices(input_data)
        self.assertIsInstance(result, dict)
        self.assertIn("deployment", result)
        
        deployment = result["deployment"]
        self.assertIsInstance(deployment, dict)
        self.assertEqual(len(deployment), 2)
        self.assertIn("ms1", deployment)
        self.assertIn("ms2", deployment)
        
        # Check that microservices are deployed to valid servers
        self.assertIn(deployment["ms1"], ["s1", "s2"])
        self.assertIn(deployment["ms2"], ["s1", "s2"])

    def test_optimal_deployment_example(self):
        """Test an example where the optimal deployment is known."""
        input_data = {
            "microservices": [
                {"id": "ms1", "cpu_requirement": 2, "memory_requirement": 4, "bandwidth_requirement": 1},
                {"id": "ms2", "cpu_requirement": 3, "memory_requirement": 2, "bandwidth_requirement": 1}
            ],
            "servers": [
                {"id": "s1", "cpu_capacity": 4, "memory_requirement": 8, "bandwidth_capacity": 2},
                {"id": "s2", "cpu_capacity": 4, "memory_requirement": 4, "bandwidth_capacity": 2}
            ],
            "dependencies": [
                ["ms1", "ms2"]
            ],
            "network_latency": [
                ["s1", "s2", 10]
            ]
        }
        
        # In this case, optimal deployment should be both microservices on the same server
        # to avoid communication costs
        result = deploy_microservices(input_data)
        deployment = result["deployment"]
        
        # Both should be on same server to avoid high latency cost
        self.assertEqual(deployment["ms1"], deployment["ms2"])

    def test_resource_constraints(self):
        """Test a scenario where resource constraints force microservices to be on different servers."""
        input_data = {
            "microservices": [
                {"id": "ms1", "cpu_requirement": 3, "memory_requirement": 2, "bandwidth_requirement": 1},
                {"id": "ms2", "cpu_requirement": 3, "memory_requirement": 2, "bandwidth_requirement": 1}
            ],
            "servers": [
                {"id": "s1", "cpu_capacity": 4, "memory_capacity": 8, "bandwidth_capacity": 2},
                {"id": "s2", "cpu_capacity": 4, "memory_capacity": 8, "bandwidth_capacity": 2}
            ],
            "dependencies": [
                ["ms1", "ms2"]
            ],
            "network_latency": [
                ["s1", "s2", 1]
            ]
        }
        
        result = deploy_microservices(input_data)
        deployment = result["deployment"]
        
        # Check that we don't exceed CPU capacity on either server
        ms1_server = deployment["ms1"]
        ms2_server = deployment["ms2"]
        
        # If they're on the same server, that server must have enough capacity
        if ms1_server == ms2_server:
            self.assertNotEqual(ms1_server, "s1")  # Can't both be on s1 (would need 6 CPU)

    def test_complex_dependency_graph(self):
        """Test a more complex dependency graph with multiple microservices."""
        input_data = {
            "microservices": [
                {"id": "ms1", "cpu_requirement": 1, "memory_requirement": 2, "bandwidth_requirement": 1},
                {"id": "ms2", "cpu_requirement": 2, "memory_requirement": 2, "bandwidth_requirement": 1},
                {"id": "ms3", "cpu_requirement": 1, "memory_requirement": 3, "bandwidth_requirement": 2},
                {"id": "ms4", "cpu_requirement": 2, "memory_requirement": 1, "bandwidth_requirement": 1},
                {"id": "ms5", "cpu_requirement": 1, "memory_requirement": 1, "bandwidth_requirement": 3}
            ],
            "servers": [
                {"id": "s1", "cpu_capacity": 4, "memory_capacity": 6, "bandwidth_capacity": 4},
                {"id": "s2", "cpu_capacity": 5, "memory_capacity": 5, "bandwidth_capacity": 5}
            ],
            "dependencies": [
                ["ms1", "ms2"],
                ["ms1", "ms3"],
                ["ms2", "ms4"],
                ["ms3", "ms5"],
                ["ms4", "ms5"]
            ],
            "network_latency": [
                ["s1", "s2", 3]
            ]
        }
        
        result = deploy_microservices(input_data)
        self.assertIsInstance(result, dict)
        self.assertIn("deployment", result)
        
        deployment = result["deployment"]
        self.assertEqual(len(deployment), 5)
        for ms_id in ["ms1", "ms2", "ms3", "ms4", "ms5"]:
            self.assertIn(ms_id, deployment)
            self.assertIn(deployment[ms_id], ["s1", "s2"])

    def test_cyclic_dependency_detection(self):
        """Test that the algorithm detects and rejects cyclic dependencies."""
        input_data = {
            "microservices": [
                {"id": "ms1", "cpu_requirement": 1, "memory_requirement": 2, "bandwidth_requirement": 1},
                {"id": "ms2", "cpu_requirement": 2, "memory_requirement": 2, "bandwidth_requirement": 1},
                {"id": "ms3", "cpu_requirement": 1, "memory_requirement": 3, "bandwidth_requirement": 2}
            ],
            "servers": [
                {"id": "s1", "cpu_capacity": 4, "memory_capacity": 8, "bandwidth_capacity": 4},
                {"id": "s2", "cpu_capacity": 4, "memory_capacity": 8, "bandwidth_capacity": 4}
            ],
            "dependencies": [
                ["ms1", "ms2"],
                ["ms2", "ms3"],
                ["ms3", "ms1"]  # This creates a cycle
            ],
            "network_latency": [
                ["s1", "s2", 3]
            ]
        }
        
        with self.assertRaises(ValueError) as context:
            deploy_microservices(input_data)
        self.assertTrue("cyclic dependencies" in str(context.exception).lower())

    def test_disconnected_network(self):
        """Test handling of a disconnected server network."""
        input_data = {
            "microservices": [
                {"id": "ms1", "cpu_requirement": 1, "memory_requirement": 2, "bandwidth_requirement": 1},
                {"id": "ms2", "cpu_requirement": 2, "memory_requirement": 2, "bandwidth_requirement": 1},
            ],
            "servers": [
                {"id": "s1", "cpu_capacity": 4, "memory_capacity": 8, "bandwidth_capacity": 4},
                {"id": "s2", "cpu_capacity": 4, "memory_capacity": 8, "bandwidth_capacity": 4},
                {"id": "s3", "cpu_capacity": 4, "memory_capacity": 8, "bandwidth_capacity": 4}
            ],
            "dependencies": [
                ["ms1", "ms2"]
            ],
            "network_latency": [
                ["s1", "s2", 3]
                # s3 is disconnected
            ]
        }
        
        result = deploy_microservices(input_data)
        deployment = result["deployment"]
        
        # ms1 and ms2 should be deployed either both on s1 or both on s2, not on s3
        self.assertIn(deployment["ms1"], ["s1", "s2"])
        self.assertIn(deployment["ms2"], ["s1", "s2"])
        # They should be on the same server to avoid infinite latency cost
        self.assertEqual(deployment["ms1"], deployment["ms2"])

    def test_no_feasible_deployment(self):
        """Test handling when no feasible deployment exists."""
        input_data = {
            "microservices": [
                {"id": "ms1", "cpu_requirement": 5, "memory_requirement": 10, "bandwidth_requirement": 5},
                {"id": "ms2", "cpu_requirement": 5, "memory_requirement": 10, "bandwidth_requirement": 5}
            ],
            "servers": [
                {"id": "s1", "cpu_capacity": 4, "memory_capacity": 8, "bandwidth_capacity": 4},
                {"id": "s2", "cpu_capacity": 4, "memory_capacity": 8, "bandwidth_capacity": 4}
            ],
            "dependencies": [
                ["ms1", "ms2"]
            ],
            "network_latency": [
                ["s1", "s2", 3]
            ]
        }
        
        # Since individual microservice requirements exceed server capacities, 
        # there should be a high resource violation penalty, but we still expect a result
        result = deploy_microservices(input_data)
        self.assertIsInstance(result, dict)
        self.assertIn("deployment", result)

    def test_large_scale_deployment(self):
        """Test algorithm performance and correctness with a larger input."""
        # Generate 20 microservices with random requirements
        microservices = []
        for i in range(1, 21):
            ms_id = f"ms{i}"
            cpu_req = i % 3 + 1  # 1-3 CPU units
            mem_req = i % 4 + 1  # 1-4 Memory units
            bw_req = i % 2 + 1   # 1-2 Bandwidth units
            microservices.append({
                "id": ms_id, 
                "cpu_requirement": cpu_req, 
                "memory_requirement": mem_req, 
                "bandwidth_requirement": bw_req
            })
        
        # Generate 5 servers with varied capacities
        servers = []
        for i in range(1, 6):
            server_id = f"s{i}"
            cpu_cap = (i + 2) * 3  # 9-21 CPU units
            mem_cap = (i + 2) * 4  # 12-28 Memory units
            bw_cap = (i + 2) * 2   # 6-14 Bandwidth units
            servers.append({
                "id": server_id, 
                "cpu_capacity": cpu_cap, 
                "memory_capacity": mem_cap, 
                "bandwidth_capacity": bw_cap
            })
        
        # Generate dependencies - tree-like structure to avoid cycles
        dependencies = []
        for i in range(2, 21):
            parent = f"ms{i//2}"
            child = f"ms{i}"
            dependencies.append([parent, child])
        
        # Generate network topology - all servers connected
        network_latency = []
        for i in range(1, 5):
            for j in range(i+1, 6):
                latency = (i + j) % 5 + 1  # 1-5 units of latency
                network_latency.append([f"s{i}", f"s{j}", latency])
        
        input_data = {
            "microservices": microservices,
            "servers": servers,
            "dependencies": dependencies,
            "network_latency": network_latency
        }
        
        import time
        start_time = time.time()
        result = deploy_microservices(input_data)
        end_time = time.time()
        
        # Check execution time is reasonable (should be under 30 seconds for this size)
        self.assertLess(end_time - start_time, 30)
        
        # Validate result structure
        self.assertIsInstance(result, dict)
        self.assertIn("deployment", result)
        deployment = result["deployment"]
        self.assertEqual(len(deployment), 20)
        
        # Check all microservices are deployed to valid servers
        for ms_id in [f"ms{i}" for i in range(1, 21)]:
            self.assertIn(ms_id, deployment)
            self.assertIn(deployment[ms_id], [f"s{i}" for i in range(1, 6)])

if __name__ == '__main__':
    unittest.main()