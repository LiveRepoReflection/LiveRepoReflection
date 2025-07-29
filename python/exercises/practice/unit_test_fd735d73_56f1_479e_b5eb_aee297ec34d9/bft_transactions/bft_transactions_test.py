import unittest
import time

try:
    from bft_transactions import Participant, ByzantineCoordinator
except ImportError as e:
    raise ImportError("Missing required classes: Participant and ByzantineCoordinator") from e

# Dummy implementations for testing purposes.
# We assume that the candidate solution uses the following interface:
# - Each Participant instance has methods: prepare(), commit(), abort() and an attribute 'decision'
# - ByzantineCoordinator is initialized with a list of participants, a fault tolerance parameter f,
#   and optionally parameters for simulating faulty behavior (e.g., a list of faulty participant indices or a flag for coordinator faults).
# - ByzantineCoordinator has a method run_transaction() that initiates the consensus process.
# - After running the transaction, each honest participant's 'decision' attribute is set to either "commit" or "abort".
# - ByzantineCoordinator has an attribute 'final_decision' that holds the consensus decision.
#
# For the purpose of testing, we will provide concrete subclasses to simulate honest and faulty behavior.

class HonestParticipant(Participant):
    def __init__(self, identifier):
        self.id = identifier
        self.decision = None

    def prepare(self):
        # Always return that this participant is ready.
        return True

    def commit(self):
        self.decision = "commit"

    def abort(self):
        self.decision = "abort"

class FaultyParticipant(Participant):
    def __init__(self, identifier, behavior='lie'):
        self.id = identifier
        self.decision = None
        # behavior can be 'lie', 'no_response', or 'conflict'
        self.behavior = behavior

    def prepare(self):
        if self.behavior == 'lie':
            # Incorrectly signal not ready.
            return False
        elif self.behavior == 'no_response':
            # Simulate a crash by not responding.
            time.sleep(2)  # delay to simulate timeout; coordinator should handle this
            return None
        # default behavior returns true
        return True

    def commit(self):
        if self.behavior == 'conflict':
            # Send conflicting decision.
            self.decision = "abort"
        else:
            self.decision = "commit"

    def abort(self):
        self.decision = "abort"

class TestBFTTransactions(unittest.TestCase):
    def setUp(self):
        # This setup defines a common scenario function to create participant lists for tests.
        # We assume that f denotes the maximum number of faulty nodes tolerated and n > 3*f.
        self.n = 7
        self.f = 2

    def all_honest_scenario(self):
        # Create all honest participants.
        participants = [HonestParticipant(i) for i in range(self.n)]
        return participants

    def mixed_fault_scenario(self):
        # Create a mix of honest and faulty participants.
        participants = []
        # Mark participants with id 1 and 3 as faulty (simulate 'lie' behavior)
        faulty_ids = {1, 3}
        for i in range(self.n):
            if i in faulty_ids:
                participants.append(FaultyParticipant(i, behavior='lie'))
            else:
                participants.append(HonestParticipant(i))
        return participants, faulty_ids

    def coordinator_fault_scenario(self):
        # Create all honest participants but simulate that the coordinator itself is faulty.
        participants = [HonestParticipant(i) for i in range(self.n)]
        return participants

    def test_all_honest_commit(self):
        # Test that in a scenario with all honest participants, the consensus decision is "commit"
        participants = self.all_honest_scenario()
        # Instantiate ByzantineCoordinator without any fault injection.
        coordinator = ByzantineCoordinator(participants=participants, f=self.f, faulty_indices=[])
        coordinator.run_transaction()
        # Check that the final decision is either "commit" or "abort". In an all-honest scenario, we expect commit.
        self.assertEqual(coordinator.final_decision, "commit", "All honest participants should commit when all are ready.")
        # Check that every participant has the same decision.
        for p in participants:
            self.assertEqual(p.decision, coordinator.final_decision,
                             f"Participant {p.id} decision should match coordinator's decision.")

    def test_mixed_faults_consensus(self):
        # Test that when some participants are faulty, all honest participants reach the same consensus.
        participants, faulty_ids = self.mixed_fault_scenario()
        coordinator = ByzantineCoordinator(participants=participants, f=self.f, faulty_indices=list(faulty_ids))
        coordinator.run_transaction()
        # Retrieve honest participants based on our simulation.
        honest_decisions = [p.decision for p in participants if p.id not in faulty_ids]
        # It is essential that all honest participants agree on the same decision.
        self.assertTrue(len(set(honest_decisions)) == 1,
                        "All honest participants must agree on the same decision even with faulty nodes.")
        self.assertEqual(coordinator.final_decision, honest_decisions[0],
                         "Coordinator's final decision should match the decision of all honest participants.")

    def test_coordinator_fault_tolerance(self):
        # Test that the system still reaches consensus even if the coordinator behaves maliciously.
        # For this simulation, we assume the ByzantineCoordinator accepts a parameter to simulate a faulty coordinator.
        participants = self.coordinator_fault_scenario()
        # Here, we simulate coordinator fault by setting a flag (e.g., faulty_coordinator=True).
        # The candidate solution is expected to handle this and still enable honest participants to reach agreement.
        coordinator = ByzantineCoordinator(participants=participants, f=self.f, faulty_indices=[], faulty_coordinator=True)
        coordinator.run_transaction()
        # Check that all honest participants have the same decision.
        decisions = [p.decision for p in participants]
        self.assertTrue(len(set(decisions)) == 1,
                        "All honest participants must agree on the same decision even when the coordinator is faulty.")
        self.assertEqual(coordinator.final_decision, decisions[0],
                         "Faulty coordinator's reported decision should match the decision of all honest participants.")

if __name__ == '__main__':
    unittest.main()