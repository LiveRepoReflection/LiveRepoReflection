import unittest
import time

from dao_governance import DAO, Proposal, DelegationError

class TestDaoGovernance(unittest.TestCase):

    def setUp(self):
        # Initialize a DAO with sample members and a portfolio.
        # Each member is represented as a tuple: (member_id, token_balance)
        members = {
            "alice": 100,
            "bob": 50,
            "charlie": 75,
            "dave": 0  # Member with zero tokens.
        }
        # Portfolio: asset_name -> quantity
        portfolio = {
            "ETH": 500,
            "BTC": 100,
            "DAI": 10000
        }
        # The DAO constructor is expected to set up members, portfolio, proposals ledger and current time simulation.
        self.dao = DAO(members, portfolio, quorum=0.5, threshold=0.6, timelock=2)

    def test_initialize_dao(self):
        # Test that DAO is initialized correctly.
        self.assertEqual(len(self.dao.members), 4)
        self.assertIn("alice", self.dao.members)
        self.assertAlmostEqual(self.dao.portfolio["DAI"], 10000)
        self.assertEqual(len(self.dao.proposals), 0)

    def test_create_proposal(self):
        # Create a valid proposal to invest in a protocol
        params = {"asset": "DAI", "amount": 1000, "protocol": "ProtocolX"}
        description = "Invest 1000 DAI in ProtocolX"
        proposal = self.dao.create_proposal(description, params, deadline=time.time() + 60)
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.description, description)
        self.assertEqual(proposal.params, params)
        self.assertEqual(proposal.vote_results, {"for": 0, "against": 0, "abstain": 0})
        self.assertEqual(proposal.status, "pending")
        # Ensure the proposal is added to the DAO's ledger
        self.assertIn(proposal.id, self.dao.proposals)

    def test_voting_and_execution(self):
        # Create a proposal and simulate voting.
        params = {"asset": "ETH", "amount": 50, "protocol": "StakingPool"}
        proposal = self.dao.create_proposal("Stake 50 ETH", params, deadline=time.time() + 60)
        # Members vote. Use snapshot mechanism: token balance at proposal creation.
        # Alice (100 tokens) and Charlie (75 tokens) vote for.
        self.dao.vote(proposal.id, "alice", "for")
        self.dao.vote(proposal.id, "charlie", "for")
        # Bob (50 tokens) votes against.
        self.dao.vote(proposal.id, "bob", "against")
        # Dave has 0 tokens and abstains.
        self.dao.vote(proposal.id, "dave", "abstain")

        # Calculate expected voting power using snapshot values.
        expected_for = 100 + 75  # 175 tokens for.
        expected_against = 50    # 50 tokens against.
        expected_abstain = 0     # 0 tokens (Dave had none)

        self.assertEqual(proposal.vote_results["for"], expected_for)
        self.assertEqual(proposal.vote_results["against"], expected_against)
        self.assertEqual(proposal.vote_results["abstain"], expected_abstain)

        # Check that quorum is met: total tokens in snapshot = 100+50+75+0 = 225.
        # Voters participated: 100+75+50+0 = 225, so quorum of 100% is met.
        # Check threshold: for votes are 175/225 ~ 77.8% which exceeds 60% threshold.
        self.assertTrue(self.dao.is_quorum_met(proposal))
        self.assertTrue(self.dao.is_threshold_met(proposal))

        # Simulate time-lock delay
        # Initially the proposal cannot be executed because timelock period not elapsed.
        self.assertFalse(self.dao.can_execute(proposal))
        # Simulate waiting for timelock to expire.
        time.sleep(self.dao.timelock)
        self.assertTrue(self.dao.can_execute(proposal))

        # Execute proposal; execution should simulate asset transfer.
        pre_balance = self.dao.portfolio["ETH"]
        self.dao.execute_proposal(proposal.id)
        # For staking, assume the asset is deducted from portfolio.
        self.assertEqual(self.dao.proposals[proposal.id].status, "executed")
        self.assertEqual(self.dao.portfolio["ETH"], pre_balance - params["amount"])

    def test_snapshot_integrity(self):
        # Ensure that token snapshot remains unchanged even if member tokens are updated after proposal creation.
        params = {"asset": "BTC", "amount": 10, "protocol": "LiquidityPool"}
        proposal = self.dao.create_proposal("Invest 10 BTC in LiquidityPool", params, deadline=time.time() + 60)
        # Alice casts vote based on snapshot.
        self.dao.vote(proposal.id, "alice", "for")
        # Change Alice's balance in the main DAO after the vote.
        self.dao.members["alice"] = 10
        # Check that the proposal's snapshot still uses the original 100 tokens.
        self.assertEqual(proposal.snapshot["alice"], 100)

    def test_delegated_voting(self):
        # Test that delegated voting allows a member to cast vote on behalf of another.
        params = {"asset": "DAI", "amount": 500, "protocol": "YieldFarming"}
        proposal = self.dao.create_proposal("Deploy 500 DAI in YieldFarming", params, deadline=time.time() + 60)
        # Bob delegates his vote to Charlie.
        self.dao.delegate("bob", "charlie")
        # Charlie votes for the proposal.
        self.dao.vote(proposal.id, "charlie", "for")
        # The voting power should include both Charlie's and delegated Bob's tokens.
        # Charlie's tokens from snapshot: 75 and Bob's: 50.
        expected_for = 75 + 50
        self.assertEqual(proposal.vote_results["for"], expected_for)

    def test_reject_malicious_proposal(self):
        # Create a proposal with a suspicious description that should be flagged.
        params = {"asset": "DAI", "amount": 100000, "protocol": "UnknownProtocol"}
        proposal = self.dao.create_proposal("!!! MALICIOUS !!! Drain funds", params, deadline=time.time() + 60)
        # System should automatically flag malicious proposals.
        self.assertTrue(self.dao.is_malicious(proposal))
        # Even if votes are cast, the proposal should be rejected.
        self.dao.vote(proposal.id, "alice", "for")
        self.dao.vote(proposal.id, "charlie", "for")
        # Fast-forward time to meet timelock.
        time.sleep(self.dao.timelock)
        self.dao.execute_proposal(proposal.id)
        self.assertEqual(self.dao.proposals[proposal.id].status, "rejected")

    def test_sybil_attack_mitigation(self):
        # Simulate a scenario in which a malicious actor creates multiple fake accounts.
        # The quadratic voting scheme should limit the total influence.
        # Create several fake members with small token balances.
        sybil_members = {
            "sybil1": 1,
            "sybil2": 1,
            "sybil3": 1,
            "sybil4": 1,
            "sybil5": 1
        }
        for member, tokens in sybil_members.items():
            self.dao.members[member] = tokens
        # Create a proposal and have all sybil members vote "for".
        params = {"asset": "DAI", "amount": 200, "protocol": "SybilTest"}
        proposal = self.dao.create_proposal("Sybil vote test", params, deadline=time.time() + 60)
        for member in sybil_members.keys():
            self.dao.vote(proposal.id, member, "for")
        # If quadratic voting is applied, the effective voting power should be less than linear sum.
        effective_power = self.dao.get_effective_vote_weight(proposal, "for")
        self.assertLess(effective_power, sum(sybil_members.values()))
        # Also test that the proposal does not pass due solely to sybil votes.
        total_snapshot = sum(self.dao.snapshot_total(proposal))
        self.assertFalse(self.dao.is_threshold_met(proposal))

    def test_invalid_proposal_parameters(self):
        # Create a proposal with invalid parameters (e.g., negative asset amount).
        params = {"asset": "BTC", "amount": -20, "protocol": "InvalidProtocol"}
        with self.assertRaises(ValueError):
            self.dao.create_proposal("Invest -20 BTC", params, deadline=time.time() + 60)

    def test_concurrent_proposal_submission(self):
        # Test that two proposals can be submitted concurrently with unique IDs.
        params1 = {"asset": "ETH", "amount": 20, "protocol": "A"}
        params2 = {"asset": "ETH", "amount": 30, "protocol": "B"}
        proposal1 = self.dao.create_proposal("Invest 20 ETH in A", params1, deadline=time.time() + 60)
        proposal2 = self.dao.create_proposal("Invest 30 ETH in B", params2, deadline=time.time() + 60)
        self.assertNotEqual(proposal1.id, proposal2.id)
        self.assertIn(proposal1.id, self.dao.proposals)
        self.assertIn(proposal2.id, self.dao.proposals)

if __name__ == "__main__":
    unittest.main()