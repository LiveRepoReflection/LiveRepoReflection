import unittest
import threading
import time
from dao_reputation import DAOReputationSystem

class TestDAOReputationSystem(unittest.TestCase):
    def setUp(self):
        self.rep_system = DAOReputationSystem(base_reputation=10)
        self.member1 = "0x1"
        self.member2 = "0x2"
        self.member3 = "0x3"

    def test_initial_reputation(self):
        self.assertEqual(self.rep_system.get_reputation(self.member1), 10)
        self.assertEqual(self.rep_system.get_reputation(self.member2), 10)

    def test_direct_reputation_update(self):
        self.rep_system.update_reputation(self.member1, 5)
        self.assertEqual(self.rep_system.get_reputation(self.member1), 15)
        self.rep_system.update_reputation(self.member1, -3)
        self.assertEqual(self.rep_system.get_reputation(self.member1), 12)

    def test_proposal_success(self):
        self.rep_system.handle_proposal_success(
            proposer_id=self.member1,
            project_impact=1000,
            co_proposers=2
        )
        self.assertGreater(self.rep_system.get_reputation(self.member1), 10)

    def test_voting_accuracy(self):
        # Test voting with successful project
        initial_rep = self.rep_system.get_reputation(self.member1)
        self.rep_system.handle_vote(
            member_id=self.member1,
            proposal_id="p1",
            vote=True,
            project_success=True,
            voting_margin=0.1
        )
        self.assertGreater(self.rep_system.get_reputation(self.member1), initial_rep)

        # Test voting against successful project
        initial_rep = self.rep_system.get_reputation(self.member2)
        self.rep_system.handle_vote(
            member_id=self.member2,
            proposal_id="p1",
            vote=False,
            project_success=True,
            voting_margin=0.1
        )
        self.assertLess(self.rep_system.get_reputation(self.member2), initial_rep)

    def test_staking(self):
        initial_rep = self.rep_system.get_reputation(self.member1)
        self.rep_system.handle_staking(self.member1, 1000)
        self.assertGreater(self.rep_system.get_reputation(self.member1), initial_rep)

    def test_reporting(self):
        # Test valid report
        reporter_initial = self.rep_system.get_reputation(self.member1)
        reported_initial = self.rep_system.get_reputation(self.member2)
        self.rep_system.handle_report(
            reporter_id=self.member1,
            reported_id=self.member2,
            is_valid=True
        )
        self.assertGreater(self.rep_system.get_reputation(self.member1), reporter_initial)
        self.assertLess(self.rep_system.get_reputation(self.member2), reported_initial)

        # Test invalid report
        reporter_initial = self.rep_system.get_reputation(self.member3)
        self.rep_system.handle_report(
            reporter_id=self.member3,
            reported_id=self.member1,
            is_valid=False
        )
        self.assertLess(self.rep_system.get_reputation(self.member3), reporter_initial)

    def test_time_decay(self):
        self.rep_system.update_reputation(self.member1, 50)
        initial_rep = self.rep_system.get_reputation(self.member1)
        self.rep_system.apply_time_decay()
        self.assertLess(self.rep_system.get_reputation(self.member1), initial_rep)

    def test_concurrent_updates(self):
        def update_rep(member_id, amount):
            for _ in range(100):
                self.rep_system.update_reputation(member_id, amount)

        threads = [
            threading.Thread(target=update_rep, args=(self.member1, 1)),
            threading.Thread(target=update_rep, args=(self.member1, -1)),
            threading.Thread(target=update_rep, args=(self.member2, 2))
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(self.rep_system.get_reputation(self.member1), 10)
        self.assertEqual(self.rep_system.get_reputation(self.member2), 210)

    def test_reputation_bounds(self):
        self.rep_system.update_reputation(self.member1, 10000)
        self.assertEqual(self.rep_system.get_reputation(self.member1), 1000)
        self.rep_system.update_reputation(self.member2, -100)
        self.assertEqual(self.rep_system.get_reputation(self.member2), 0)

if __name__ == '__main__':
    unittest.main()