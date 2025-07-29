import unittest
from dao_rollback.dao import (
    create_account,
    create_proposal,
    vote_on_proposal,
    create_block,
    approve_block,
    process_block,
    rollback_block
)

class TestDAORollback(unittest.TestCase):
    def setUp(self):
        self.dao_state = {"accounts": {}, "blocks": {}}
        create_account(self.dao_state, 1, 100)
        create_account(self.dao_state, 2, 50)
        create_account(self.dao_state, 3, 200)

    def test_create_account(self):
        self.assertTrue(create_account(self.dao_state, 4, 75))
        self.assertFalse(create_account(self.dao_state, 1, 50))  # Duplicate ID
        self.assertEqual(self.dao_state["accounts"][4]["balance"], 75)

    def test_create_proposal(self):
        proposal = create_proposal(self.dao_state, 1, 2, 20)
        self.assertEqual(proposal["proposer_id"], 1)
        self.assertEqual(proposal["recipient_id"], 2)
        self.assertEqual(proposal["amount"], 20)
        self.assertEqual(len(proposal["votes"]), 0)

    def test_vote_on_proposal(self):
        proposal = create_proposal(self.dao_state, 1, 2, 20)
        vote_on_proposal(proposal, 1)
        vote_on_proposal(proposal, 2)
        self.assertEqual(len(proposal["votes"]), 2)
        self.assertIn(1, proposal["votes"])
        self.assertIn(2, proposal["votes"])

    def test_create_block(self):
        proposal = create_proposal(self.dao_state, 1, 2, 20)
        block = create_block(self.dao_state, 1, [proposal])
        self.assertEqual(block["block_id"], 1)
        self.assertEqual(len(block["proposals"]), 1)
        self.assertEqual(len(block["approvals"]), 0)
        self.assertFalse(create_block(self.dao_state, 1, []))  # Duplicate block ID

    def test_approve_block(self):
        proposal = create_proposal(self.dao_state, 1, 2, 20)
        block = create_block(self.dao_state, 1, [proposal])
        approve_block(block, 1)
        approve_block(block, 2)
        self.assertEqual(len(block["approvals"]), 2)
        self.assertIn(1, block["approvals"])
        self.assertIn(2, block["approvals"])

    def test_process_block_success(self):
        proposal = create_proposal(self.dao_state, 1, 2, 20)
        vote_on_proposal(proposal, 1)
        vote_on_proposal(proposal, 2)
        vote_on_proposal(proposal, 3)
        block = create_block(self.dao_state, 1, [proposal])
        approve_block(block, 1)
        approve_block(block, 2)
        self.assertTrue(process_block(self.dao_state, block))
        self.assertEqual(self.dao_state["accounts"][1]["balance"], 80)
        self.assertEqual(self.dao_state["accounts"][2]["balance"], 70)

    def test_process_block_insufficient_funds(self):
        proposal = create_proposal(self.dao_state, 1, 2, 200)
        vote_on_proposal(proposal, 1)
        vote_on_proposal(proposal, 2)
        block = create_block(self.dao_state, 1, [proposal])
        self.assertFalse(process_block(self.dao_state, block))
        self.assertEqual(self.dao_state["accounts"][1]["balance"], 100)

    def test_process_block_invalid_account(self):
        proposal = create_proposal(self.dao_state, 1, 99, 20)
        vote_on_proposal(proposal, 1)
        vote_on_proposal(proposal, 2)
        block = create_block(self.dao_state, 1, [proposal])
        self.assertFalse(process_block(self.dao_state, block))
        self.assertEqual(self.dao_state["accounts"][1]["balance"], 100)

    def test_rollback_block(self):
        proposal = create_proposal(self.dao_state, 1, 2, 20)
        vote_on_proposal(proposal, 1)
        vote_on_proposal(proposal, 2)
        block = create_block(self.dao_state, 1, [proposal])
        approve_block(block, 1)
        approve_block(block, 2)
        process_block(self.dao_state, block)
        self.assertTrue(rollback_block(self.dao_state, 1))
        self.assertEqual(self.dao_state["accounts"][1]["balance"], 100)
        self.assertEqual(self.dao_state["accounts"][2]["balance"], 50)
        self.assertNotIn(1, self.dao_state["blocks"])

    def test_rollback_nonexistent_block(self):
        self.assertFalse(rollback_block(self.dao_state, 99))

    def test_multiple_blocks_rollback(self):
        # First block
        proposal1 = create_proposal(self.dao_state, 1, 2, 20)
        vote_on_proposal(proposal1, 1)
        vote_on_proposal(proposal1, 2)
        block1 = create_block(self.dao_state, 1, [proposal1])
        approve_block(block1, 1)
        approve_block(block1, 2)
        process_block(self.dao_state, block1)

        # Second block
        proposal2 = create_proposal(self.dao_state, 2, 3, 30)
        vote_on_proposal(proposal2, 1)
        vote_on_proposal(proposal2, 2)
        block2 = create_block(self.dao_state, 2, [proposal2])
        approve_block(block2, 1)
        approve_block(block2, 2)
        process_block(self.dao_state, block2)

        # Rollback second block
        self.assertTrue(rollback_block(self.dao_state, 2))
        self.assertEqual(self.dao_state["accounts"][2]["balance"], 70)  # From block1
        self.assertEqual(self.dao_state["accounts"][3]["balance"], 200)  # Original
        self.assertIn(1, self.dao_state["blocks"])
        self.assertNotIn(2, self.dao_state["blocks"])

if __name__ == "__main__":
    unittest.main()