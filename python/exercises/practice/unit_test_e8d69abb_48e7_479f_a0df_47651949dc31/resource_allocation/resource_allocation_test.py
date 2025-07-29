import unittest
from resource_allocation import allocate_resources


class ResourceAllocationTest(unittest.TestCase):
    def test_simple_allocation(self):
        microservices = [(2, 4096, 50), (1, 2048, 20), (3, 8192, 100), (1, 1024, 10)]
        servers = [(4, 16384, 200)]
        self.assertEqual(allocate_resources(microservices, servers), 2)

    def test_exact_fit(self):
        microservices = [(2, 4096, 50), (2, 4096, 50)]
        servers = [(4, 8192, 100)]
        self.assertEqual(allocate_resources(microservices, servers), 1)

    def test_unable_to_fit(self):
        # One microservice is too large for any server
        microservices = [(5, 4096, 50), (2, 4096, 50)]
        servers = [(4, 8192, 100)]
        self.assertEqual(allocate_resources(microservices, servers), -1)

    def test_empty_microservices(self):
        microservices = []
        servers = [(4, 8192, 100)]
        self.assertEqual(allocate_resources(microservices, servers), 0)

    def test_empty_servers(self):
        microservices = [(2, 4096, 50)]
        servers = []
        self.assertEqual(allocate_resources(microservices, servers), -1)

    def test_large_number_of_microservices(self):
        # 100 small microservices that should fit on 10 servers
        microservices = [(1, 1000, 10)] * 100
        servers = [(10, 10000, 100)]
        self.assertEqual(allocate_resources(microservices, servers), 10)

    def test_tight_resource_constraints(self):
        # Test with tight constraints on different resource types
        microservices = [
            (3, 1000, 10),  # CPU intensive
            (1, 8000, 10),  # RAM intensive
            (1, 1000, 90),  # Disk intensive
            (2, 2000, 20)   # Balanced
        ]
        servers = [(4, 8192, 100)]
        self.assertEqual(allocate_resources(microservices, servers), 3)

    def test_multiple_server_types(self):
        microservices = [(2, 4000, 50), (3, 6000, 70)]
        servers = [(3, 8000, 100), (4, 10000, 120)]  # Different server types
        self.assertEqual(allocate_resources(microservices, servers), 2)

    def test_edge_case_resource_match(self):
        # Exactly matching server resources
        microservices = [(4, 16384, 200)]
        servers = [(4, 16384, 200)]
        self.assertEqual(allocate_resources(microservices, servers), 1)

    def test_large_variation_in_microservice_sizes(self):
        microservices = [
            (1, 1000, 10),    # Very small
            (3, 14000, 180),  # Almost fills a server
            (2, 2000, 20),    # Medium
            (1, 500, 5)       # Tiny
        ]
        servers = [(4, 16384, 200)]
        self.assertEqual(allocate_resources(microservices, servers), 2)

    def test_complex_packing_scenario(self):
        # A more complex scenario requiring careful packing
        microservices = [
            (2, 5000, 60),
            (2, 6000, 70),
            (1, 3000, 40),
            (3, 8000, 90),
            (1, 2000, 30),
            (2, 4000, 50)
        ]
        servers = [(4, 16384, 200)]
        self.assertEqual(allocate_resources(microservices, servers), 3)
    
    def test_all_resources_matter(self):
        # Test where all three resource types (CPU, RAM, disk) are constraining factors
        microservices = [
            (4, 5000, 50),    # CPU constrained
            (2, 16000, 50),   # RAM constrained
            (2, 5000, 200)    # Disk constrained
        ]
        servers = [(4, 16384, 200)]
        self.assertEqual(allocate_resources(microservices, servers), 3)

    def test_large_number_with_impossible_allocation(self):
        # 99 small microservices that fit, but one that doesn't
        microservices = [(1, 1000, 10)] * 99 + [(5, 20000, 300)]
        servers = [(4, 16384, 200)]
        self.assertEqual(allocate_resources(microservices, servers), -1)


if __name__ == '__main__':
    unittest.main()