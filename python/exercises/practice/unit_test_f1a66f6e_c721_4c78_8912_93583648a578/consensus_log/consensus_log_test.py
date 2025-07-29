import unittest
from consensus_log import Node, LogEntry

class ConsensusLogTest(unittest.TestCase):
    def setUp(self):
        self.node0 = Node(0)
        self.node1 = Node(1)
        self.node2 = Node(2)

    def test_initial_state(self):
        self.assertEqual(self.node0.get_current_term(), 1)
        self.assertEqual(len(self.node0.get_log()), 0)

    def test_simple_append_entry(self):
        entry = LogEntry(1, 1, "SET x 5")
        self.assertTrue(self.node0.append_entry(entry))
        self.assertEqual(len(self.node0.get_log()), 1)
        self.assertEqual(self.node0.get_log()[0].command, "SET x 5")

    def test_append_entry_wrong_index(self):
        entry = LogEntry(1, 2, "SET x 5")  # Index should start at 1
        self.assertFalse(self.node0.append_entry(entry))

    def test_append_entry_wrong_term(self):
        self.node0.set_current_term(2)
        entry = LogEntry(1, 1, "SET x 5")  # Term less than current_term
        self.assertFalse(self.node0.append_entry(entry))

    def test_accept_proposal_basic(self):
        entry = LogEntry(1, 1, "SET x 5")
        self.assertTrue(self.node0.accept_proposal(1, 0, 0, entry))
        self.assertEqual(len(self.node0.get_log()), 1)

    def test_accept_proposal_term_update(self):
        self.node0.set_current_term(1)
        entry = LogEntry(2, 1, "SET x 5")
        self.assertTrue(self.node0.accept_proposal(2, 0, 0, entry))
        self.assertEqual(self.node0.get_current_term(), 2)

    def test_accept_proposal_invalid_prev_log(self):
        # Try to append entry 2 when entry 1 doesn't exist
        entry = LogEntry(1, 2, "SET x 5")
        self.assertFalse(self.node0.accept_proposal(1, 1, 1, entry))

    def test_accept_proposal_conflict_resolution(self):
        # First append entry with term 1
        entry1 = LogEntry(1, 1, "SET x 5")
        self.node0.append_entry(entry1)
        
        # Then propose conflicting entry with higher term
        entry2 = LogEntry(2, 1, "SET x 10")
        self.assertTrue(self.node0.accept_proposal(2, 0, 0, entry2))
        
        # Check that the new entry replaced the old one
        log = self.node0.get_log()
        self.assertEqual(len(log), 1)
        self.assertEqual(log[0].term, 2)
        self.assertEqual(log[0].command, "SET x 10")

    def test_accept_proposal_multiple_entries(self):
        entry1 = LogEntry(1, 1, "SET x 5")
        entry2 = LogEntry(1, 2, "SET y 10")
        
        self.assertTrue(self.node0.accept_proposal(1, 0, 0, entry1))
        self.assertTrue(self.node0.accept_proposal(1, 1, 1, entry2))
        
        log = self.node0.get_log()
        self.assertEqual(len(log), 2)
        self.assertEqual(log[0].command, "SET x 5")
        self.assertEqual(log[1].command, "SET y 10")

    def test_log_matching_property(self):
        # Append same entries to both nodes
        entry1 = LogEntry(1, 1, "SET x 5")
        entry2 = LogEntry(1, 2, "SET y 10")
        
        self.node0.accept_proposal(1, 0, 0, entry1)
        self.node1.accept_proposal(1, 0, 0, entry1)
        
        self.node0.accept_proposal(1, 1, 1, entry2)
        self.node1.accept_proposal(1, 1, 1, entry2)
        
        log0 = self.node0.get_log()
        log1 = self.node1.get_log()
        
        self.assertEqual(len(log0), len(log1))
        for i in range(len(log0)):
            self.assertEqual(log0[i].term, log1[i].term)
            self.assertEqual(log0[i].index, log1[i].index)
            self.assertEqual(log0[i].command, log1[i].command)

    def test_immutability_of_log_entries(self):
        entry = LogEntry(1, 1, "SET x 5")
        self.node0.append_entry(entry)
        
        # Attempt to modify the entry after it's in the log
        log = self.node0.get_log()
        with self.assertRaises(AttributeError):
            log[0].term = 2
        with self.assertRaises(AttributeError):
            log[0].index = 2
        with self.assertRaises(AttributeError):
            log[0].command = "SET x 10"

if __name__ == '__main__':
    unittest.main()