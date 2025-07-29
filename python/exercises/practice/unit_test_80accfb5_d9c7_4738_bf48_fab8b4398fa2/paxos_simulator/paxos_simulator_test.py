import unittest
from paxos_simulator import simulate_paxos

class PaxosSimulatorTest(unittest.TestCase):
    def test_basic_consensus(self):
        # Basic test with one proposal and perfect network (no message loss or failures)
        # Expect the consensus value to be the only proposed value.
        consensus = simulate_paxos(
            n=3,
            proposals=[(0, "value1")],
            message_loss_probability=0.0,
            failure_rate=0.0,
            recovery_rate=1.0,
            max_steps=100
        )
        self.assertEqual(consensus, "value1")

    def test_multiple_proposals_deterministic(self):
        # Deterministic test with multiple proposals, no message loss/failure.
        # The consensus value should be one of the proposed values.
        consensus = simulate_paxos(
            n=5,
            proposals=[(0, "value1"), (1, "value2"), (2, "value3")],
            message_loss_probability=0.0,
            failure_rate=0.0,
            recovery_rate=1.0,
            max_steps=200
        )
        self.assertIn(consensus, {"value1", "value2", "value3"})
    
    def test_message_loss_and_failures(self):
        # Scenario with moderate message loss and node failures with possibility of recovery.
        # Depending on randomness, consensus might be reached or not.
        consensus = simulate_paxos(
            n=5,
            proposals=[(0, "alpha"), (2, "beta")],
            message_loss_probability=0.1,
            failure_rate=0.1,
            recovery_rate=0.5,
            max_steps=300
        )
        if consensus != "No Consensus":
            self.assertIn(consensus, {"alpha", "beta"})
        else:
            self.assertEqual(consensus, "No Consensus")

    def test_max_steps_no_consensus(self):
        # Set max_steps too small to allow any consensus.
        consensus = simulate_paxos(
            n=5,
            proposals=[(0, "x"), (1, "y")],
            message_loss_probability=0.2,
            failure_rate=0.2,
            recovery_rate=0.2,
            max_steps=1
        )
        self.assertEqual(consensus, "No Consensus")
    
    def test_all_nodes_fail(self):
        # Simulate scenario with high failure probability and no recovery,
        # making it impossible to reach consensus.
        consensus = simulate_paxos(
            n=3,
            proposals=[(0, "one"), (1, "two")],
            message_loss_probability=0.0,
            failure_rate=0.9,
            recovery_rate=0.0,
            max_steps=50
        )
        self.assertEqual(consensus, "No Consensus")
    
    def test_large_cluster(self):
        # Test with a larger cluster and multiple proposals under realistic network conditions.
        consensus = simulate_paxos(
            n=7,
            proposals=[(0, "red"), (1, "blue"), (3, "green")],
            message_loss_probability=0.05,
            failure_rate=0.05,
            recovery_rate=0.5,
            max_steps=500
        )
        if consensus != "No Consensus":
            self.assertIn(consensus, {"red", "blue", "green"})
        else:
            self.assertEqual(consensus, "No Consensus")

if __name__ == '__main__':
    unittest.main()