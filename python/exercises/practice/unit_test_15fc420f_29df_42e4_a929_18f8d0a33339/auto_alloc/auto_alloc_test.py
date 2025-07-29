import unittest

# Assume that the solution implementation is provided in auto_alloc/auto_alloc.py
# and that it contains a function allocate_resource(request, vm_types, infrastructure)
from auto_alloc.auto_alloc import allocate_resource

class TestAutoAlloc(unittest.TestCase):
    def setUp(self):
        # Define VM types
        self.vm_types = [
            {
                "id": "vm_small",
                "cpu": 2,
                "memory": 4,
                "storage": 50,
                "cost_per_hour": 0.1,
                "performance_score": 100
            },
            {
                "id": "vm_medium",
                "cpu": 4,
                "memory": 8,
                "storage": 100,
                "cost_per_hour": 0.2,
                "performance_score": 200
            },
            {
                "id": "vm_large",
                "cpu": 8,
                "memory": 16,
                "storage": 200,
                "cost_per_hour": 0.4,
                "performance_score": 300
            }
        ]
        
        # Define infrastructure with PM nodes and edges
        self.infrastructure_nodes = [
            {
                "id": "pm1",
                "available_cpu": 8,
                "available_memory": 16,
                "available_storage": 200,
                "cost_per_hour": 0.05
            },
            {
                "id": "pm2",
                "available_cpu": 4,
                "available_memory": 8,
                "available_storage": 100,
                "cost_per_hour": 0.03
            }
        ]
        
        self.infrastructure_edges = [
            {
                "source": "pm1",
                "destination": "pm2",
                "latency": 10,
                "bandwidth": 100
            },
            {
                "source": "pm2",
                "destination": "pm1",
                "latency": 12,
                "bandwidth": 100
            }
        ]
        
        self.infrastructure = {
            "nodes": self.infrastructure_nodes,
            "edges": self.infrastructure_edges
        }

    def test_simple_allocation(self):
        # Test a basic allocation scenario
        request = {
            "request_id": "req1",
            "required_cpu": 2,
            "required_memory": 4,
            "expected_performance_score": 90,
            "max_latency": 15,
            "duration": 5
        }
        allocation = allocate_resource(request, self.vm_types, self.infrastructure)
        self.assertEqual(allocation["request_id"], "req1")
        self.assertIn(allocation["vm_id"], {"vm_small", "vm_medium", "vm_large"})
        self.assertIn(allocation["pm_id"], {"pm1", "pm2"})
        self.assertIsInstance(allocation["total_cost"], float)

    def test_no_suitable_vm(self):
        # Test case where the request requires performance that no VM type can provide
        request = {
            "request_id": "req2",
            "required_cpu": 8,
            "required_memory": 16,
            "expected_performance_score": 1000,  # Exceeds available performance scores
            "max_latency": 15,
            "duration": 2
        }
        with self.assertRaises(Exception):
            allocate_resource(request, self.vm_types, self.infrastructure)

    def test_latency_constraint(self):
        # Test a scenario where the max_latency constraint forces the allocation to choose a single PM
        infra_nodes = [
            {
                "id": "pm3",
                "available_cpu": 8,
                "available_memory": 16,
                "available_storage": 200,
                "cost_per_hour": 0.05
            },
            {
                "id": "pm4",
                "available_cpu": 8,
                "available_memory": 16,
                "available_storage": 200,
                "cost_per_hour": 0.05
            }
        ]
        infra_edges = [
            {
                "source": "pm3",
                "destination": "pm4",
                "latency": 50,
                "bandwidth": 100
            },
            {
                "source": "pm4",
                "destination": "pm3",
                "latency": 50,
                "bandwidth": 100
            }
        ]
        infra = {"nodes": infra_nodes, "edges": infra_edges}
        
        request = {
            "request_id": "req3",
            "required_cpu": 2,
            "required_memory": 4,
            "expected_performance_score": 80,
            "max_latency": 30,  # latency requirement is less than edge latency of 50
            "duration": 3
        }
        allocation = allocate_resource(request, self.vm_types, infra)
        # The allocation should select one of the PMs without trying to combine VMs across these nodes
        self.assertIn(allocation["pm_id"], {"pm3", "pm4"})

    def test_cost_optimization(self):
        # Test that the total cost is calculated correctly given the VM and PM costs and the duration
        request = {
            "request_id": "req4",
            "required_cpu": 4,
            "required_memory": 8,
            "expected_performance_score": 150,
            "max_latency": 20,
            "duration": 10
        }
        allocation = allocate_resource(request, self.vm_types, self.infrastructure)
        vm = next((v for v in self.vm_types if v["id"] == allocation["vm_id"]), None)
        pm = next((p for p in self.infrastructure_nodes if p["id"] == allocation["pm_id"]), None)
        expected_cost = (vm["cost_per_hour"] + pm["cost_per_hour"]) * request["duration"]
        self.assertAlmostEqual(allocation["total_cost"], expected_cost, places=5)

    def test_multiple_allocations(self):
        # Test sequential allocations and ensure resources are not over-allocated.
        # First allocation
        request1 = {
            "request_id": "req5",
            "required_cpu": 2,
            "required_memory": 4,
            "expected_performance_score": 80,
            "max_latency": 20,
            "duration": 4
        }
        allocation1 = allocate_resource(request1, self.vm_types, self.infrastructure)
        # Simulate resource update: deduct allocated resources from chosen PM.
        for node in self.infrastructure["nodes"]:
            if node["id"] == allocation1["pm_id"]:
                allocated_vm = next(v for v in self.vm_types if v["id"] == allocation1["vm_id"])
                node["available_cpu"] -= allocated_vm["cpu"]
                node["available_memory"] -= allocated_vm["memory"]
                node["available_storage"] -= allocated_vm["storage"]

        # Second allocation that might fail on the same PM due to resource constraints.
        request2 = {
            "request_id": "req6",
            "required_cpu": 8,
            "required_memory": 16,
            "expected_performance_score": 250,
            "max_latency": 20,
            "duration": 6
        }
        allocation2 = allocate_resource(request2, self.vm_types, self.infrastructure)
        self.assertNotEqual(allocation1["pm_id"], allocation2["pm_id"])

if __name__ == '__main__':
    unittest.main()