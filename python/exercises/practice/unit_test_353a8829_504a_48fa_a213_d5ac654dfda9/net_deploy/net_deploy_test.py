import unittest
from net_deploy import net_deploy

class TestNetDeploy(unittest.TestCase):
    def test_small_network(self):
        N = 3
        K = 2
        adjacency_matrix = [
            [0, 10, 20],
            [10, 0, 30],
            [20, 30, 0]
        ]
        service_dependencies = {1: [0]}
        dependency_latency_threshold = 15
        node_resources = [(100, 100, 100), (100, 100, 100), (100, 100, 100)]
        service_requirements = [(50, 50, 50), (50, 50, 50)]
        replication_factor = 2
        node_failures_tolerated = 1
        service_communication = [
            [0, 100],
            [50, 0]
        ]

        result = net_deploy(
            N, K, adjacency_matrix, service_dependencies,
            dependency_latency_threshold, node_resources,
            service_requirements, replication_factor,
            node_failures_tolerated, service_communication
        )
        
        self.assertEqual(len(result), K)
        for service, nodes in result.items():
            self.assertEqual(len(nodes), replication_factor)
        
        # Verify dependency constraint
        self.assertTrue(
            all(adjacency_matrix[result[1][i]][result[0][j]] <= dependency_latency_threshold
                for i in range(replication_factor)
                for j in range(replication_factor))
        )

    def test_resource_constraints(self):
        N = 2
        K = 2
        adjacency_matrix = [
            [0, 10],
            [10, 0]
        ]
        service_dependencies = {}
        dependency_latency_threshold = 100
        node_resources = [(50, 50, 50), (100, 100, 100)]
        service_requirements = [(60, 60, 60), (50, 50, 50)]
        replication_factor = 1
        node_failures_tolerated = 0
        service_communication = [
            [0, 0],
            [0, 0]
        ]

        result = net_deploy(
            N, K, adjacency_matrix, service_dependencies,
            dependency_latency_threshold, node_resources,
            service_requirements, replication_factor,
            node_failures_tolerated, service_communication
        )
        
        self.assertEqual(result, {})

    def test_fault_tolerance(self):
        N = 4
        K = 1
        adjacency_matrix = [
            [0, 10, 20, 30],
            [10, 0, 40, 50],
            [20, 40, 0, 60],
            [30, 50, 60, 0]
        ]
        service_dependencies = {}
        dependency_latency_threshold = 100
        node_resources = [(100, 100, 100)] * 4
        service_requirements = [(50, 50, 50)]
        replication_factor = 3
        node_failures_tolerated = 1
        service_communication = [
            [0]
        ]

        result = net_deploy(
            N, K, adjacency_matrix, service_dependencies,
            dependency_latency_threshold, node_resources,
            service_requirements, replication_factor,
            node_failures_tolerated, service_communication
        )
        
        self.assertEqual(len(result[0]), replication_factor)
        # Verify any 1 node can fail and still have R instances
        for node_to_remove in range(N):
            remaining_nodes = [n for n in result[0] if n != node_to_remove]
            self.assertGreaterEqual(len(remaining_nodes), replication_factor - node_failures_tolerated)

    def test_complex_dependencies(self):
        N = 5
        K = 3
        adjacency_matrix = [
            [0, 5, 10, 15, 20],
            [5, 0, 8, 12, 18],
            [10, 8, 0, 6, 14],
            [15, 12, 6, 0, 9],
            [20, 18, 14, 9, 0]
        ]
        service_dependencies = {
            1: [0],
            2: [0, 1]
        }
        dependency_latency_threshold = 10
        node_resources = [(100, 100, 100)] * 5
        service_requirements = [(30, 30, 30)] * 3
        replication_factor = 2
        node_failures_tolerated = 1
        service_communication = [
            [0, 50, 30],
            [20, 0, 40],
            [10, 30, 0]
        ]

        result = net_deploy(
            N, K, adjacency_matrix, service_dependencies,
            dependency_latency_threshold, node_resources,
            service_requirements, replication_factor,
            node_failures_tolerated, service_communication
        )
        
        self.assertEqual(len(result), K)
        # Verify all dependencies are satisfied
        for s2 in service_dependencies:
            for s1 in service_dependencies[s2]:
                for node2 in result[s2]:
                    valid = any(adjacency_matrix[node2][node1] <= dependency_latency_threshold
                              for node1 in result[s1])
                    self.assertTrue(valid)

    def test_no_solution(self):
        N = 2
        K = 2
        adjacency_matrix = [
            [0, 100],
            [100, 0]
        ]
        service_dependencies = {1: [0]}
        dependency_latency_threshold = 10
        node_resources = [(100, 100, 100)] * 2
        service_requirements = [(50, 50, 50)] * 2
        replication_factor = 1
        node_failures_tolerated = 0
        service_communication = [
            [0, 0],
            [0, 0]
        ]

        result = net_deploy(
            N, K, adjacency_matrix, service_dependencies,
            dependency_latency_threshold, node_resources,
            service_requirements, replication_factor,
            node_failures_tolerated, service_communication
        )
        
        self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main()