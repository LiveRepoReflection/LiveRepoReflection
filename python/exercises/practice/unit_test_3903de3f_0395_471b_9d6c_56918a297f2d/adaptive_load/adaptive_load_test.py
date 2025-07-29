import unittest
from adaptive_load import adaptive_load

class AdaptiveLoadTest(unittest.TestCase):
    def test_basic_load_balancing(self):
        N = 3
        server_capacities = [(100, 100, 100), (50, 50, 50), (75, 75, 75)]
        server_weights = [1.0, 0.5, 0.75]
        requests = [(10, 10, 10), (20, 20, 20), (30, 30, 30), (10, 10, 10), (40, 40, 40)]
        
        assignments = adaptive_load(N, server_capacities, server_weights, requests)
        
        # Check that assignments are valid indices or -1
        for assignment in assignments:
            self.assertTrue(-1 <= assignment < N)
        
        # Verify server capacity constraints are not violated
        server_loads = [(0, 0, 0) for _ in range(N)]
        for i, assignment in enumerate(assignments):
            if assignment != -1:
                cpu_req, mem_req, net_req = requests[i]
                cpu_load, mem_load, net_load = server_loads[assignment]
                
                # Update loads
                server_loads[assignment] = (
                    cpu_load + cpu_req,
                    mem_load + mem_req,
                    net_load + net_req
                )
                
                # Check capacity not exceeded
                self.assertLessEqual(server_loads[assignment][0], server_capacities[assignment][0])
                self.assertLessEqual(server_loads[assignment][1], server_capacities[assignment][1])
                self.assertLessEqual(server_loads[assignment][2], server_capacities[assignment][2])
    
    def test_empty_requests(self):
        N = 3
        server_capacities = [(100, 100, 100), (50, 50, 50), (75, 75, 75)]
        server_weights = [1.0, 0.5, 0.75]
        requests = []
        
        assignments = adaptive_load(N, server_capacities, server_weights, requests)
        self.assertEqual(assignments, [])
    
    def test_all_servers_full(self):
        N = 2
        server_capacities = [(10, 10, 10), (10, 10, 10)]
        server_weights = [1.0, 1.0]
        requests = [(10, 10, 10), (10, 10, 10), (10, 10, 10)]
        
        assignments = adaptive_load(N, server_capacities, server_weights, requests)
        # First two requests should be assigned, third should be -1
        self.assertEqual(len(assignments), 3)
        self.assertNotEqual(assignments[0], -1)
        self.assertNotEqual(assignments[1], -1)
        self.assertEqual(assignments[2], -1)
    
    def test_large_request(self):
        N = 2
        server_capacities = [(50, 50, 50), (30, 30, 30)]
        server_weights = [1.0, 0.8]
        requests = [(60, 60, 60), (20, 20, 20)]
        
        assignments = adaptive_load(N, server_capacities, server_weights, requests)
        self.assertEqual(assignments[0], -1)  # Too large for any server
        self.assertNotEqual(assignments[1], -1)  # Should fit on a server
    
    def test_heterogeneous_servers(self):
        N = 3
        server_capacities = [(100, 50, 75), (50, 150, 25), (75, 25, 100)]
        server_weights = [1.0, 0.8, 1.2]
        requests = [(30, 20, 10), (10, 80, 5), (20, 10, 50)]
        
        assignments = adaptive_load(N, server_capacities, server_weights, requests)
        
        # Each request should be routed to a server that has capacity
        for i, assignment in enumerate(assignments):
            self.assertNotEqual(assignment, -1)
            
            # Request should fit on assigned server
            cpu_req, mem_req, net_req = requests[i]
            server_cpu, server_mem, server_net = server_capacities[assignment]
            
            self.assertLessEqual(cpu_req, server_cpu)
            self.assertLessEqual(mem_req, server_mem)
            self.assertLessEqual(net_req, server_net)
    
    def test_adaptive_behavior(self):
        N = 2
        server_capacities = [(100, 100, 100), (100, 100, 100)]
        server_weights = [1.0, 0.5]  # First server is faster
        
        # Create requests that will gradually fill servers
        requests = [(20, 20, 20) for _ in range(9)]
        
        assignments = adaptive_load(N, server_capacities, server_weights, requests)
        
        # Count assignments to each server
        server_0_count = assignments.count(0)
        server_1_count = assignments.count(1)
        
        # The faster server should get more requests initially
        self.assertGreaterEqual(server_0_count, server_1_count)
    
    def test_edge_case_single_server(self):
        N = 1
        server_capacities = [(50, 50, 50)]
        server_weights = [1.0]
        requests = [(20, 20, 20), (20, 20, 20), (20, 20, 20)]
        
        assignments = adaptive_load(N, server_capacities, server_weights, requests)
        
        # First two requests should go to server 0, third should be -1
        self.assertEqual(assignments[0], 0)
        self.assertEqual(assignments[1], 0)
        self.assertEqual(assignments[2], -1)
    
    def test_single_resource_bottleneck(self):
        N = 2
        server_capacities = [(100, 20, 100), (20, 100, 100)]
        server_weights = [1.0, 1.0]
        requests = [(10, 10, 10), (10, 10, 10), (10, 10, 10)]
        
        assignments = adaptive_load(N, server_capacities, server_weights, requests)
        
        # All three requests should be assigned
        self.assertEqual(len(assignments), 3)
        self.assertTrue(all(a != -1 for a in assignments))
        
        # Check that load is properly distributed based on bottleneck resources
        server_loads = [(0, 0, 0), (0, 0, 0)]
        for i, assignment in enumerate(assignments):
            cpu_req, mem_req, net_req = requests[i]
            cpu_load, mem_load, net_load = server_loads[assignment]
            
            # Update loads
            server_loads[assignment] = (
                cpu_load + cpu_req,
                mem_load + mem_req,
                net_load + net_req
            )
        
        # Memory on server 0 and CPU on server 1 are bottlenecks
        self.assertLessEqual(server_loads[0][1], 20)  # Memory on server 0
        self.assertLessEqual(server_loads[1][0], 20)  # CPU on server 1

if __name__ == '__main__':
    unittest.main()