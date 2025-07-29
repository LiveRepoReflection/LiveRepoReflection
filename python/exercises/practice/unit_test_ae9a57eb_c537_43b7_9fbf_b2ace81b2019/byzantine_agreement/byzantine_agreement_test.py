import unittest
from byzantine_agreement import reach_consensus


class ByzantineAgreementTest(unittest.TestCase):
    def test_small_network_no_faulty_nodes(self):
        N = 5
        leader = 0
        proposed_value = 1
        faulty_nodes = set()
        network = [
            [1, 2, 3, 4],
            [0, 2, 3, 4],
            [0, 1, 3, 4],
            [0, 1, 2, 4],
            [0, 1, 2, 3]
        ]
        
        result = reach_consensus(N, leader, proposed_value, faulty_nodes, network)
        
        # All nodes should agree on the leader's value
        for node_id in range(N):
            self.assertEqual(result[node_id], proposed_value)
    
    def test_small_network_one_faulty_node(self):
        N = 5
        leader = 0
        proposed_value = 1
        faulty_nodes = {1}
        network = [
            [1, 2, 3, 4],
            [0, 2, 3, 4],
            [0, 1, 3, 4],
            [0, 1, 2, 4],
            [0, 1, 2, 3]
        ]
        
        result = reach_consensus(N, leader, proposed_value, faulty_nodes, network)
        
        # All loyal nodes should agree on the leader's value
        # The faulty node could have any value
        for node_id in range(N):
            if node_id not in faulty_nodes and node_id != leader:
                self.assertEqual(result[node_id], proposed_value)
        
        # The leader should maintain its proposed value
        self.assertEqual(result[leader], proposed_value)
    
    def test_faulty_leader(self):
        N = 5
        leader = 0
        proposed_value = 1
        faulty_nodes = {0}  # Leader is faulty
        network = [
            [1, 2, 3, 4],
            [0, 2, 3, 4],
            [0, 1, 3, 4],
            [0, 1, 2, 4],
            [0, 1, 2, 3]
        ]
        
        result = reach_consensus(N, leader, proposed_value, faulty_nodes, network)
        
        # Check that all loyal nodes have the same value
        loyal_nodes = [n for n in range(N) if n not in faulty_nodes]
        if loyal_nodes:
            expected_value = result[loyal_nodes[0]]
            for node_id in loyal_nodes:
                self.assertEqual(result[node_id], expected_value)
    
    def test_medium_network_with_multiple_faulty_nodes(self):
        N = 9
        leader = 0
        proposed_value = 0
        faulty_nodes = {1, 2, 3}  # Less than (N-1)/2 = 4
        network = [[j for j in range(N) if j != i] for i in range(N)]
        
        result = reach_consensus(N, leader, proposed_value, faulty_nodes, network)
        
        # All loyal nodes should agree on the same value
        loyal_nodes = [n for n in range(N) if n not in faulty_nodes]
        if loyal_nodes:
            expected_value = result[loyal_nodes[0]]
            for node_id in loyal_nodes:
                self.assertEqual(result[node_id], expected_value)
    
    def test_large_network(self):
        N = 101
        leader = 0
        proposed_value = 1
        faulty_nodes = set(range(1, 50))  # Less than (N-1)/2 = 50
        network = [[j for j in range(N) if j != i] for i in range(N)]
        
        result = reach_consensus(N, leader, proposed_value, faulty_nodes, network)
        
        # All loyal nodes should agree on the same value
        loyal_nodes = [n for n in range(N) if n not in faulty_nodes]
        if loyal_nodes:
            expected_value = result[loyal_nodes[0]]
            for node_id in loyal_nodes:
                self.assertEqual(result[node_id], expected_value)
    
    def test_maximum_allowed_faulty_nodes(self):
        N = 11
        leader = 0
        proposed_value = 1
        faulty_nodes = set(range(1, 6))  # Exactly (N-1)/2 = 5
        network = [[j for j in range(N) if j != i] for i in range(N)]
        
        result = reach_consensus(N, leader, proposed_value, faulty_nodes, network)
        
        # All loyal nodes should agree on the same value
        loyal_nodes = [n for n in range(N) if n not in faulty_nodes]
        if loyal_nodes:
            expected_value = result[loyal_nodes[0]]
            for node_id in loyal_nodes:
                self.assertEqual(result[node_id], expected_value)
    
    def test_disconnected_network(self):
        N = 5
        leader = 0
        proposed_value = 1
        faulty_nodes = set()
        # Node 4 is disconnected from the network
        network = [
            [1, 2, 3],
            [0, 2, 3],
            [0, 1, 3],
            [0, 1, 2],
            []
        ]
        
        result = reach_consensus(N, leader, proposed_value, faulty_nodes, network)
        
        # Nodes 0, 1, 2, 3 should agree on the leader's value
        for node_id in range(4):
            self.assertEqual(result[node_id], proposed_value)
        
        # Node 4 could have any value or None
        self.assertIn(result[4], [0, 1, None])
    
    def test_empty_network(self):
        N = 0
        leader = None
        proposed_value = None
        faulty_nodes = set()
        network = []
        
        result = reach_consensus(N, leader, proposed_value, faulty_nodes, network)
        
        self.assertEqual(result, {})
    
    def test_asymmetric_network(self):
        # A network where some nodes can send to others, but not receive
        N = 5
        leader = 0
        proposed_value = 1
        faulty_nodes = {1}
        network = [
            [1, 2, 3, 4],  # Node 0 can send to all
            [2, 3],        # Node 1 can only send to 2, 3
            [0, 1, 3],     # Node 2 can send to 0, 1, 3
            [0, 1, 2, 4],  # Node 3 can send to 0, 1, 2, 4
            [0, 3]         # Node 4 can only send to 0, 3
        ]
        
        result = reach_consensus(N, leader, proposed_value, faulty_nodes, network)
        
        # Check that all nodes have a value
        for node_id in range(N):
            self.assertIn(result[node_id], [0, 1])

    def test_custom_scenario(self):
        # A specific scenario that might be challenging
        N = 7
        leader = 3
        proposed_value = 0
        faulty_nodes = {0, 5}
        network = [
            [1, 2, 3, 4, 5, 6],  # Node 0
            [0, 2, 3, 4, 5],     # Node 1 (can't send to 6)
            [0, 1, 3, 4],        # Node 2 (can't send to 5, 6)
            [0, 1, 2, 4, 5, 6],  # Node 3 (leader)
            [0, 1, 2, 3, 5, 6],  # Node 4
            [0, 1, 3, 4, 6],     # Node 5
            [0, 3, 4, 5]         # Node 6 (can't send to 1, 2)
        ]
        
        result = reach_consensus(N, leader, proposed_value, faulty_nodes, network)
        
        # Loyal nodes should agree on a value
        loyal_nodes = [n for n in range(N) if n not in faulty_nodes]
        if loyal_nodes:
            expected_value = result[loyal_nodes[0]]
            for node_id in loyal_nodes:
                self.assertEqual(result[node_id], expected_value)


if __name__ == "__main__":
    unittest.main()