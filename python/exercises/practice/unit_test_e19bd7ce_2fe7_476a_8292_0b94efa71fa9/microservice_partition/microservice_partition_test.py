import unittest
from microservice_partition import partition_microservices

class MicroservicePartitionTest(unittest.TestCase):
    def test_simple_partition(self):
        N = 4
        C = [
            [0, 10, 0, 5],
            [10, 0, 8, 0],
            [0, 8, 0, 20],
            [5, 0, 20, 0]
        ]
        R = [40, 30, 20, 10]
        K = 100
        dependencies = [(0, 1), (2, 3)]
        
        result = partition_microservices(N, C, R, K, dependencies)
        
        # Verify type and structure of result
        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(cluster, set) for cluster in result))
        
        # Check that all microservices are assigned to exactly one cluster
        all_services = set()
        for cluster in result:
            all_services.update(cluster)
        self.assertEqual(all_services, set(range(N)))
        
        # Check that there's no overlap between clusters
        for i in range(len(result)):
            for j in range(i + 1, len(result)):
                self.assertEqual(len(result[i].intersection(result[j])), 0)
        
        # Check cluster capacity constraints
        for cluster in result:
            total_resources = sum(R[service] for service in cluster)
            self.assertLessEqual(total_resources, K)
            
    def test_single_cluster(self):
        N = 3
        C = [
            [0, 100, 100],
            [100, 0, 100],
            [100, 100, 0]
        ]
        R = [30, 30, 30]
        K = 100
        dependencies = [(0, 1), (1, 2), (2, 0)]
        
        result = partition_microservices(N, C, R, K, dependencies)
        
        # Expect a single cluster for this high-communication scenario
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {0, 1, 2})
        
    def test_multiple_clusters(self):
        N = 6
        C = [
            [0, 100, 80, 0, 0, 0],
            [100, 0, 90, 0, 0, 0],
            [80, 90, 0, 0, 0, 0],
            [0, 0, 0, 0, 100, 90],
            [0, 0, 0, 100, 0, 80],
            [0, 0, 0, 90, 80, 0]
        ]
        R = [40, 30, 30, 40, 30, 30]
        K = 100
        dependencies = [(0, 1), (1, 2), (3, 4), (4, 5)]
        
        result = partition_microservices(N, C, R, K, dependencies)
        
        # Expect services 0,1,2 to be grouped and 3,4,5 to be grouped
        self.assertEqual(len(result), 2)
        
        # Get the cluster containing service 0
        cluster_with_0 = next(cluster for cluster in result if 0 in cluster)
        self.assertTrue(1 in cluster_with_0 and 2 in cluster_with_0)
        
        # Get the cluster containing service 3
        cluster_with_3 = next(cluster for cluster in result if 3 in cluster)
        self.assertTrue(4 in cluster_with_3 and 5 in cluster_with_3)
        
    def test_exceeds_capacity(self):
        N = 4
        C = [
            [0, 10, 20, 30],
            [10, 0, 40, 50],
            [20, 40, 0, 60],
            [30, 50, 60, 0]
        ]
        R = [40, 30, 20, 120]  # Service 3 exceeds cluster capacity
        K = 100
        dependencies = []
        
        result = partition_microservices(N, C, R, K, dependencies)
        
        # Should return None since service 3 exceeds capacity
        self.assertIsNone(result)
        
    def test_tight_capacity_constraints(self):
        N = 5
        C = [
            [0, 10, 0, 0, 0],
            [10, 0, 0, 0, 0],
            [0, 0, 0, 10, 0],
            [0, 0, 10, 0, 0],
            [0, 0, 0, 0, 0]
        ]
        R = [50, 50, 50, 50, 90]
        K = 100
        dependencies = []
        
        result = partition_microservices(N, C, R, K, dependencies)
        
        # Verify that all capacity constraints are met
        for cluster in result:
            total_resources = sum(R[service] for service in cluster)
            self.assertLessEqual(total_resources, K)
        
        # Verify that microservices with high communication are grouped together
        service_0_cluster = next(cluster for cluster in result if 0 in cluster)
        service_2_cluster = next(cluster for cluster in result if 2 in cluster)
        
        self.assertTrue(1 in service_0_cluster)  # 0 and 1 should be together
        self.assertTrue(3 in service_2_cluster)  # 2 and 3 should be together
        
    def test_complex_case(self):
        N = 10
        # Create a communication matrix where odd-indexed services communicate with each other
        # and even-indexed services communicate with each other
        C = [[0 for _ in range(N)] for _ in range(N)]
        for i in range(N):
            for j in range(N):
                if i != j and i % 2 == j % 2:
                    C[i][j] = 100
        
        R = [25, 25, 25, 25, 25, 25, 25, 25, 25, 25]
        K = 100
        dependencies = [(0, 2), (1, 3), (4, 6), (5, 7), (8, 0), (9, 1)]
        
        result = partition_microservices(N, C, R, K, dependencies)
        
        # Verify solution validity
        self.assertIsNotNone(result)
        
        # Check that all microservices are assigned
        assigned_services = set()
        for cluster in result:
            assigned_services.update(cluster)
        self.assertEqual(assigned_services, set(range(N)))
        
        # Check capacity constraints
        for cluster in result:
            total_resources = sum(R[service] for service in cluster)
            self.assertLessEqual(total_resources, K)
            
    def test_dependencies_versus_communication(self):
        N = 6
        # Services 0,1,2 have high communication
        # Services 3,4,5 have high communication
        # But dependencies try to group 0,3 and 1,4 and 2,5
        C = [
            [0, 90, 90, 10, 10, 10],
            [90, 0, 90, 10, 10, 10],
            [90, 90, 0, 10, 10, 10],
            [10, 10, 10, 0, 90, 90],
            [10, 10, 10, 90, 0, 90],
            [10, 10, 10, 90, 90, 0]
        ]
        R = [30, 30, 30, 30, 30, 30]
        K = 100
        dependencies = [(0, 3), (1, 4), (2, 5)]
        
        result = partition_microservices(N, C, R, K, dependencies)
        
        # Check that solution exists and respects capacity
        self.assertIsNotNone(result)
        for cluster in result:
            total_resources = sum(R[service] for service in cluster)
            self.assertLessEqual(total_resources, K)
        
        # Calculate the total inter-cluster communication cost
        inter_cluster_cost = 0
        for i in range(N):
            for j in range(N):
                if i == j:
                    continue
                    
                # Find clusters for i and j
                cluster_i = next(cluster for cluster in result if i in cluster)
                cluster_j = next(cluster for cluster in result if j in cluster)
                
                if cluster_i != cluster_j:
                    inter_cluster_cost += C[i][j]
        
        # The solution should prioritize minimizing communication cost
        # rather than keeping all dependent services together
        # This is more of a heuristic test, as optimal grouping depends on the algorithm
        self.assertLess(inter_cluster_cost, 1000)  # Arbitrary threshold
            
    def test_large_scale(self):
        N = 100
        # Create a sparse communication matrix
        C = [[0 for _ in range(N)] for _ in range(N)]
        for i in range(N):
            for j in range(max(0, i-5), min(N, i+6)):
                if i != j:
                    C[i][j] = 10
        
        # Every 10th service has high communication with all others in its group
        for group in range(10):
            base = group * 10
            for i in range(base, base + 10):
                for j in range(base, base + 10):
                    if i != j:
                        C[i][j] = 100
        
        R = [5 for _ in range(N)]
        K = 50
        dependencies = [(i, (i+1) % N) for i in range(N)]
        
        result = partition_microservices(N, C, R, K, dependencies)
        
        # Verify basic properties
        self.assertIsNotNone(result)
        
        # All microservices should be assigned
        assigned = set()
        for cluster in result:
            assigned.update(cluster)
        self.assertEqual(assigned, set(range(N)))
        
        # Check capacity constraints
        for cluster in result:
            total_resources = sum(R[service] for service in cluster)
            self.assertLessEqual(total_resources, K)

if __name__ == '__main__':
    unittest.main()