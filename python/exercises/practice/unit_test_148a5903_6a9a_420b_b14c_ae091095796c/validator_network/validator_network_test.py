import unittest
from validator_network import can_reach_quorum

class ValidatorNetworkTest(unittest.TestCase):
    def test_simple_network(self):
        network = [(0, 1), (1, 2), (2, 3)]
        def validation_function(transaction, validator_id):
            return True
        self.assertTrue(can_reach_quorum(
            network=network,
            transaction="test_transaction",
            source_validator=0,
            quorum_size=3,
            max_hops=2,
            byzantine_tolerance=0,
            validation_function=validation_function
        ))

    def test_disconnected_network(self):
        network = [(0, 1), (2, 3)]
        def validation_function(transaction, validator_id):
            return True
        self.assertFalse(can_reach_quorum(
            network=network,
            transaction="test_transaction",
            source_validator=0,
            quorum_size=3,
            max_hops=2,
            byzantine_tolerance=0,
            validation_function=validation_function
        ))

    def test_byzantine_failures(self):
        network = [(0, 1), (0, 2), (0, 3), (1, 4), (2, 4), (3, 4)]
        def validation_function(transaction, validator_id):
            return validator_id != 1  # Validator 1 is Byzantine
        self.assertTrue(can_reach_quorum(
            network=network,
            transaction="test_transaction",
            source_validator=0,
            quorum_size=3,
            max_hops=2,
            byzantine_tolerance=1,
            validation_function=validation_function
        ))

    def test_max_hops_limit(self):
        network = [(0, 1), (1, 2), (2, 3)]
        def validation_function(transaction, validator_id):
            return True
        self.assertFalse(can_reach_quorum(
            network=network,
            transaction="test_transaction",
            source_validator=0,
            quorum_size=4,
            max_hops=1,
            byzantine_tolerance=0,
            validation_function=validation_function
        ))

    def test_empty_network(self):
        network = []
        def validation_function(transaction, validator_id):
            return True
        self.assertFalse(can_reach_quorum(
            network=network,
            transaction="test_transaction",
            source_validator=0,
            quorum_size=2,
            max_hops=1,
            byzantine_tolerance=0,
            validation_function=validation_function
        ))

    def test_self_loops(self):
        network = [(0, 0), (0, 1), (1, 1)]
        def validation_function(transaction, validator_id):
            return True
        self.assertTrue(can_reach_quorum(
            network=network,
            transaction="test_transaction",
            source_validator=0,
            quorum_size=2,
            max_hops=1,
            byzantine_tolerance=0,
            validation_function=validation_function
        ))

    def test_large_network(self):
        # Create a large network with 1000 nodes
        network = [(i, i+1) for i in range(999)]
        def validation_function(transaction, validator_id):
            return True
        self.assertFalse(can_reach_quorum(
            network=network,
            transaction="test_transaction",
            source_validator=0,
            quorum_size=1000,
            max_hops=5,
            byzantine_tolerance=0,
            validation_function=validation_function
        ))

    def test_all_byzantine(self):
        network = [(0, 1), (0, 2), (0, 3)]
        def validation_function(transaction, validator_id):
            return False  # All validators return False
        self.assertFalse(can_reach_quorum(
            network=network,
            transaction="test_transaction",
            source_validator=0,
            quorum_size=2,
            max_hops=1,
            byzantine_tolerance=1,
            validation_function=validation_function
        ))

    def test_cyclic_network(self):
        network = [(0, 1), (1, 2), (2, 0)]
        def validation_function(transaction, validator_id):
            return True
        self.assertTrue(can_reach_quorum(
            network=network,
            transaction="test_transaction",
            source_validator=0,
            quorum_size=3,
            max_hops=2,
            byzantine_tolerance=0,
            validation_function=validation_function
        ))

    def test_invalid_source(self):
        network = [(0, 1), (1, 2)]
        def validation_function(transaction, validator_id):
            return True
        self.assertFalse(can_reach_quorum(
            network=network,
            transaction="test_transaction",
            source_validator=3,  # Invalid source validator
            quorum_size=2,
            max_hops=1,
            byzantine_tolerance=0,
            validation_function=validation_function
        ))

if __name__ == '__main__':
    unittest.main()