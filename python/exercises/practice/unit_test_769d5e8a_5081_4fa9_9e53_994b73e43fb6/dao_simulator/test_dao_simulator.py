import unittest
from dao_simulator.dao_simulator import evaluate_proposal

class TestDAOSimulator(unittest.TestCase):
    def test_performance_boost_stable(self):
        N = 3
        edges = [(0, 1), (1, 2)]
        node_performances = [100.0, 100.0, 100.0]
        node_dependencies = [[], [], []]
        proposal = {
            'type': 'boost',
            'node_id': 0,
            'percentage': 10.0
        }
        votes = [10, -5, 8]
        total_tokens = 100
        quorum_threshold = 0.1
        approval_threshold = 0.6
        influence_factor = 0.1
        critical_threshold = 50.0
        
        result = evaluate_proposal(
            N, edges, node_performances, node_dependencies,
            proposal, votes, total_tokens, quorum_threshold,
            approval_threshold, influence_factor, critical_threshold
        )
        self.assertTrue(result)

    def test_reconfigure_unstable(self):
        N = 4
        edges = [(0, 1), (1, 2), (2, 3)]
        node_performances = [100.0, 80.0, 60.0, 40.0]
        node_dependencies = [[1], [2], [3], []]
        proposal = {
            'type': 'reconfigure',
            'node1': 0,
            'node2': 3,
            'add_connection': True
        }
        votes = [20, -10, 15]
        total_tokens = 200
        quorum_threshold = 0.2
        approval_threshold = 0.5
        influence_factor = 0.2
        critical_threshold = 50.0
        
        result = evaluate_proposal(
            N, edges, node_performances, node_dependencies,
            proposal, votes, total_tokens, quorum_threshold,
            approval_threshold, influence_factor, critical_threshold
        )
        self.assertFalse(result)

    def test_dependency_update_quorum_fail(self):
        N = 2
        edges = [(0, 1)]
        node_performances = [100.0, 100.0]
        node_dependencies = [[1], []]
        proposal = {
            'type': 'dependency',
            'node_id': 0,
            'new_dependencies': []
        }
        votes = [5]
        total_tokens = 1000
        quorum_threshold = 0.3
        approval_threshold = 0.5
        influence_factor = 0.1
        critical_threshold = 80.0
        
        result = evaluate_proposal(
            N, edges, node_performances, node_dependencies,
            proposal, votes, total_tokens, quorum_threshold,
            approval_threshold, influence_factor, critical_threshold
        )
        self.assertFalse(result)

    def test_approval_threshold_fail(self):
        N = 3
        edges = [(0, 1), (1, 2)]
        node_performances = [100.0, 100.0, 100.0]
        node_dependencies = [[], [], []]
        proposal = {
            'type': 'boost',
            'node_id': 1,
            'percentage': 5.0
        }
        votes = [10, -20, 5]
        total_tokens = 100
        quorum_threshold = 0.1
        approval_threshold = 0.7
        influence_factor = 0.05
        critical_threshold = 90.0
        
        result = evaluate_proposal(
            N, edges, node_performances, node_dependencies,
            proposal, votes, total_tokens, quorum_threshold,
            approval_threshold, influence_factor, critical_threshold
        )
        self.assertFalse(result)

    def test_circular_dependencies(self):
        N = 3
        edges = [(0, 1), (1, 2)]
        node_performances = [100.0, 100.0, 100.0]
        node_dependencies = [[1], [2], [0]]
        proposal = {
            'type': 'boost',
            'node_id': 0,
            'percentage': 20.0
        }
        votes = [30, 10, 5]
        total_tokens = 100
        quorum_threshold = 0.2
        approval_threshold = 0.5
        influence_factor = 0.15
        critical_threshold = 80.0
        
        result = evaluate_proposal(
            N, edges, node_performances, node_dependencies,
            proposal, votes, total_tokens, quorum_threshold,
            approval_threshold, influence_factor, critical_threshold
        )
        self.assertTrue(result)

    def test_empty_votes(self):
        N = 2
        edges = [(0, 1)]
        node_performances = [100.0, 100.0]
        node_dependencies = [[], []]
        proposal = {
            'type': 'reconfigure',
            'node1': 0,
            'node2': 1,
            'add_connection': False
        }
        votes = []
        total_tokens = 100
        quorum_threshold = 0.1
        approval_threshold = 0.5
        influence_factor = 0.1
        critical_threshold = 90.0
        
        result = evaluate_proposal(
            N, edges, node_performances, node_dependencies,
            proposal, votes, total_tokens, quorum_threshold,
            approval_threshold, influence_factor, critical_threshold
        )
        self.assertFalse(result)

    def test_zero_performance_node(self):
        N = 3
        edges = [(0, 1), (1, 2)]
        node_performances = [0.0, 100.0, 100.0]
        node_dependencies = [[1], [2], []]
        proposal = {
            'type': 'boost',
            'node_id': 0,
            'percentage': 100.0
        }
        votes = [50, 30, 20]
        total_tokens = 100
        quorum_threshold = 0.5
        approval_threshold = 0.6
        influence_factor = 0.2
        critical_threshold = 10.0
        
        result = evaluate_proposal(
            N, edges, node_performances, node_dependencies,
            proposal, votes, total_tokens, quorum_threshold,
            approval_threshold, influence_factor, critical_threshold
        )
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()